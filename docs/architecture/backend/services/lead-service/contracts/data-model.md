# Data Model — LEAD (`emp_<slug>`, schema-per-tenant)

> LEAD owns the **lead** aggregate and satellites in each operational schema `emp_<slug>`. These
> tables are authored here and extracted by `scripts/be-migration-generator.py` into
> `db/migration/empresa/` (centralized Flyway in `journey-os-migrations`, applied to every tenant
> schema). LEAD runs `ddl-auto=validate` and `open-in-view=false` (RULE-08).
>
> Identifiers are **pt-BR snake_case**, matching the canonical model. Tables are **unqualified**:
> the schema is the per-tenant `emp_<slug>` resolved at runtime (`EmpresaContextHolder`); the same
> DDL is replicated to each tenant schema. `gen_random_uuid()` relies on `pgcrypto`, provided
> globally by MIG.

## 1. Conventions

- **PK strategy:** `UUID` (`gen_random_uuid()`) for all entities.
- **Timestamps:** `criado_em TIMESTAMPTZ NOT NULL DEFAULT now()`, `atualizado_em TIMESTAMPTZ`.
- **Soft-delete / lifecycle:** leads use `estado_qualificacao` (no physical delete except LGPD purge); config aggregates use `ativo BOOLEAN`.
- **Naming:** `snake_case`, pt-BR. JSONB for flexible breakdown/predicate payloads.
- **PII:** `lead`/`perfil_lead`/`atributo_perfil` hold PII; `base_legal` mandatory; anonymization clears PII columns, keeps aggregate rows.
- **Dimensions (6D):** `PERFIL`, `ENGAJAMENTO`, `INTENCAO`, `CAPACIDADE`, `URGENCIA`, `ADERENCIA` (enforced by CHECK; see SPEC-03).

## 2. Schema-level mapping

| Tables | Schema |
|---|---|
| lead, perfil_lead, atributo_perfil, survey, pergunta, resposta_survey, regra_qualificacao, condicao_regra, maturity_score, score_dimensao, segmento, lead_segmento | `empresa` (`emp_<slug>`) |

## 3. Entities

### 3.1 `lead` [empresa]

Aggregate root. One lead per empresa per `chave_natural` (normalized email/phone + source).
`estado_qualificacao` is driven exclusively by score computation (SPEC-03). `base_legal` is the
LGPD legal basis captured at ingestion.

```sql
-- schema: empresa
CREATE TABLE lead (
    lead_id              UUID NOT NULL DEFAULT gen_random_uuid(),
    chave_natural        VARCHAR(255) NOT NULL,
    nome                 VARCHAR(200),
    email                VARCHAR(255),
    telefone             VARCHAR(40),
    fonte                VARCHAR(60) NOT NULL,
    estado_qualificacao  VARCHAR(20) NOT NULL DEFAULT 'NOVO',
    base_legal           VARCHAR(40) NOT NULL,
    consentimento_em     TIMESTAMPTZ,
    criado_em            TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em        TIMESTAMPTZ,
    PRIMARY KEY (lead_id),
    UNIQUE (chave_natural),
    CHECK (estado_qualificacao IN ('NOVO','EM_QUALIFICACAO','QUALIFICADO','NAO_QUALIFICADO','DESCARTADO','ANONIMIZADO')),
    CHECK (base_legal IN ('CONSENTIMENTO','LEGITIMO_INTERESSE','EXECUCAO_CONTRATO','OBRIGACAO_LEGAL'))
);
CREATE INDEX idx_lead_estado ON lead (estado_qualificacao);
CREATE INDEX idx_lead_fonte ON lead (fonte);
COMMENT ON TABLE lead IS 'Lead aggregate root; unique per empresa by chave_natural (dedup)';
COMMENT ON COLUMN lead.chave_natural IS 'Normalized dedup key: lower(email) and/or digits(telefone) + fonte';
```

**Invariants:** `chave_natural` unique per schema (dedup); `base_legal` required before qualification; `ANONIMIZADO` is terminal and clears PII columns.

### 3.2 `perfil_lead` [empresa]

1–1 consolidated profile snapshot for fast reads/segmentation.

```sql
-- schema: empresa
CREATE TABLE perfil_lead (
    lead_id        UUID NOT NULL,
    cargo          VARCHAR(120),
    segmento_mercado VARCHAR(120),
    faturamento_faixa VARCHAR(40),
    tamanho_equipe VARCHAR(40),
    canais         JSONB NOT NULL DEFAULT '{}'::jsonb,
    consolidado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (lead_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE
);
COMMENT ON TABLE perfil_lead IS 'Denormalized profile snapshot derived from atributo_perfil';
```

**Invariants:** exactly one row per lead; rebuilt from `atributo_perfil` on profile change.

### 3.3 `atributo_perfil` [empresa]

Typed attribute with provenance; the source of truth for the profile.

```sql
-- schema: empresa
CREATE TABLE atributo_perfil (
    atributo_id   UUID NOT NULL DEFAULT gen_random_uuid(),
    lead_id       UUID NOT NULL,
    chave         VARCHAR(80) NOT NULL,
    valor         TEXT,
    tipo          VARCHAR(20) NOT NULL DEFAULT 'TEXTO',
    origem        VARCHAR(20) NOT NULL,
    registrado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (atributo_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE,
    CHECK (tipo IN ('TEXTO','NUMERO','BOOLEANO','DATA','ENUM')),
    CHECK (origem IN ('FORM','SURVEY','INTEGRACAO','ASSIST_IA','MANUAL'))
);
CREATE INDEX idx_atributo_lead ON atributo_perfil (lead_id);
CREATE UNIQUE INDEX uq_atributo_lead_chave ON atributo_perfil (lead_id, chave);
```

**Invariants:** one current value per (lead, chave); `origem='ASSIST_IA'` marks AI-suggested attributes (SPEC-03 INV).

### 3.4 `survey` [empresa]

Versioned questionnaire whose answers feed the profile.

```sql
-- schema: empresa
CREATE TABLE survey (
    survey_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    nome       VARCHAR(150) NOT NULL,
    versao     INT NOT NULL DEFAULT 1,
    ativo      BOOLEAN NOT NULL DEFAULT true,
    criado_em  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (survey_id),
    UNIQUE (nome, versao)
);
```

### 3.5 `pergunta` [empresa]

Question belonging to a survey; maps to a target dimension.

```sql
-- schema: empresa
CREATE TABLE pergunta (
    pergunta_id   UUID NOT NULL DEFAULT gen_random_uuid(),
    survey_id     UUID NOT NULL,
    ordem         SMALLINT NOT NULL DEFAULT 0,
    enunciado     TEXT NOT NULL,
    tipo          VARCHAR(20) NOT NULL DEFAULT 'TEXTO',
    dimensao_alvo VARCHAR(20),
    PRIMARY KEY (pergunta_id),
    FOREIGN KEY (survey_id) REFERENCES survey (survey_id) ON DELETE CASCADE,
    CHECK (tipo IN ('TEXTO','NUMERO','BOOLEANO','ESCOLHA','ESCALA')),
    CHECK (dimensao_alvo IS NULL OR dimensao_alvo IN ('PERFIL','ENGAJAMENTO','INTENCAO','CAPACIDADE','URGENCIA','ADERENCIA'))
);
CREATE INDEX idx_pergunta_survey ON pergunta (survey_id);
```

### 3.6 `resposta_survey` [empresa]

A lead's answer to a question; updates `atributo_perfil` and triggers score recompute.

```sql
-- schema: empresa
CREATE TABLE resposta_survey (
    resposta_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    lead_id      UUID NOT NULL,
    pergunta_id  UUID NOT NULL,
    valor        TEXT,
    respondido_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (resposta_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES pergunta (pergunta_id),
    UNIQUE (lead_id, pergunta_id)
);
CREATE INDEX idx_resposta_lead ON resposta_survey (lead_id);
```

**Invariants:** one answer per (lead, pergunta) — re-answering overwrites.

### 3.7 `regra_qualificacao` [empresa]

Versioned rule set. Every score references the rule version that produced it (auditability).

```sql
-- schema: empresa
CREATE TABLE regra_qualificacao (
    regra_id    UUID NOT NULL DEFAULT gen_random_uuid(),
    versao      INT NOT NULL,
    nome        VARCHAR(150) NOT NULL,
    ativo       BOOLEAN NOT NULL DEFAULT false,
    limiar_qualificado SMALLINT NOT NULL DEFAULT 60,
    vigente_de  TIMESTAMPTZ,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (regra_id),
    UNIQUE (versao),
    CHECK (limiar_qualificado BETWEEN 0 AND 100)
);
CREATE UNIQUE INDEX uq_regra_ativa ON regra_qualificacao (ativo) WHERE ativo = true;
COMMENT ON TABLE regra_qualificacao IS 'Versioned qualification rule set; exactly one active at a time';
```

**Invariants:** at most one `ativo=true` row (partial unique index); `versao` strictly increasing; `limiar_qualificado` ∈ [0,100].

### 3.8 `condicao_regra` [empresa]

A single condition: maps a signal to a weighted contribution on a dimension.

```sql
-- schema: empresa
CREATE TABLE condicao_regra (
    condicao_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    regra_id     UUID NOT NULL,
    sinal        VARCHAR(80) NOT NULL,
    operador     VARCHAR(10) NOT NULL,
    valor_ref    TEXT,
    dimensao     VARCHAR(20) NOT NULL,
    peso         SMALLINT NOT NULL,
    PRIMARY KEY (condicao_id),
    FOREIGN KEY (regra_id) REFERENCES regra_qualificacao (regra_id) ON DELETE CASCADE,
    CHECK (operador IN ('EQ','NEQ','GT','GTE','LT','LTE','IN','EXISTS')),
    CHECK (dimensao IN ('PERFIL','ENGAJAMENTO','INTENCAO','CAPACIDADE','URGENCIA','ADERENCIA')),
    CHECK (peso BETWEEN -100 AND 100)
);
CREATE INDEX idx_condicao_regra ON condicao_regra (regra_id);
```

### 3.9 `maturity_score` [empresa]

Latest computed score for a lead; idempotency key = (`lead_id`,`versao_regra`,`hash_sinais`).

```sql
-- schema: empresa
CREATE TABLE maturity_score (
    maturity_score_id UUID NOT NULL DEFAULT gen_random_uuid(),
    lead_id        UUID NOT NULL,
    valor_agregado SMALLINT NOT NULL,
    versao_regra   INT NOT NULL,
    hash_sinais    VARCHAR(64) NOT NULL,
    assist_ia      BOOLEAN NOT NULL DEFAULT false,
    calculado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (maturity_score_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE,
    UNIQUE (lead_id),
    CHECK (valor_agregado BETWEEN 0 AND 100)
);
CREATE INDEX idx_score_versao ON maturity_score (versao_regra);
COMMENT ON COLUMN maturity_score.hash_sinais IS 'Hash of the signal set used; with lead_id+versao_regra forms the idempotency key (SPEC-05)';
```

**Invariants:** one current score per lead; `valor_agregado` ∈ [0,100]; `versao_regra` references an existing `regra_qualificacao.versao`.

### 3.10 `score_dimensao` [empresa]

Per-dimension breakdown (explainability). `contribuintes` lists the conditions that fired.

```sql
-- schema: empresa
CREATE TABLE score_dimensao (
    maturity_score_id UUID NOT NULL,
    dimensao      VARCHAR(20) NOT NULL,
    valor         SMALLINT NOT NULL,
    contribuintes JSONB NOT NULL DEFAULT '[]'::jsonb,
    PRIMARY KEY (maturity_score_id, dimensao),
    FOREIGN KEY (maturity_score_id) REFERENCES maturity_score (maturity_score_id) ON DELETE CASCADE,
    CHECK (dimensao IN ('PERFIL','ENGAJAMENTO','INTENCAO','CAPACIDADE','URGENCIA','ADERENCIA')),
    CHECK (valor BETWEEN 0 AND 100)
);
```

**Invariants:** up to 6 rows per score (one per dimension); the aggregate is a function of these (SPEC-03).

### 3.11 `segmento` [empresa]

Dynamic group defined by a predicate over profile + score.

```sql
-- schema: empresa
CREATE TABLE segmento (
    segmento_id UUID NOT NULL DEFAULT gen_random_uuid(),
    nome        VARCHAR(120) NOT NULL,
    predicado   JSONB NOT NULL DEFAULT '{}'::jsonb,
    ativo       BOOLEAN NOT NULL DEFAULT true,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (segmento_id),
    UNIQUE (nome)
);
COMMENT ON COLUMN segmento.predicado IS 'JSON predicate over perfil+score evaluated by SegmentEvaluator';
```

### 3.12 `lead_segmento` [empresa]

Materialized lead↔segment membership.

```sql
-- schema: empresa
CREATE TABLE lead_segmento (
    lead_id     UUID NOT NULL,
    segmento_id UUID NOT NULL,
    entrou_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (lead_id, segmento_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE,
    FOREIGN KEY (segmento_id) REFERENCES segmento (segmento_id) ON DELETE CASCADE
);
CREATE INDEX idx_lead_segmento_seg ON lead_segmento (segmento_id);
```

**Invariants:** membership reflects the predicate at last evaluation; entering/leaving emits `journey-os.lead.segmento.alterado`.

## 4. Relations (ASCII)

```
lead 1───1 perfil_lead
lead 1───N atributo_perfil
lead 1───N resposta_survey N───1 pergunta N───1 survey
lead 1───1 maturity_score 1───N score_dimensao
lead N───N segmento  (lead_segmento)
regra_qualificacao 1───N condicao_regra
maturity_score.versao_regra ──▶ regra_qualificacao.versao  (logical ref)
```

## 5. Migration plan

| Range | Theme |
|---|---|
| `V<N>__lead_core.sql` | lead, perfil_lead, atributo_perfil |
| `V<N>__lead_surveys.sql` | survey, pergunta, resposta_survey |
| `V<N>__lead_qualification.sql` | regra_qualificacao, condicao_regra |
| `V<N>__lead_score.sql` | maturity_score, score_dimensao |
| `V<N>__lead_segments.sql` | segmento, lead_segmento |

> All blocks are `-- schema: empresa` → routed to `db/migration/empresa/` and applied to every
> tenant schema. Default `regra_qualificacao` and `segmento` seeds are created per tenant on
> `journey-os.empresa.provisionada` consume (not via a global data migration). `V<N>` ranges are
> assigned by `journey-os-migrations` to avoid collisions across modules.
