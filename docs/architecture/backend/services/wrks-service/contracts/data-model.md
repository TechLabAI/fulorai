# Data Model — WRKS (IAM, `journeyos_global`)

> WRKS owns the **IAM subset** of `journeyos_global`. These tables are authored here and
> extracted by `scripts/be-migration-generator.py` into `db/migration/global/` (centralized
> Flyway in `journey-os-migrations`). WRKS runs `ddl-auto=validate`.
>
> Identifiers are **pt-BR** to match the canonical RBAC model (`shared/rbac/modelo.md`,
> `shared/modelo-dados/global-schema.md`) already referenced platform-wide. Extensions
> (`pgcrypto` → `gen_random_uuid()`) are provided by MIG.

## 1. Conventions

- **PK strategy:** `UUID` (`gen_random_uuid()`) for domain entities; `VARCHAR(50)` slug for `empresa_id` (= schema name); `BIGSERIAL` for audit trail.
- **Timestamps:** `criado_em TIMESTAMPTZ NOT NULL DEFAULT now()`, `atualizado_em TIMESTAMPTZ`.
- **Soft-delete:** `ativo BOOLEAN NOT NULL DEFAULT true` (never physical DELETE).
- **Naming:** `snake_case`; pt-BR per canonical IAM schema.
- All WRKS tables live in `journeyos_global` (schema: global), created once (not replicated per empresa).

## 2. Schema-level mapping

| Table | Schema |
|---|---|
| empresa, business_unit, team, usuario, usuario_team, papel, permissao, papel_permissao, usuario_empresa, modelo_acesso_versao, evento_auditoria | `global` (`journeyos_global`) |

## 3. Entities

### 3.1 `empresa` [global]

Workspace / tenant. `empresa_id` is the slug and the name of the operational schema
(`emp_<slug>`). `status` tracks provisioning; immutable slug after provisioning.

```sql
-- schema: global
CREATE TABLE journeyos_global.empresa (
    empresa_id      VARCHAR(50) NOT NULL,
    nome_fantasia   VARCHAR(150) NOT NULL,
    razao_social    VARCHAR(200),
    documento       VARCHAR(20),
    status          VARCHAR(20) NOT NULL DEFAULT 'PROVISIONANDO',
    parametros      JSONB NOT NULL DEFAULT '{}'::jsonb,
    ativo           BOOLEAN NOT NULL DEFAULT true,
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em   TIMESTAMPTZ,
    PRIMARY KEY (empresa_id),
    CHECK (status IN ('PROVISIONANDO','ATIVA','INATIVA')),
    CHECK (empresa_id ~ '^emp_[a-z0-9_]+$')
);
COMMENT ON TABLE journeyos_global.empresa IS 'Workspace/tenant; empresa_id = operational schema name emp_<slug>';
```

**Invariants:** `empresa_id` unique and immutable once `status='ATIVA'`; created as `PROVISIONANDO` until MIG confirms; soft-delete sets `ativo=false`/`status='INATIVA'`.

### 3.2 `business_unit` [global]

Organizational subdivision inside an empresa (introduced by WRKS MVP).

```sql
-- schema: global
CREATE TABLE journeyos_global.business_unit (
    business_unit_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    empresa_id        VARCHAR(50) NOT NULL,
    nome              VARCHAR(120) NOT NULL,
    ativo             BOOLEAN NOT NULL DEFAULT true,
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em     TIMESTAMPTZ,
    PRIMARY KEY (business_unit_id),
    FOREIGN KEY (empresa_id) REFERENCES journeyos_global.empresa (empresa_id),
    UNIQUE (empresa_id, nome)
);
CREATE INDEX idx_business_unit_empresa ON journeyos_global.business_unit (empresa_id);
```

**Invariants:** name unique within empresa.

### 3.3 `team` [global]

Group of users inside a business unit.

```sql
-- schema: global
CREATE TABLE journeyos_global.team (
    team_id           UUID NOT NULL DEFAULT gen_random_uuid(),
    business_unit_id  UUID NOT NULL,
    nome              VARCHAR(120) NOT NULL,
    ativo             BOOLEAN NOT NULL DEFAULT true,
    criado_em         TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em     TIMESTAMPTZ,
    PRIMARY KEY (team_id),
    FOREIGN KEY (business_unit_id) REFERENCES journeyos_global.business_unit (business_unit_id),
    UNIQUE (business_unit_id, nome)
);
CREATE INDEX idx_team_bu ON journeyos_global.team (business_unit_id);
```

### 3.4 `usuario` [global]

Physical person who logs in; global to the group, operates N empresas.

```sql
-- schema: global
CREATE TABLE journeyos_global.usuario (
    usuario_id    UUID NOT NULL DEFAULT gen_random_uuid(),
    email         VARCHAR(255) NOT NULL,
    nome          VARCHAR(150) NOT NULL,
    idp_subject   VARCHAR(255),
    ativo         BOOLEAN NOT NULL DEFAULT true,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em TIMESTAMPTZ,
    PRIMARY KEY (usuario_id),
    UNIQUE (email)
);
CREATE UNIQUE INDEX idx_usuario_idp_subject ON journeyos_global.usuario (idp_subject) WHERE idp_subject IS NOT NULL;
COMMENT ON COLUMN journeyos_global.usuario.idp_subject IS 'Keycloak OIDC subject (sub) mapped to this user';
```

**Invariants:** email unique; `idp_subject` (Keycloak `sub`) unique when present.

### 3.5 `usuario_team` [global]

User ↔ team membership.

```sql
-- schema: global
CREATE TABLE journeyos_global.usuario_team (
    usuario_id  UUID NOT NULL,
    team_id     UUID NOT NULL,
    PRIMARY KEY (usuario_id, team_id),
    FOREIGN KEY (usuario_id) REFERENCES journeyos_global.usuario (usuario_id),
    FOREIGN KEY (team_id)    REFERENCES journeyos_global.team (team_id)
);
```

### 3.6 `papel` [global]

Canonical group role (seeded V1 from `rbac.arch.json`): INFOPRODUTOR, HEAD_GROWTH, SDR.

```sql
-- schema: global
CREATE TABLE journeyos_global.papel (
    papel_id   UUID NOT NULL DEFAULT gen_random_uuid(),
    codigo     VARCHAR(50) NOT NULL,
    nome       VARCHAR(100) NOT NULL,
    descricao  TEXT,
    nivel      SMALLINT NOT NULL DEFAULT 0,
    ativo      BOOLEAN NOT NULL DEFAULT true,
    PRIMARY KEY (papel_id),
    UNIQUE (codigo)
);
COMMENT ON COLUMN journeyos_global.papel.nivel IS 'Hierarchy level for anti-escalation guard (higher = more authority)';
```

**Invariants:** `codigo` unique and canonical; `nivel` orders roles for the anti-escalation guard (INV-1).

### 3.7 `permissao` [global]

Atomic permission `<modulo>.<recurso>.<acao>` (seeded from `permission-catalogue.arch.json`).

```sql
-- schema: global
CREATE TABLE journeyos_global.permissao (
    permissao_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    codigo        VARCHAR(100) NOT NULL,
    modulo        VARCHAR(10)  NOT NULL,
    nome          VARCHAR(150) NOT NULL,
    descricao     TEXT,
    PRIMARY KEY (permissao_id),
    UNIQUE (codigo)
);
CREATE INDEX idx_permissao_modulo ON journeyos_global.permissao (modulo);
```

**Invariants:** `codigo` unique; never a wildcard (auditability).

### 3.8 `papel_permissao` [global]

Role ↔ permission (explicit bundle, no wildcards).

```sql
-- schema: global
CREATE TABLE journeyos_global.papel_permissao (
    papel_id      UUID NOT NULL,
    permissao_id  UUID NOT NULL,
    PRIMARY KEY (papel_id, permissao_id),
    FOREIGN KEY (papel_id)     REFERENCES journeyos_global.papel (papel_id),
    FOREIGN KEY (permissao_id) REFERENCES journeyos_global.permissao (permissao_id)
);
```

### 3.9 `usuario_empresa` [global]

User ↔ empresa association carrying the role and optional data scope.

```sql
-- schema: global
CREATE TABLE journeyos_global.usuario_empresa (
    usuario_id  UUID NOT NULL,
    empresa_id  VARCHAR(50) NOT NULL,
    papel       VARCHAR(50) NOT NULL,
    data_scope  VARCHAR(50),
    ativo       BOOLEAN NOT NULL DEFAULT true,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (usuario_id, empresa_id),
    FOREIGN KEY (usuario_id) REFERENCES journeyos_global.usuario (usuario_id),
    FOREIGN KEY (empresa_id) REFERENCES journeyos_global.empresa (empresa_id),
    FOREIGN KEY (papel)      REFERENCES journeyos_global.papel (codigo)
);
CREATE INDEX idx_usuario_empresa_empresa ON journeyos_global.usuario_empresa (empresa_id);
```

**Invariants:** one role per (usuario, empresa); `papel` references a canonical role code; login requires ≥1 active row (INV-2).

### 3.10 `modelo_acesso_versao` [global]

Singleton version counter; bump invalidates AccessDecision caches platform-wide.

```sql
-- schema: global
CREATE TABLE journeyos_global.modelo_acesso_versao (
    id             INT NOT NULL DEFAULT 1,
    versao         BIGINT NOT NULL DEFAULT 1,
    atualizado_em  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CHECK (id = 1)
);
INSERT INTO journeyos_global.modelo_acesso_versao (id, versao) VALUES (1, 1) ON CONFLICT (id) DO NOTHING;
```

**Invariants:** singleton (`id=1`); `versao` monotonically increasing; bumped in the same transaction as any RBAC mutation (INV-4).

### 3.11 `evento_auditoria` [global]

Consolidated audit trail of all `journey-os.*` events (also indexed in Elastic `audit-events`).

```sql
-- schema: global
CREATE TABLE journeyos_global.evento_auditoria (
    id              BIGSERIAL NOT NULL,
    empresa_id      VARCHAR(50),
    usuario_id      UUID,
    evento          VARCHAR(120) NOT NULL,
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
    correlation_id  UUID,
    source_service  VARCHAR(60) NOT NULL,
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);
CREATE INDEX idx_auditoria_empresa_ts ON journeyos_global.evento_auditoria (empresa_id, timestamp DESC);
CREATE INDEX idx_auditoria_evento ON journeyos_global.evento_auditoria (evento);
```

**Invariants:** append-only; `empresa_id` populated for tenant-scoped events; idempotent on `correlation_id`+`evento` (see SPEC-05/09).

## 4. Relations (ASCII)

```
empresa 1───N business_unit 1───N team 1───N usuario_team N───1 usuario
empresa 1───N usuario_empresa N───1 usuario
papel 1───N usuario_empresa            (via codigo)
papel N───N permissao  (papel_permissao)
modelo_acesso_versao  (singleton)
evento_auditoria      (append-only, FK-free)
```

## 5. Migration plan

| Range | Theme |
|---|---|
| `V0001__iam_papel_permissao.sql` | papel, permissao, papel_permissao + seeds (canonical roles/permissions) |
| `V0002__iam_usuario_empresa.sql` | empresa, usuario, usuario_empresa, modelo_acesso_versao |
| `V0003__iam_org_structure.sql` | business_unit, team, usuario_team |
| `V0004__iam_auditoria.sql` | evento_auditoria |

> Seeds for `papel`/`permissao` come from `rbac.arch.json` / `permission-catalogue.arch.json`
> (canonical roles INFOPRODUTOR/HEAD_GROWTH/SDR). WRKS-owned `wrks.*` permissions are declared
> in `api-contract.md` §error/permission tables and must be added to the catalogue JSON.
