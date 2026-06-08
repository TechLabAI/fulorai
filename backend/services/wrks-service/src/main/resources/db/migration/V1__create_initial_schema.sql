-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   wrks-service
-- Generated: 2026-06-04 by be-migration-generator.py
-- Source:    contracts/data-model.md (extraído de 11 blocos ```sql```)
--
-- ATENÇÃO: este arquivo é GERADO. Para alterar DDL:
--   1. Edite contracts/data-model.md (blocos ```sql```).
--   2. Re-rode: python scripts/be-migration-generator.py <service> --spec-dir <path> --force
-- =============================================================================

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

-- schema: global
CREATE TABLE journeyos_global.usuario_team (
    usuario_id  UUID NOT NULL,
    team_id     UUID NOT NULL,
    PRIMARY KEY (usuario_id, team_id),
    FOREIGN KEY (usuario_id) REFERENCES journeyos_global.usuario (usuario_id),
    FOREIGN KEY (team_id)    REFERENCES journeyos_global.team (team_id)
);

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

-- schema: global
CREATE TABLE journeyos_global.papel_permissao (
    papel_id      UUID NOT NULL,
    permissao_id  UUID NOT NULL,
    PRIMARY KEY (papel_id, permissao_id),
    FOREIGN KEY (papel_id)     REFERENCES journeyos_global.papel (papel_id),
    FOREIGN KEY (permissao_id) REFERENCES journeyos_global.permissao (permissao_id)
);

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

-- schema: global
CREATE TABLE journeyos_global.modelo_acesso_versao (
    id             INT NOT NULL DEFAULT 1,
    versao         BIGINT NOT NULL DEFAULT 1,
    atualizado_em  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CHECK (id = 1)
);
INSERT INTO journeyos_global.modelo_acesso_versao (id, versao) VALUES (1, 1) ON CONFLICT (id) DO NOTHING;

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
