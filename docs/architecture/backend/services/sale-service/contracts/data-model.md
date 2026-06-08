# Data Model — SALE (`emp_<slug>`, schema-per-tenant)

> SALE owns the **sales pipeline (CRM)**, **offers**, **purchases/revenue**, **attribution** and
> **LTV** in each operational schema `emp_<slug>`. These tables are authored here and extracted by
> `scripts/be-migration-generator.py` into `db/migration/empresa/` (centralized Flyway in
> `journey-os-migrations`, applied to every tenant schema). SALE runs `ddl-auto=validate` and
> `open-in-view=false` (RULE-08).
>
> Identifiers are **pt-BR snake_case**, matching the canonical model. Tables are **unqualified**:
> the schema is the per-tenant `emp_<slug>` resolved at runtime (`EmpresaContextHolder`); the same
> DDL is replicated to each tenant schema. `gen_random_uuid()` relies on `pgcrypto`, provided
> globally by MIG.

## 1. Conventions

- **PK strategy:** `UUID` (`gen_random_uuid()`) for all entities except `ltv` (keyed by `contato_ref`).
- **Timestamps:** `criado_em TIMESTAMPTZ NOT NULL DEFAULT now()`, `atualizado_em TIMESTAMPTZ`.
- **Money:** `NUMERIC(15,2)` + a `moeda CHAR(3)` (ISO-4217, default `'BRL'`). Never `float`.
- **Lifecycle:** `oportunidade.estado` and `compra.status` are state machines (no physical delete except LGPD purge); config aggregates (`oferta`, `modelo_atribuicao`, `campanha`) use `ativo BOOLEAN`.
- **Naming:** `snake_case`, pt-BR. JSONB only where flexibility is required.
- **PII:** `compra` holds buyer PII (`nome_comprador`, `email_comprador`); `base_legal` mandatory; anonymization clears PII columns but keeps revenue/aggregate rows.
- **Idempotency:** `compra` is unique per `(id_externo, origem)` — revenue is never double-counted (SPEC-05).

## 2. Schema-level mapping

| Tables | Schema |
|---|---|
| oportunidade, historico_estagio, oferta, compra, item_compra, modelo_atribuicao, atribuicao, campanha, ltv | `empresa` (`emp_<slug>`) |

## 3. Entities

### 3.1 `oportunidade` [empresa]

Aggregate root of the CRM pipeline. A deal linked to a lead, moving through configurable stages
until won/lost. `estado` is terminal on `GANHA`/`PERDIDA` (save explicit reopen, SPEC-02).

```sql
-- schema: empresa
CREATE TABLE oportunidade (
    oportunidade_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    lead_id          UUID,
    estagio          VARCHAR(40) NOT NULL DEFAULT 'NOVA',
    valor_estimado   NUMERIC(15,2) NOT NULL DEFAULT 0,
    moeda            CHAR(3) NOT NULL DEFAULT 'BRL',
    probabilidade    SMALLINT NOT NULL DEFAULT 0,
    responsavel_id   UUID,
    estado           VARCHAR(20) NOT NULL DEFAULT 'NOVA',
    motivo_perda     VARCHAR(120),
    criado_em        TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em    TIMESTAMPTZ,
    PRIMARY KEY (oportunidade_id),
    CHECK (estado IN ('NOVA','EM_ANDAMENTO','GANHA','PERDIDA','DESCARTADA')),
    CHECK (probabilidade BETWEEN 0 AND 100),
    CHECK (valor_estimado >= 0)
);
CREATE INDEX idx_oportunidade_estagio ON oportunidade (estagio);
CREATE INDEX idx_oportunidade_responsavel ON oportunidade (responsavel_id);
CREATE INDEX idx_oportunidade_lead ON oportunidade (lead_id);
COMMENT ON TABLE oportunidade IS 'CRM deal aggregate root; moves through pipeline stages to GANHA/PERDIDA';
```

**Invariants:** `estado` transitions to `GANHA`/`PERDIDA` at most once (terminal); `PERDIDA` requires `motivo_perda`; `probabilidade` ∈ [0,100].

### 3.2 `historico_estagio` [empresa]

Append-only trail of stage transitions (funnel analytics + audit).

```sql
-- schema: empresa
CREATE TABLE historico_estagio (
    historico_id     UUID NOT NULL DEFAULT gen_random_uuid(),
    oportunidade_id  UUID NOT NULL,
    de_estagio       VARCHAR(40),
    para_estagio     VARCHAR(40) NOT NULL,
    ator_id          UUID,
    ocorrido_em      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (historico_id),
    FOREIGN KEY (oportunidade_id) REFERENCES oportunidade (oportunidade_id) ON DELETE CASCADE
);
CREATE INDEX idx_historico_oportunidade ON historico_estagio (oportunidade_id);
COMMENT ON TABLE historico_estagio IS 'Append-only stage transition trail of an oportunidade';
```

**Invariants:** every stage change writes exactly one row; never updated/deleted (append-only).

### 3.3 `oferta` [empresa]

Catalog item (product/service) with price; versioned. Gives meaning to recognized revenue.

```sql
-- schema: empresa
CREATE TABLE oferta (
    oferta_id    UUID NOT NULL DEFAULT gen_random_uuid(),
    nome         VARCHAR(180) NOT NULL,
    sku          VARCHAR(80),
    preco        NUMERIC(15,2) NOT NULL DEFAULT 0,
    moeda        CHAR(3) NOT NULL DEFAULT 'BRL',
    versao       INT NOT NULL DEFAULT 1,
    ativo        BOOLEAN NOT NULL DEFAULT true,
    vigente_de   TIMESTAMPTZ,
    vigente_ate  TIMESTAMPTZ,
    criado_em    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (oferta_id),
    UNIQUE (sku, versao),
    CHECK (preco >= 0)
);
CREATE INDEX idx_oferta_ativo ON oferta (ativo);
COMMENT ON TABLE oferta IS 'Versioned offer catalog (product + price + validity)';
```

**Invariants:** `(sku, versao)` unique when `sku` present; `preco >= 0`.

### 3.4 `compra` [empresa]

Aggregate root of revenue. A **confirmed** order from an external system; recognizes revenue.
Idempotent per `(id_externo, origem)` — reprocessing the same order never double-counts revenue.

```sql
-- schema: empresa
CREATE TABLE compra (
    compra_id        UUID NOT NULL DEFAULT gen_random_uuid(),
    id_externo       VARCHAR(120) NOT NULL,
    origem           VARCHAR(60) NOT NULL,
    contato_ref      VARCHAR(255) NOT NULL,
    oportunidade_id  UUID,
    valor_total      NUMERIC(15,2) NOT NULL,
    moeda            CHAR(3) NOT NULL DEFAULT 'BRL',
    status           VARCHAR(20) NOT NULL DEFAULT 'CONFIRMADA',
    base_legal       VARCHAR(40) NOT NULL,
    nome_comprador   VARCHAR(200),
    email_comprador  VARCHAR(255),
    confirmada_em    TIMESTAMPTZ NOT NULL DEFAULT now(),
    criado_em        TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em    TIMESTAMPTZ,
    PRIMARY KEY (compra_id),
    UNIQUE (id_externo, origem),
    FOREIGN KEY (oportunidade_id) REFERENCES oportunidade (oportunidade_id) ON DELETE SET NULL,
    CHECK (status IN ('CONFIRMADA','ESTORNADA','CANCELADA')),
    CHECK (base_legal IN ('CONSENTIMENTO','LEGITIMO_INTERESSE','EXECUCAO_CONTRATO','OBRIGACAO_LEGAL')),
    CHECK (valor_total >= 0)
);
CREATE INDEX idx_compra_contato ON compra (contato_ref);
CREATE INDEX idx_compra_status ON compra (status);
CREATE INDEX idx_compra_oportunidade ON compra (oportunidade_id);
COMMENT ON TABLE compra IS 'Revenue aggregate root; unique per (id_externo, origem) for idempotency';
COMMENT ON COLUMN compra.contato_ref IS 'Normalized buyer key (lower(email)/document) used to consolidate LTV';
```

**Invariants:** unique `(id_externo, origem)` per schema (idempotency); `valor_total` equals Σ `item_compra.valor_total`; `base_legal` required; confirmed `compra` is immutable except status transition to `ESTORNADA`/`CANCELADA`.

### 3.5 `item_compra` [empresa]

A purchase line: offer + quantity + value.

```sql
-- schema: empresa
CREATE TABLE item_compra (
    item_id        UUID NOT NULL DEFAULT gen_random_uuid(),
    compra_id      UUID NOT NULL,
    oferta_id      UUID,
    descricao      VARCHAR(180),
    quantidade     INT NOT NULL DEFAULT 1,
    valor_unitario NUMERIC(15,2) NOT NULL DEFAULT 0,
    valor_total    NUMERIC(15,2) NOT NULL DEFAULT 0,
    PRIMARY KEY (item_id),
    FOREIGN KEY (compra_id) REFERENCES compra (compra_id) ON DELETE CASCADE,
    FOREIGN KEY (oferta_id) REFERENCES oferta (oferta_id) ON DELETE SET NULL,
    CHECK (quantidade > 0),
    CHECK (valor_unitario >= 0),
    CHECK (valor_total >= 0)
);
CREATE INDEX idx_item_compra_compra ON item_compra (compra_id);
COMMENT ON TABLE item_compra IS 'Purchase line; sum of valor_total equals compra.valor_total';
```

**Invariants:** `valor_total = quantidade * valor_unitario`; Σ items = `compra.valor_total` (revenue conservation, SPEC-03).

### 3.6 `modelo_atribuicao` [empresa]

Versioned attribution model. Every attribution references the model version that produced it.

```sql
-- schema: empresa
CREATE TABLE modelo_atribuicao (
    modelo_id    UUID NOT NULL DEFAULT gen_random_uuid(),
    tipo         VARCHAR(20) NOT NULL DEFAULT 'LAST_TOUCH',
    versao       INT NOT NULL,
    ativo        BOOLEAN NOT NULL DEFAULT false,
    vigente_de   TIMESTAMPTZ,
    criado_em    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (modelo_id),
    UNIQUE (versao),
    CHECK (tipo IN ('LAST_TOUCH','FIRST_TOUCH','LINEAR'))
);
CREATE UNIQUE INDEX uq_modelo_atribuicao_ativo ON modelo_atribuicao (ativo) WHERE ativo = true;
COMMENT ON TABLE modelo_atribuicao IS 'Versioned attribution model; exactly one active at a time';
```

**Invariants:** at most one `ativo=true` row (partial unique index); `versao` strictly increasing; default seed `LAST_TOUCH` v1 active per tenant.

### 3.7 `atribuicao` [empresa]

Distribution of a purchase's revenue across touchpoints under the active model (the breakdown).

```sql
-- schema: empresa
CREATE TABLE atribuicao (
    atribuicao_id    UUID NOT NULL DEFAULT gen_random_uuid(),
    compra_id        UUID NOT NULL,
    touchpoint       VARCHAR(180) NOT NULL,
    tipo_touchpoint  VARCHAR(20) NOT NULL,
    valor_atribuido  NUMERIC(15,2) NOT NULL,
    versao_modelo    INT NOT NULL,
    calculado_em     TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (atribuicao_id),
    FOREIGN KEY (compra_id) REFERENCES compra (compra_id) ON DELETE CASCADE,
    CHECK (tipo_touchpoint IN ('ORIGEM_LEAD','JORNADA','CAMPANHA','DIRETO')),
    CHECK (valor_atribuido >= 0)
);
CREATE INDEX idx_atribuicao_compra ON atribuicao (compra_id);
CREATE INDEX idx_atribuicao_touchpoint ON atribuicao (tipo_touchpoint, touchpoint);
COMMENT ON COLUMN atribuicao.versao_modelo IS 'modelo_atribuicao.versao that produced this attribution (audit)';
```

**Invariants:** Σ `valor_atribuido` per `compra_id` equals `compra.valor_total` (revenue conservation, SPEC-03); `versao_modelo` references an existing `modelo_atribuicao.versao`.

### 3.8 `campanha` [empresa]

Attribution target (source/promotion). Feeds the Elastic `campaign-events` index.

```sql
-- schema: empresa
CREATE TABLE campanha (
    campanha_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    nome         VARCHAR(180) NOT NULL,
    origem       VARCHAR(80),
    ativo        BOOLEAN NOT NULL DEFAULT true,
    iniciada_em  TIMESTAMPTZ,
    encerrada_em TIMESTAMPTZ,
    criado_em    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (campanha_id),
    UNIQUE (nome)
);
CREATE INDEX idx_campanha_ativo ON campanha (ativo);
COMMENT ON TABLE campanha IS 'Campaign as an attribution target (ROI by campaign)';
```

### 3.9 `ltv` [empresa]

Materialized Lifetime Value per contact; a deterministic function of confirmed purchases.

```sql
-- schema: empresa
CREATE TABLE ltv (
    contato_ref        VARCHAR(255) NOT NULL,
    valor_total        NUMERIC(15,2) NOT NULL DEFAULT 0,
    num_compras        INT NOT NULL DEFAULT 0,
    primeira_compra_em TIMESTAMPTZ,
    ultima_compra_em   TIMESTAMPTZ,
    atualizado_em      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (contato_ref),
    CHECK (valor_total >= 0),
    CHECK (num_compras >= 0)
);
COMMENT ON TABLE ltv IS 'Materialized LTV per contato_ref; recomputed on compra.confirmada / estorno';
```

**Invariants:** one row per `contato_ref`; `valor_total`/`num_compras` are deterministic over the contact's `CONFIRMADA` purchases (SPEC-03); `ESTORNADA`/`CANCELADA` purchases are excluded from the running total.

## 4. Relations (ASCII)

```
oportunidade 1───N historico_estagio
oportunidade 1───N compra            (compra.oportunidade_id nullable — direct sale allowed)
compra 1───N item_compra N───1 oferta
compra 1───N atribuicao
atribuicao.versao_modelo ──▶ modelo_atribuicao.versao  (logical ref)
atribuicao.touchpoint (tipo CAMPANHA) ──▶ campanha.nome  (logical ref)
compra.contato_ref ──▶ ltv.contato_ref  (aggregation key)
```

## 5. Migration plan

| Range | Theme |
|---|---|
| `V<N>__sale_pipeline.sql` | oportunidade, historico_estagio |
| `V<N>__sale_catalog.sql` | oferta |
| `V<N>__sale_purchases.sql` | compra, item_compra |
| `V<N>__sale_attribution.sql` | modelo_atribuicao, atribuicao, campanha |
| `V<N>__sale_ltv.sql` | ltv |

> All blocks are `-- schema: empresa` → routed to `db/migration/empresa/` and applied to every tenant
> schema. Default pipeline stages, an initial `oferta` catalog and a default `modelo_atribuicao`
> (`LAST_TOUCH` v1, active) are seeded per tenant on `journey-os.empresa.provisionada` consume (not via
> a global data migration). `V<N>` ranges are assigned by `journey-os-migrations` to avoid collisions
> across modules.
