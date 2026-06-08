-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   asst-service
-- Generated: 2026-06-04 by be-migration-generator.py
-- Source:    contracts/data-model.md (extraído de 4 blocos ```sql```)
--
-- ATENÇÃO: este arquivo é GERADO. Para alterar DDL:
--   1. Edite contracts/data-model.md (blocos ```sql```).
--   2. Re-rode: python scripts/be-migration-generator.py <service> --spec-dir <path> --force
-- =============================================================================

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
