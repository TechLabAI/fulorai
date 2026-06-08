# Data Model — JRNY (Journey & Routing, schema `emp_<slug>`)

> JRNY owns its journey/routing tables in the **tenant operational schema** `emp_<slug>`. These
> tables are authored here and extracted by `scripts/be-migration-generator.py` into
> `db/migration/empresa/` (centralized Flyway in `journey-os-migrations`). JRNY runs
> `ddl-auto=validate`.
>
> **Tenant isolation:** every JRNY table carries an explicit `empresa_id UUID NOT NULL` column as
> a **defense-in-depth tenant guard** (set from `EmpresaContextHolder.require()` on both the HTTP
> and the Kafka-consume paths). It is **redundant** to the schema isolation (the `emp_<slug>`
> schema already isolates the tenant via `SET search_path`), but JRNY's vision (ADR-004, doc 05 §2,
> doc 03 §5 invariant 7) mandates it: routing decisions and enrolments are cross-module-referenced
> facts and the explicit guard makes every query and every immutable decision provably
> single-tenant. JRNY **never** writes to `journeyos_global`.
> Identifiers are **pt-BR** snake_case to match the platform convention.

## 0. Extensions

JRNY needs **no new** Postgres extension. UUID generation uses `gen_random_uuid()` from `pgcrypto`,
already provided globally by MIG (`-- schema: global`). It is **not** re-declared here — JRNY only
*uses* it. `jsonb` is core Postgres. No extension block is emitted by this contract.

## 1. Conventions

- **PK strategy:** `UUID` (`gen_random_uuid()`, from `pgcrypto` provided by MIG) for all entities.
- **Tenant guard:** every table carries `empresa_id UUID NOT NULL` = `EmpresaContextHolder.require()` (ADR-004).
- **Timestamps:** `criado_em TIMESTAMPTZ NOT NULL DEFAULT now()`, `atualizado_em TIMESTAMPTZ` where mutable.
- **Soft-delete:** journeys use `estado_jornada='ARQUIVADA'`; enrolments use `estado='ENCERRADA'`/`'CONCLUIDA'` (never physical DELETE).
- **Immutability:** `decisao_roteamento` rows are **write-once** — no UPDATE/DELETE path in the domain (enforced in `application/service`; see SPEC-04/SPEC-02).
- **Cross-module refs are logical:** `lead_id` (→ LEAD) and `estagio.asset_ref_id` (→ ASST) are **logical references**, never physical FKs to other schemas/services.
- **Predicate/config payloads:** `regra_roteamento.condicao`, `estagio.config` and `decisao_roteamento.snapshot_entrada` are `JSONB`.
- All JRNY tables live in `emp_<slug>` (schema: empresa), replicated per tenant by MIG.

## 2. Schema-level mapping

| Table | Schema |
|---|---|
| jornada, estagio, regra_roteamento, inscricao_jornada, decisao_roteamento | `empresa` (`emp_<slug>`) |
| outbox_event, processed_events | `empresa` (shared idempotency/outbox migration — referenced, not redefined here) |

## 3. Entities

### 3.1 `jornada` [empresa]

Aggregate root: a versioned multi-stage funnel definition for the tenant. Drives the publication
state machine `RASCUNHO → PUBLICADA → ARQUIVADA`. Editing a `PUBLICADA` journey is forbidden
in-place — a change produces a new `versao` (ADR-005).

```sql
-- schema: empresa
CREATE TABLE jornada (
    id              UUID NOT NULL DEFAULT gen_random_uuid(),
    empresa_id      UUID NOT NULL,
    nome            VARCHAR(180) NOT NULL,
    descricao       TEXT,
    estado_jornada  VARCHAR(20) NOT NULL DEFAULT 'RASCUNHO',
    versao          INTEGER NOT NULL DEFAULT 1,
    criado_por      UUID NOT NULL,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em   TIMESTAMPTZ,
    PRIMARY KEY (id),
    CHECK (estado_jornada IN ('RASCUNHO','PUBLICADA','ARQUIVADA')),
    CHECK (versao >= 1)
);
CREATE INDEX idx_jornada_empresa_estado ON jornada (empresa_id, estado_jornada);
COMMENT ON TABLE jornada IS 'Aggregate root: versioned funnel definition; estado_jornada drives the publication state machine (ADR-005)';
COMMENT ON COLUMN jornada.empresa_id IS 'Tenant guard (redundant to schema isolation) = EmpresaContextHolder.require()';
COMMENT ON COLUMN jornada.versao IS 'Incremental per journey; a PUBLICADA journey is never edited in place — a change produces a new versao';
```

**Invariants (EARS):**
- `THE SYSTEM SHALL keep estado_jornada within { RASCUNHO, PUBLICADA, ARQUIVADA } and SHALL only transition it per the Journey Builder state machine (SPEC-03).`
- `IF an edit targets a jornada that is not in RASCUNHO, THEN THE SYSTEM SHALL reject the in-place change and require a new versao.`
- `THE SYSTEM SHALL set empresa_id = EmpresaContextHolder.require() on every jornada row.`

### 3.2 `estagio` [empresa]

Ordered, typed child stage of a journey. May reference a published asset of ASST
(`asset_ref_id`, logical), may be `terminal`, and carries a `config` jsonb (signalled actions,
parameters). Stage `ordem` is unique within a journey.

```sql
-- schema: empresa
CREATE TABLE estagio (
    id            UUID NOT NULL DEFAULT gen_random_uuid(),
    empresa_id    UUID NOT NULL,
    jornada_id    UUID NOT NULL,
    ordem         INTEGER NOT NULL,
    tipo_estagio  VARCHAR(20) NOT NULL,
    nome          VARCHAR(180) NOT NULL,
    asset_ref_id  UUID,
    terminal      BOOLEAN NOT NULL DEFAULT false,
    config        JSONB NOT NULL DEFAULT '{}'::jsonb,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em TIMESTAMPTZ,
    PRIMARY KEY (id),
    FOREIGN KEY (jornada_id) REFERENCES jornada (id) ON DELETE CASCADE,
    UNIQUE (jornada_id, ordem),
    CHECK (ordem >= 1),
    CHECK (tipo_estagio IN ('CAPTURA','NUTRICAO','QUALIFICACAO','OFERTA','FECHAMENTO','POS_VENDA'))
);
CREATE INDEX idx_estagio_jornada ON estagio (jornada_id);
CREATE INDEX idx_estagio_empresa ON estagio (empresa_id);
COMMENT ON TABLE estagio IS 'Ordered typed stage within a journey; asset_ref_id is a logical reference to a published ASST asset (no physical FK)';
COMMENT ON COLUMN estagio.asset_ref_id IS 'Logical ref to ASST published asset; refreshed reactively on journey-os.asset.versao.publicada';
COMMENT ON COLUMN estagio.terminal IS 'Marks a final stage; reaching it concludes the inscricao (journey-os.jornada.concluida)';
```

**Invariants (EARS):**
- `THE SYSTEM SHALL enforce a unique (jornada_id, ordem) so no two stages share a position in a journey.`
- `THE SYSTEM SHALL keep tipo_estagio within the six MVP stage types (CAPTURA..POS_VENDA).`
- `IF asset_ref_id references an asset, THEN THE SYSTEM SHALL treat it as a logical reference resolved via AssetQueryClient and SHALL NOT create a physical FK across schemas.`

### 3.3 `regra_roteamento` [empresa]

Versioned routing rule of a journey. The `condicao` jsonb is a predicate over the lead's
qualification snapshot (aggregate score, 6D dimensions, segment, attributes — sourced from LEAD
events). Rules are evaluated deterministically, ordered by `prioridade` ascending (lower =
evaluated first). `estagio_origem_id` null means an **entry** rule (enrolment).

```sql
-- schema: empresa
CREATE TABLE regra_roteamento (
    id                 UUID NOT NULL DEFAULT gen_random_uuid(),
    empresa_id         UUID NOT NULL,
    jornada_id         UUID NOT NULL,
    estagio_origem_id  UUID,
    estagio_destino_id UUID NOT NULL,
    condicao           JSONB NOT NULL DEFAULT '{}'::jsonb,
    prioridade         INTEGER NOT NULL DEFAULT 100,
    versao             INTEGER NOT NULL DEFAULT 1,
    ativa              BOOLEAN NOT NULL DEFAULT true,
    criado_por         UUID NOT NULL,
    criado_em          TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em      TIMESTAMPTZ,
    PRIMARY KEY (id),
    FOREIGN KEY (jornada_id) REFERENCES jornada (id) ON DELETE CASCADE,
    FOREIGN KEY (estagio_origem_id) REFERENCES estagio (id) ON DELETE CASCADE,
    FOREIGN KEY (estagio_destino_id) REFERENCES estagio (id) ON DELETE CASCADE,
    CHECK (versao >= 1),
    CHECK (prioridade >= 0)
);
CREATE INDEX idx_regra_jornada_origem ON regra_roteamento (jornada_id, estagio_origem_id, prioridade);
CREATE INDEX idx_regra_ativa ON regra_roteamento (jornada_id, ativa);
COMMENT ON TABLE regra_roteamento IS 'Versioned routing rule; condicao is a deterministic predicate over the lead qualification snapshot (score/dimensoes/segmento/atributo)';
COMMENT ON COLUMN regra_roteamento.estagio_origem_id IS 'NULL = entry rule (enrolment); non-null = jump rule from a given stage';
COMMENT ON COLUMN regra_roteamento.prioridade IS 'Ascending tie-break: lower is evaluated first; first satisfied rule wins (ADR-005)';
COMMENT ON COLUMN regra_roteamento.condicao IS 'JSONB predicate grammar — see §5 condicao grammar (operadores + campos do lead de LEAD)';
```

**Invariants (EARS):**
- `THE SYSTEM SHALL evaluate active rules of a journey ordered by prioridade ascending and SHALL select the first rule whose condicao is satisfied.`
- `WHILE a rule has ativa=false, THE SYSTEM SHALL exclude it from evaluation.`
- `THE SYSTEM SHALL treat estagio_origem_id IS NULL as an entry (enrolment) rule.`
- `THE SYSTEM SHALL evaluate condicao deterministically so the same snapshot_entrada and the same rule version always yield the same outcome (ADR-005).`

### 3.4 `inscricao_jornada` [empresa]

A lead's execution state within a journey: current stage, entry version, lifecycle state. A lead
has **at most one** `ATIVA` enrolment per journey at a time (unique partial index). Pins the
`jornada_versao` of entry so active enrolments are not mutated when a new journey version is
published.

```sql
-- schema: empresa
CREATE TABLE inscricao_jornada (
    id                  UUID NOT NULL DEFAULT gen_random_uuid(),
    empresa_id          UUID NOT NULL,
    lead_id             UUID NOT NULL,
    jornada_id          UUID NOT NULL,
    jornada_versao      INTEGER NOT NULL,
    estagio_corrente_id UUID NOT NULL,
    estado              VARCHAR(20) NOT NULL DEFAULT 'ATIVA',
    entrou_em           TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em       TIMESTAMPTZ,
    PRIMARY KEY (id),
    FOREIGN KEY (jornada_id) REFERENCES jornada (id) ON DELETE CASCADE,
    FOREIGN KEY (estagio_corrente_id) REFERENCES estagio (id),
    CHECK (estado IN ('ATIVA','CONCLUIDA','ENCERRADA')),
    CHECK (jornada_versao >= 1)
);
CREATE UNIQUE INDEX uq_inscricao_lead_jornada_ativa
    ON inscricao_jornada (lead_id, jornada_id) WHERE estado = 'ATIVA';
CREATE INDEX idx_inscricao_lead ON inscricao_jornada (empresa_id, lead_id);
CREATE INDEX idx_inscricao_jornada ON inscricao_jornada (jornada_id);
COMMENT ON TABLE inscricao_jornada IS 'Lead execution state in a journey; pins jornada_versao of entry so active enrolments are immune to new versions (ADR-005)';
COMMENT ON INDEX uq_inscricao_lead_jornada_ativa IS 'A lead has at most one ATIVA enrolment per journey (idempotency guard against event reprocessing — R3)';
COMMENT ON COLUMN inscricao_jornada.jornada_versao IS 'Version of the journey at enrolment time; never changes for an active enrolment';
```

**Invariants (EARS):**
- `THE SYSTEM SHALL allow at most one inscricao_jornada in state ATIVA per (lead_id, jornada_id) at any time.`
- `THE SYSTEM SHALL pin jornada_versao at enrolment time and SHALL NOT change it for an active enrolment when a new journey version is published.`
- `WHEN an enrolment reaches a terminal stage, THE SYSTEM SHALL set estado=CONCLUIDA.`
- `THE SYSTEM SHALL advance estagio_corrente_id only through a Routing Engine decision, never by arbitrary jump.`

### 3.5 `decisao_roteamento` [empresa] *(immutable — decision log)*

Write-once record of one Routing Engine decision: the trigger, the input snapshot that produced
it, the fired rule (if any), whether AI assisted, the result and the chosen target. It is the
auditable "why" of every routing decision. **Never updated, never deleted** in normal operation;
projected into the Elastic `routing-decisions` index (fact).

```sql
-- schema: empresa
CREATE TABLE decisao_roteamento (
    id                UUID NOT NULL DEFAULT gen_random_uuid(),
    empresa_id        UUID NOT NULL,
    lead_id           UUID NOT NULL,
    inscricao_id      UUID,
    jornada_id        UUID,
    gatilho           VARCHAR(60) NOT NULL,
    snapshot_entrada  JSONB NOT NULL,
    regra_id          UUID,
    assist_ia         VARCHAR(20) NOT NULL DEFAULT 'IGNORADO',
    resultado         VARCHAR(20) NOT NULL,
    estagio_alvo_id   UUID,
    motivo            TEXT NOT NULL,
    decidido_em       TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (inscricao_id) REFERENCES inscricao_jornada (id) ON DELETE SET NULL,
    FOREIGN KEY (regra_id) REFERENCES regra_roteamento (id) ON DELETE SET NULL,
    FOREIGN KEY (estagio_alvo_id) REFERENCES estagio (id) ON DELETE SET NULL,
    CHECK (assist_ia IN ('USADO','IGNORADO','INDISPONIVEL')),
    CHECK (resultado IN ('ROTEADO','SEM_MUDANCA','NAO_ROTEADO')),
    CHECK (resultado <> 'ROTEADO' OR estagio_alvo_id IS NOT NULL)
);
CREATE INDEX idx_decisao_lead ON decisao_roteamento (empresa_id, lead_id, decidido_em DESC);
CREATE INDEX idx_decisao_inscricao ON decisao_roteamento (inscricao_id);
CREATE INDEX idx_decisao_regra ON decisao_roteamento (regra_id);
COMMENT ON TABLE decisao_roteamento IS 'IMMUTABLE decision log (write-once): the auditable "why" of every routing decision; projected to Elastic routing-decisions (fact). No UPDATE/DELETE in the domain (ADR-005)';
COMMENT ON COLUMN decisao_roteamento.gatilho IS 'Origin event of the decision (e.g. lead.qualificado, lead.score.atualizado, lead.segmento.alterado)';
COMMENT ON COLUMN decisao_roteamento.snapshot_entrada IS 'Score/dimensoes/segmento/atributos at decision time — provenance of the decision';
COMMENT ON COLUMN decisao_roteamento.assist_ia IS 'USADO (AI recommendation applied) | IGNORADO (AI not consulted/overridden by guard rule) | INDISPONIVEL (AI timeout/circuit-open — deterministic fallback)';
```

**Invariants (EARS):**
- `THE SYSTEM SHALL persist exactly one decisao_roteamento for every routing evaluation, including SEM_MUDANCA and NAO_ROTEADO outcomes.`
- `IF a decisao_roteamento already exists, THEN THE SYSTEM SHALL NOT update or delete it; a correction SHALL be a new decision.`
- `IF resultado = ROTEADO, THEN THE SYSTEM SHALL require estagio_alvo_id to be non-null (DB CHECK).`
- `THE SYSTEM SHALL record snapshot_entrada on every decision as the provenance of the "why".`

## 4. Relations (ASCII)

```
jornada (1) ───< (N) estagio              [estagio.jornada_id → jornada.id]
jornada (1) ───< (N) regra_roteamento     [regra.jornada_id → jornada.id]
estagio (1) ───< (N) regra_roteamento     [regra.estagio_origem_id (nullable) / estagio_destino_id]
jornada (1) ───< (N) inscricao_jornada    [inscricao.jornada_id → jornada.id; estagio_corrente_id → estagio.id]
inscricao_jornada (1) ───< (N) decisao_roteamento   [decisao.inscricao_id → inscricao.id (nullable)]
regra_roteamento (0..1) ──< (N) decisao_roteamento  [decisao.regra_id → regra.id (nullable)]
estagio (0..1) ──< (N) decisao_roteamento           [decisao.estagio_alvo_id → estagio.id (nullable)]

lead_id          → LEAD     (logical ref — no physical FK)
estagio.asset_ref_id → ASST (logical ref — no physical FK)
```

## 5. `condicao` predicate grammar (regra_roteamento)

The `condicao` jsonb is a deterministic predicate over the lead's qualification snapshot, sourced
from LEAD events (`lead.qualificado` / `lead.score.atualizado` / `lead.segmento.alterado`,
`../lead-service/contracts/event-contracts.md`). MVP grammar:

```json
{
  "operador": "E",
  "predicados": [
    { "campo": "scoreAgregado", "op": ">=", "valor": 70 },
    { "campo": "dimensoes.INTENCAO", "op": ">=", "valor": 80 },
    { "campo": "estadoQualificacao", "op": "=", "valor": "QUALIFICADO" },
    { "campo": "segmentoId", "op": "in", "valor": ["<uuid-seg-a>", "<uuid-seg-b>"] }
  ]
}
```

- **Available fields** (from the LEAD snapshot): `scoreAgregado` (0..100), `dimensoes.<DIM>` where
  `<DIM>` ∈ `{ PERFIL, ENGAJAMENTO, INTENCAO, CAPACIDADE, URGENCIA, ADERENCIA }`,
  `estadoQualificacao`, `segmentoId`, and `atributo.<chave>` for tenant attributes.
- **Operators (`op`):** `=`, `<>`, `>`, `>=`, `<`, `<=`, `in`, `nin`, `existe`.
- **Combinators (`operador`):** `E` (AND), `OU` (OR) over `predicados`.
- `THE SYSTEM SHALL reject (422) a condicao referencing a field outside the documented snapshot grammar at rule-definition time (SPEC-02/SPEC-03).`
- `THE SYSTEM SHALL evaluate condicao as a pure function of the snapshot — no I/O — so it is reproducible (ADR-005).`

## 6. Migration plan

- Reserved range in `db/migration/empresa/`: `V<N>__jrny_*.sql` (allocated by MIG; JRNY does not own the V-number sequence).
- Suggested split: `V<N>__jrny_journey.sql` (jornada, estagio, regra_roteamento), `V<N>__jrny_routing.sql` (inscricao_jornada, decisao_roteamento).
- `be-migration-generator.py` extracts the `sql` blocks above **in order** into the JRNY DDL migrations.
- `outbox_event` and `processed_events` are provided by the shared outbox/idempotency migration
  (`journey-os-migrations/.../V<N>__shared_outbox.sql`) — **not** redefined here.

## 7. Fact projections (not PostgreSQL)

Journey telemetry and the decision log are projected into the Elasticsearch **fact** indices
`journey-events` (stage transitions) and `routing-decisions` (decision log), one document per
fact, `domainContext=JRNY`, ingest `direct-java-client`. They are append-only and **rebuildable**
from the tables above; PostgreSQL remains the source of truth. Contract:
`docs/architecture/integrations/elastic-data-contract.md`.
