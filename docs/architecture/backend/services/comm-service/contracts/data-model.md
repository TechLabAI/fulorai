# Data Model — COMM (Communication Hub, schema `emp_<slug>`)

> COMM owns communication tables in the **tenant operational schema** `emp_<slug>`. These tables
> are authored here and extracted by `scripts/be-migration-generator.py` into
> `db/migration/empresa/` (centralized Flyway in `journey-os-migrations`). COMM runs
> `ddl-auto=validate`.
>
> **Tenant isolation:** operational tables carry **no `empresa_id`** column — the schema itself
> isolates the tenant (`SET search_path TO emp_<id>, journeyos_global, public` per connection,
> via `MultiTenantConnectionProvider`). See `shared/modelo-dados/empresa.md`.
> Identifiers are **pt-BR** snake_case to match the platform convention.

## 1. Conventions

- **PK strategy:** `UUID` (`gen_random_uuid()`, from `pgcrypto` provided by MIG) for all domain entities.
- **Timestamps:** `criado_em TIMESTAMPTZ NOT NULL DEFAULT now()`, `atualizado_em TIMESTAMPTZ`.
- **Soft-delete:** template uses `estado='ARQUIVADO'` (sent messages are never physically deleted).
- **Immutability:** `mensagem.conteudo_renderizado` is the frozen snapshot of what was sent; `evento_entrega` rows are append-only (write-once).
- **Content:** `variaveis`, `condicoes`, `canais_fallback`, `destinatario`, `conteudo_renderizado`, `provedor_payload`, `brief_composicao`, `janela_envio` are `JSONB`.
- **Secrets:** `config_canal.credencial_ref` stores a **reference** to a secret (e.g. `secret://...` / `${VAR}`), never the raw secret.
- All COMM tables live in `emp_<slug>` (schema: empresa), replicated per tenant by MIG.

## 2. Schema-level mapping

| Table | Schema |
|---|---|
| template_mensagem, mensagem, evento_entrega, regra_roteamento, config_canal | `empresa` (`emp_<slug>`) |
| outbox_event, processed_events | `empresa` (shared idempotency/outbox migration — referenced, not redefined here) |

## 3. Entities

### 3.1 `template_mensagem` [empresa]

Reusable, channel-typed message template with `{{variavel}}` placeholders. Aggregate root.
May reference a published ASST asset as its source (`asset_origem_id`). `estado` gates whether
it can be used for real dispatch (only `ATIVO`).

```sql
-- schema: empresa
CREATE TABLE template_mensagem (
    id                UUID NOT NULL DEFAULT gen_random_uuid(),
    nome              VARCHAR(180) NOT NULL,
    canal             VARCHAR(20) NOT NULL,
    tipo_template     VARCHAR(20) NOT NULL,
    assunto           VARCHAR(240),
    corpo             TEXT NOT NULL,
    variaveis         JSONB NOT NULL DEFAULT '[]'::jsonb,
    asset_origem_id   UUID,
    estado            VARCHAR(20) NOT NULL DEFAULT 'RASCUNHO',
    versao            INTEGER NOT NULL DEFAULT 1,
    brief_composicao  JSONB,
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em     TIMESTAMPTZ,
    PRIMARY KEY (id),
    CHECK (canal IN ('WHATSAPP','EMAIL','TELEGRAM','SMS')),
    CHECK (tipo_template IN ('TRANSACIONAL','MARKETING','NOTIFICACAO')),
    CHECK (estado IN ('RASCUNHO','ATIVO','ARQUIVADO')),
    CHECK (versao >= 1)
);
CREATE INDEX idx_template_canal_estado ON template_mensagem (canal, estado);
CREATE INDEX idx_template_nome ON template_mensagem (nome);
COMMENT ON TABLE template_mensagem IS 'Channel-typed reusable message template; estado=ATIVO required for real dispatch';
```

**Invariants:** `nome` not blank; if `canal='EMAIL'` then `assunto` not blank; every placeholder
in `corpo` SHALL be declared in `variaveis`; only `estado='ATIVO'` is dispatchable.

### 3.2 `mensagem` [empresa]

A dispatch instance to a recipient over a channel. Carries the **immutable** rendered snapshot
and the delivery state. Idempotent on `chave_idempotencia`.

```sql
-- schema: empresa
CREATE TABLE mensagem (
    id                    UUID NOT NULL DEFAULT gen_random_uuid(),
    template_id           UUID,
    canal                 VARCHAR(20) NOT NULL,
    lead_id               UUID NOT NULL,
    destinatario          JSONB NOT NULL,
    conteudo_renderizado  JSONB NOT NULL,
    estado_entrega        VARCHAR(20) NOT NULL DEFAULT 'PENDENTE',
    provedor              VARCHAR(20),
    provedor_message_id   VARCHAR(180),
    tentativas            INTEGER NOT NULL DEFAULT 0,
    motivo_falha          TEXT,
    chave_idempotencia    VARCHAR(120) NOT NULL,
    agendado_para         TIMESTAMPTZ,
    criado_em             TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em         TIMESTAMPTZ,
    PRIMARY KEY (id),
    FOREIGN KEY (template_id) REFERENCES template_mensagem (id) ON DELETE SET NULL,
    UNIQUE (chave_idempotencia),
    CHECK (canal IN ('WHATSAPP','EMAIL','TELEGRAM','SMS')),
    CHECK (estado_entrega IN ('PENDENTE','ENFILEIRADA','ENVIADA','ENTREGUE','LIDA','FALHADA')),
    CHECK (tentativas >= 0)
);
CREATE INDEX idx_mensagem_lead ON mensagem (lead_id);
CREATE INDEX idx_mensagem_estado ON mensagem (estado_entrega);
CREATE INDEX idx_mensagem_provedor_msg ON mensagem (provedor_message_id);
COMMENT ON TABLE mensagem IS 'Dispatch instance; conteudo_renderizado is the immutable sent snapshot; idempotent on chave_idempotencia';
```

**Invariants:** `chave_idempotencia` unique within the tenant schema; `conteudo_renderizado`
never updated after ENVIADA; `estado_entrega` transitions only per the delivery state machine
(SPEC-02) and are monotonic.

### 3.3 `evento_entrega` [empresa]

Append-only lifecycle trail of a message. Feeds the Elastic `communication-events` projection.

```sql
-- schema: empresa
CREATE TABLE evento_entrega (
    id                UUID NOT NULL DEFAULT gen_random_uuid(),
    mensagem_id       UUID NOT NULL,
    tipo              VARCHAR(20) NOT NULL,
    provedor_payload  JSONB,
    ocorrido_em       TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (mensagem_id) REFERENCES mensagem (id) ON DELETE CASCADE,
    CHECK (tipo IN ('ENFILEIRADA','ENVIADA','ENTREGUE','LIDA','FALHADA','REJEITADA'))
);
CREATE INDEX idx_evento_entrega_mensagem ON evento_entrega (mensagem_id);
COMMENT ON TABLE evento_entrega IS 'Append-only delivery lifecycle events; source for the communication-events Elastic fact index';
```

**Invariants:** write-once (no UPDATE/DELETE in normal operation); every delivery-state transition
of a `mensagem` writes exactly one `evento_entrega`.

### 3.4 `regra_roteamento` [empresa]

Prioritized rule resolving preferred channel + fallback + template from recipient/context conditions.

```sql
-- schema: empresa
CREATE TABLE regra_roteamento (
    id               UUID NOT NULL DEFAULT gen_random_uuid(),
    nome             VARCHAR(180) NOT NULL,
    prioridade       INTEGER NOT NULL DEFAULT 100,
    condicoes        JSONB NOT NULL DEFAULT '{}'::jsonb,
    canal_preferido  VARCHAR(20) NOT NULL,
    canais_fallback  JSONB NOT NULL DEFAULT '[]'::jsonb,
    template_id      UUID,
    ativa            BOOLEAN NOT NULL DEFAULT true,
    criado_em        TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em    TIMESTAMPTZ,
    PRIMARY KEY (id),
    FOREIGN KEY (template_id) REFERENCES template_mensagem (id) ON DELETE SET NULL,
    CHECK (canal_preferido IN ('WHATSAPP','EMAIL','TELEGRAM','SMS')),
    CHECK (prioridade >= 0)
);
CREATE INDEX idx_regra_roteamento_prioridade ON regra_roteamento (prioridade) WHERE ativa = true;
COMMENT ON TABLE regra_roteamento IS 'Prioritized routing rule; lower prioridade evaluated first; resolves channel + fallback + template';
```

**Invariants:** lower `prioridade` evaluated first; an active rule SHALL resolve a valid channel
(preferred or one of `canais_fallback`) or routing fails explicitly (no silent drop).

### 3.5 `config_canal` [empresa]

Per-tenant channel/provider configuration. Holds only a **reference** to the provider secret.

```sql
-- schema: empresa
CREATE TABLE config_canal (
    id                    UUID NOT NULL DEFAULT gen_random_uuid(),
    canal                 VARCHAR(20) NOT NULL,
    provedor              VARCHAR(20) NOT NULL,
    identidade_remetente  VARCHAR(180) NOT NULL,
    credencial_ref        VARCHAR(240) NOT NULL,
    janela_envio          JSONB,
    ativo                 BOOLEAN NOT NULL DEFAULT true,
    criado_em             TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em         TIMESTAMPTZ,
    PRIMARY KEY (id),
    UNIQUE (canal, provedor),
    CHECK (canal IN ('WHATSAPP','EMAIL','TELEGRAM','SMS')),
    CHECK (provedor IN ('META_WABA','SES','SENDGRID','TELEGRAM_BOT','TWILIO','SNS'))
);
CREATE INDEX idx_config_canal_canal ON config_canal (canal) WHERE ativo = true;
COMMENT ON TABLE config_canal IS 'Per-tenant channel/provider config; credencial_ref is a secret reference, never the raw secret';
```

**Invariants:** `(canal, provedor)` unique per tenant; `credencial_ref` never holds a raw secret.

## 4. Relations (ASCII)

```
template_mensagem (1) ───< (N) mensagem            [mensagem.template_id → template_mensagem.id, nullable]
mensagem          (1) ───< (N) evento_entrega
template_mensagem (1) ───< (N) regra_roteamento    [regra_roteamento.template_id, nullable]
config_canal      (per canal/provedor) ── resolves provider for a mensagem's canal
```

## 5. Migration plan

- Reserved range in `db/migration/empresa/`: `V<N>__comm_*.sql` (allocated by MIG; COMM does not own the V-number sequence).
- `be-migration-generator.py` extracts the `sql` blocks above **in order** into the communication DDL migration.
- `outbox_event` and `processed_events` are provided by the shared outbox/idempotency migration
  (`journey-os-migrations/.../V<N>__shared_outbox.sql`) — **not** redefined here.

## 6. Analytics projection (not PostgreSQL)

The delivery-lifecycle analytics projection lives in the Elasticsearch **fact** (append-only)
index `communication-events` (one document per `evento_entrega`). It is rebuildable from
`evento_entrega`; PostgreSQL remains the source of truth. Contract:
`docs/architecture/integrations/elastic-data-contract.md`.
