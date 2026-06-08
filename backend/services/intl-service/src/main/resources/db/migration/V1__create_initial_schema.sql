-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   intl-service
-- Generated: 2026-06-05 by be-migration-generator.py
-- Source:    contracts/data-model.md (extraído de 7 blocos ```sql```)
--
-- ATENÇÃO: este arquivo é GERADO. Para alterar DDL:
--   1. Edite contracts/data-model.md (blocos ```sql```).
--   2. Re-rode: python scripts/be-migration-generator.py <service> --spec-dir <path> --force
-- =============================================================================

-- schema: empresa
CREATE TABLE base_conhecimento (
    id              uuid        NOT NULL DEFAULT gen_random_uuid(),
    embedding_modelo varchar(120) NULL,
    total_nos       integer     NOT NULL DEFAULT 0,
    criada_em       timestamptz NOT NULL DEFAULT now(),
    atualizada_em   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);

COMMENT ON TABLE base_conhecimento IS 'Raiz da Base de Conhecimento da empresa (1:1); alimenta o RAG do Copilot.';

-- schema: empresa
CREATE TABLE fonte_conhecimento (
    id          uuid        NOT NULL DEFAULT gen_random_uuid(),
    tipo        varchar(20) NOT NULL,
    referencia  varchar(300) NULL,
    criada_em   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_fonte_tipo CHECK (tipo IN ('MANUAL','ASSET','IMPORT'))
);

CREATE INDEX ix_fonte_tipo ON fonte_conhecimento (tipo);
COMMENT ON TABLE fonte_conhecimento IS 'Proveniência de um nó de conhecimento (MANUAL/ASSET/IMPORT).';

-- schema: empresa
CREATE TABLE no_conhecimento (
    id              uuid         NOT NULL DEFAULT gen_random_uuid(),
    base_id         uuid         NOT NULL,
    fonte_id        uuid         NOT NULL,
    titulo          varchar(300) NOT NULL,
    conteudo        text         NOT NULL,
    tags            text[]       NOT NULL DEFAULT '{}',
    embedding       vector(1536) NULL,
    embedding_modelo varchar(120) NULL,
    status          varchar(20)  NOT NULL DEFAULT 'RASCUNHO',
    versao          integer      NOT NULL DEFAULT 1,
    criado_em       timestamptz  NOT NULL DEFAULT now(),
    atualizado_em   timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_no_status CHECK (status IN ('RASCUNHO','INDEXADO','ARQUIVADO')),
    CONSTRAINT ck_no_versao CHECK (versao >= 1),
    FOREIGN KEY (base_id) REFERENCES base_conhecimento (id) ON DELETE CASCADE,
    FOREIGN KEY (fonte_id) REFERENCES fonte_conhecimento (id) ON DELETE RESTRICT
);

CREATE INDEX ix_no_status ON no_conhecimento (status);
CREATE INDEX ix_no_base ON no_conhecimento (base_id);
COMMENT ON TABLE no_conhecimento IS 'Nó curado de conhecimento; canônico em PG + indexado em Elastic knowledge-nodes.';

-- schema: empresa
CREATE TABLE conversa_copiloto (
    id            uuid         NOT NULL DEFAULT gen_random_uuid(),
    usuario_ref   uuid         NOT NULL,
    titulo        varchar(300) NULL,
    estado        varchar(20)  NOT NULL DEFAULT 'ABERTA',
    criada_em     timestamptz  NOT NULL DEFAULT now(),
    atualizada_em timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_conversa_estado CHECK (estado IN ('ABERTA','PROCESSANDO','RESPONDIDA','DEGRADADA','ERRO'))
);

CREATE INDEX ix_conversa_usuario ON conversa_copiloto (usuario_ref);
COMMENT ON TABLE conversa_copiloto IS 'Sessão conversacional do AI Copilot (por usuário, dentro da empresa).';

-- schema: empresa
CREATE TABLE mensagem_copiloto (
    id            uuid         NOT NULL DEFAULT gen_random_uuid(),
    conversa_id   uuid         NOT NULL,
    ordem         integer      NOT NULL,
    papel         varchar(10)  NOT NULL,
    conteudo      text         NOT NULL,
    status        varchar(20)  NOT NULL DEFAULT 'PENDENTE',
    modelo        varchar(120) NULL,
    custo_tokens  integer      NULL,
    latencia_ms   integer      NULL,
    criada_em     timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT ck_msg_papel CHECK (papel IN ('USUARIO','COPILOTO')),
    CONSTRAINT ck_msg_status CHECK (status IN ('PENDENTE','RESPONDIDA','DEGRADADA','NAO_FUNDAMENTADA','ERRO')),
    CONSTRAINT ck_msg_custo CHECK (custo_tokens IS NULL OR custo_tokens >= 0),
    FOREIGN KEY (conversa_id) REFERENCES conversa_copiloto (id) ON DELETE CASCADE,
    UNIQUE (conversa_id, ordem)
);

CREATE INDEX ix_msg_conversa ON mensagem_copiloto (conversa_id);
COMMENT ON TABLE mensagem_copiloto IS 'Turno da conversa do Copilot (USUARIO=pergunta, COPILOTO=resposta).';

-- schema: empresa
CREATE TABLE citacao (
    id           uuid         NOT NULL DEFAULT gen_random_uuid(),
    mensagem_id  uuid         NOT NULL,
    documento_id varchar(200) NOT NULL,
    indice       varchar(120) NOT NULL,
    trecho       text         NULL,
    score        double precision NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (mensagem_id) REFERENCES mensagem_copiloto (id) ON DELETE CASCADE
);

CREATE INDEX ix_citacao_mensagem ON citacao (mensagem_id);
COMMENT ON TABLE citacao IS 'Citação verificável (documento Elastic) que fundamenta uma resposta do Copilot.';

-- schema: empresa
CREATE TABLE evento_indexado (
    evento_id    varchar(200) NOT NULL,
    tipo         varchar(80)  NOT NULL,
    indice_alvo  varchar(120) NOT NULL,
    status       varchar(10)  NOT NULL,
    indexado_em  timestamptz  NOT NULL DEFAULT now(),
    PRIMARY KEY (evento_id),
    CONSTRAINT ck_evt_status CHECK (status IN ('INDEXADO','DLQ'))
);

CREATE INDEX ix_evt_indice ON evento_indexado (indice_alvo);
COMMENT ON TABLE evento_indexado IS 'Ledger append-only das projeções Elastic de INTL (idempotência/auditoria/replay).';
