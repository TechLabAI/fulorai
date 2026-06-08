-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   comm-service
-- Generated: 2026-06-05 by be-migration-generator.py
-- Source:    contracts/data-model.md (extraído de 5 blocos ```sql```)
--
-- ATENÇÃO: este arquivo é GERADO. Para alterar DDL:
--   1. Edite contracts/data-model.md (blocos ```sql```).
--   2. Re-rode: python scripts/be-migration-generator.py <service> --spec-dir <path> --force
-- =============================================================================

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
