# Data Model — ASST (Asset Hub, schema `emp_<slug>`)

> ASST owns asset tables in the **tenant operational schema** `emp_<slug>`. These tables are
> authored here and extracted by `scripts/be-migration-generator.py` into
> `db/migration/empresa/` (centralized Flyway in `journey-os-migrations`). ASST runs
> `ddl-auto=validate`.
>
> **Tenant isolation:** operational tables carry **no `empresa_id`** column — the schema itself
> isolates the tenant (`SET search_path TO emp_<id>, journeyos_global, public` per connection,
> via `MultiTenantConnectionProvider`). See `shared/modelo-dados/empresa.md`.
> Identifiers are **pt-BR** snake_case to match the platform convention.

## 1. Conventions

- **PK strategy:** `UUID` (`gen_random_uuid()`, from `pgcrypto` provided by MIG) for all domain entities.
- **Timestamps:** `criado_em TIMESTAMPTZ NOT NULL DEFAULT now()`, `atualizado_em TIMESTAMPTZ`.
- **Soft-delete:** asset uses `estado_asset='ARQUIVADO'` (never physical DELETE of assets/versions/approvals).
- **Immutability:** `versao_asset` rows are write-once (enforced in the domain; no UPDATE path).
- **Content:** `conteudo`/`binarios`/`brief_composicao` are `JSONB`.
- All ASST tables live in `emp_<slug>` (schema: empresa), replicated per tenant by MIG.

## 2. Schema-level mapping

| Table | Schema |
|---|---|
| asset, versao_asset, aprovacao, tag_asset | `empresa` (`emp_<slug>`) |
| outbox_event, processed_events | `empresa` (shared idempotency/outbox migration — referenced, not redefined here) |

## 3. Entities

### 3.1 `asset` [empresa]

Aggregate root: a managed content asset. Holds the current state in the approval/publication
state machine and a pointer to its current published version (`versao_vigente_id`).

```sql
-- schema: empresa
CREATE TABLE asset (
    id                 UUID NOT NULL DEFAULT gen_random_uuid(),
    tipo_asset         VARCHAR(20) NOT NULL,
    titulo             VARCHAR(180) NOT NULL,
    descricao          TEXT,
    estado_asset       VARCHAR(20) NOT NULL DEFAULT 'RASCUNHO',
    versao_vigente_id  UUID,
    dono_id            UUID NOT NULL,
    criado_em          TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em      TIMESTAMPTZ,
    PRIMARY KEY (id),
    CHECK (tipo_asset IN ('LANDING_PAGE','EMAIL','CRIATIVO','ROTEIRO','DOCUMENTO','SCRIPT_SDR')),
    CHECK (estado_asset IN ('RASCUNHO','EM_REVISAO','APROVADO','PUBLICADO','REJEITADO','ARQUIVADO'))
);
CREATE INDEX idx_asset_tipo_estado ON asset (tipo_asset, estado_asset);
CREATE INDEX idx_asset_dono ON asset (dono_id);
COMMENT ON TABLE asset IS 'Aggregate root of a content asset; estado_asset drives the approval state machine';
```

**Invariants:** `titulo` not blank; `estado_asset` only transitions per the state machine
(SPEC-02); `versao_vigente_id` is non-null only while/after the asset has been PUBLICADO.

### 3.2 `versao_asset` [empresa]

Immutable, numbered revision of an asset's content. Never updated in place — a correction or a
new composition produces a new row with the next `numero`.

```sql
-- schema: empresa
CREATE TABLE versao_asset (
    id                UUID NOT NULL DEFAULT gen_random_uuid(),
    asset_id          UUID NOT NULL,
    numero            INTEGER NOT NULL,
    conteudo          JSONB NOT NULL DEFAULT '{}'::jsonb,
    binarios          JSONB NOT NULL DEFAULT '[]'::jsonb,
    origem            VARCHAR(20) NOT NULL DEFAULT 'MANUAL',
    brief_composicao  JSONB,
    estado            VARCHAR(20) NOT NULL DEFAULT 'RASCUNHO',
    criado_por        UUID NOT NULL,
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (asset_id) REFERENCES asset (id) ON DELETE CASCADE,
    UNIQUE (asset_id, numero),
    CHECK (numero >= 1),
    CHECK (origem IN ('MANUAL','ASSET_STUDIO')),
    CHECK (estado IN ('RASCUNHO','PUBLICADA'))
);
CREATE INDEX idx_versao_asset_asset ON versao_asset (asset_id);
COMMENT ON TABLE versao_asset IS 'Immutable numbered revision; origem=ASSET_STUDIO carries brief_composicao for provenance';
```

**Invariants:** `(asset_id, numero)` unique; `numero` is contiguous starting at 1; rows are
write-once (the application never issues UPDATE); a row with `origem=ASSET_STUDIO` SHALL carry a
non-null `brief_composicao`.

### 3.3 `aprovacao` [empresa]

Record of a review decision (approve/reject) on a specific version. Append-only audit trail.

```sql
-- schema: empresa
CREATE TABLE aprovacao (
    id           UUID NOT NULL DEFAULT gen_random_uuid(),
    asset_id     UUID NOT NULL,
    versao_id    UUID NOT NULL,
    revisor_id   UUID NOT NULL,
    decisao      VARCHAR(20) NOT NULL,
    comentario   TEXT,
    decidido_em  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (asset_id) REFERENCES asset (id) ON DELETE CASCADE,
    FOREIGN KEY (versao_id) REFERENCES versao_asset (id) ON DELETE CASCADE,
    CHECK (decisao IN ('APROVADO','REJEITADO'))
);
CREATE INDEX idx_aprovacao_asset ON aprovacao (asset_id);
COMMENT ON TABLE aprovacao IS 'Append-only review decisions; preserves who approved/rejected and why';
```

**Invariants:** every transition into APROVADO/REJEITADO writes exactly one `aprovacao`;
`revisor_id` is the authenticated reviewer (`asst.asset.aprovar`).

### 3.4 `tag_asset` [empresa]

Organizational labels, manual or AI-suggested (Asset Intelligence). Mirrored into Elastic for search.

```sql
-- schema: empresa
CREATE TABLE tag_asset (
    id        UUID NOT NULL DEFAULT gen_random_uuid(),
    asset_id  UUID NOT NULL,
    valor     VARCHAR(60) NOT NULL,
    origem    VARCHAR(10) NOT NULL DEFAULT 'MANUAL',
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (asset_id) REFERENCES asset (id) ON DELETE CASCADE,
    UNIQUE (asset_id, valor),
    CHECK (origem IN ('MANUAL','IA'))
);
CREATE INDEX idx_tag_asset_valor ON tag_asset (valor);
COMMENT ON TABLE tag_asset IS 'Tags for organization/search; origem=IA produced by Asset Intelligence';
```

**Invariants:** `(asset_id, valor)` unique (no duplicate tags per asset).

## 4. Relations (ASCII)

```
asset (1) ───< (N) versao_asset        [asset.versao_vigente_id → versao_asset.id]
asset (1) ───< (N) aprovacao >─── (1) versao_asset
asset (1) ───< (N) tag_asset
```

## 5. Migration plan

- Reserved range in `db/migration/empresa/`: `V<N>__asst_*.sql` (allocated by MIG; ASST does not own the V-number sequence).
- `be-migration-generator.py` extracts the `sql` blocks above **in order** into the asset DDL migration.
- `outbox_event` and `processed_events` are provided by the shared outbox/idempotency migration
  (`journey-os-migrations/.../V<N>__shared_outbox.sql`) — **not** redefined here.

## 6. Search projection (not PostgreSQL)

The full-text/search and Asset Intelligence projection lives in the Elasticsearch **dimension**
index `assets` (one document per asset reflecting current state + tags). It is rebuildable from
the tables above; PostgreSQL remains the source of truth. Contract:
`docs/architecture/integrations/elastic-data-contract.md`.
