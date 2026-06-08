-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   sale-service
-- Generated: 2026-06-05 by be-migration-generator.py
-- Source:    contracts/data-model.md (extraído de 9 blocos ```sql```)
--
-- ATENÇÃO: este arquivo é GERADO. Para alterar DDL:
--   1. Edite contracts/data-model.md (blocos ```sql```).
--   2. Re-rode: python scripts/be-migration-generator.py <service> --spec-dir <path> --force
-- =============================================================================

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
