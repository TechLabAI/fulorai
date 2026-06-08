-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   lead-service
-- Generated: 2026-06-04 by be-migration-generator.py
-- Source:    contracts/data-model.md (extraído de 12 blocos ```sql```)
--
-- ATENÇÃO: este arquivo é GERADO. Para alterar DDL:
--   1. Edite contracts/data-model.md (blocos ```sql```).
--   2. Re-rode: python scripts/be-migration-generator.py <service> --spec-dir <path> --force
-- =============================================================================

-- schema: empresa
CREATE TABLE lead (
    lead_id              UUID NOT NULL DEFAULT gen_random_uuid(),
    chave_natural        VARCHAR(255) NOT NULL,
    nome                 VARCHAR(200),
    email                VARCHAR(255),
    telefone             VARCHAR(40),
    fonte                VARCHAR(60) NOT NULL,
    estado_qualificacao  VARCHAR(20) NOT NULL DEFAULT 'NOVO',
    base_legal           VARCHAR(40) NOT NULL,
    consentimento_em     TIMESTAMPTZ,
    criado_em            TIMESTAMPTZ NOT NULL DEFAULT now(),
    atualizado_em        TIMESTAMPTZ,
    PRIMARY KEY (lead_id),
    UNIQUE (chave_natural),
    CHECK (estado_qualificacao IN ('NOVO','EM_QUALIFICACAO','QUALIFICADO','NAO_QUALIFICADO','DESCARTADO','ANONIMIZADO')),
    CHECK (base_legal IN ('CONSENTIMENTO','LEGITIMO_INTERESSE','EXECUCAO_CONTRATO','OBRIGACAO_LEGAL'))
);
CREATE INDEX idx_lead_estado ON lead (estado_qualificacao);
CREATE INDEX idx_lead_fonte ON lead (fonte);
COMMENT ON TABLE lead IS 'Lead aggregate root; unique per empresa by chave_natural (dedup)';
COMMENT ON COLUMN lead.chave_natural IS 'Normalized dedup key: lower(email) and/or digits(telefone) + fonte';

-- schema: empresa
CREATE TABLE perfil_lead (
    lead_id        UUID NOT NULL,
    cargo          VARCHAR(120),
    segmento_mercado VARCHAR(120),
    faturamento_faixa VARCHAR(40),
    tamanho_equipe VARCHAR(40),
    canais         JSONB NOT NULL DEFAULT '{}'::jsonb,
    consolidado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (lead_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE
);
COMMENT ON TABLE perfil_lead IS 'Denormalized profile snapshot derived from atributo_perfil';

-- schema: empresa
CREATE TABLE atributo_perfil (
    atributo_id   UUID NOT NULL DEFAULT gen_random_uuid(),
    lead_id       UUID NOT NULL,
    chave         VARCHAR(80) NOT NULL,
    valor         TEXT,
    tipo          VARCHAR(20) NOT NULL DEFAULT 'TEXTO',
    origem        VARCHAR(20) NOT NULL,
    registrado_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (atributo_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE,
    CHECK (tipo IN ('TEXTO','NUMERO','BOOLEANO','DATA','ENUM')),
    CHECK (origem IN ('FORM','SURVEY','INTEGRACAO','ASSIST_IA','MANUAL'))
);
CREATE INDEX idx_atributo_lead ON atributo_perfil (lead_id);
CREATE UNIQUE INDEX uq_atributo_lead_chave ON atributo_perfil (lead_id, chave);

-- schema: empresa
CREATE TABLE survey (
    survey_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    nome       VARCHAR(150) NOT NULL,
    versao     INT NOT NULL DEFAULT 1,
    ativo      BOOLEAN NOT NULL DEFAULT true,
    criado_em  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (survey_id),
    UNIQUE (nome, versao)
);

-- schema: empresa
CREATE TABLE pergunta (
    pergunta_id   UUID NOT NULL DEFAULT gen_random_uuid(),
    survey_id     UUID NOT NULL,
    ordem         SMALLINT NOT NULL DEFAULT 0,
    enunciado     TEXT NOT NULL,
    tipo          VARCHAR(20) NOT NULL DEFAULT 'TEXTO',
    dimensao_alvo VARCHAR(20),
    PRIMARY KEY (pergunta_id),
    FOREIGN KEY (survey_id) REFERENCES survey (survey_id) ON DELETE CASCADE,
    CHECK (tipo IN ('TEXTO','NUMERO','BOOLEANO','ESCOLHA','ESCALA')),
    CHECK (dimensao_alvo IS NULL OR dimensao_alvo IN ('PERFIL','ENGAJAMENTO','INTENCAO','CAPACIDADE','URGENCIA','ADERENCIA'))
);
CREATE INDEX idx_pergunta_survey ON pergunta (survey_id);

-- schema: empresa
CREATE TABLE resposta_survey (
    resposta_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    lead_id      UUID NOT NULL,
    pergunta_id  UUID NOT NULL,
    valor        TEXT,
    respondido_em TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (resposta_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE,
    FOREIGN KEY (pergunta_id) REFERENCES pergunta (pergunta_id),
    UNIQUE (lead_id, pergunta_id)
);
CREATE INDEX idx_resposta_lead ON resposta_survey (lead_id);

-- schema: empresa
CREATE TABLE regra_qualificacao (
    regra_id    UUID NOT NULL DEFAULT gen_random_uuid(),
    versao      INT NOT NULL,
    nome        VARCHAR(150) NOT NULL,
    ativo       BOOLEAN NOT NULL DEFAULT false,
    limiar_qualificado SMALLINT NOT NULL DEFAULT 60,
    vigente_de  TIMESTAMPTZ,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (regra_id),
    UNIQUE (versao),
    CHECK (limiar_qualificado BETWEEN 0 AND 100)
);
CREATE UNIQUE INDEX uq_regra_ativa ON regra_qualificacao (ativo) WHERE ativo = true;
COMMENT ON TABLE regra_qualificacao IS 'Versioned qualification rule set; exactly one active at a time';

-- schema: empresa
CREATE TABLE condicao_regra (
    condicao_id  UUID NOT NULL DEFAULT gen_random_uuid(),
    regra_id     UUID NOT NULL,
    sinal        VARCHAR(80) NOT NULL,
    operador     VARCHAR(10) NOT NULL,
    valor_ref    TEXT,
    dimensao     VARCHAR(20) NOT NULL,
    peso         SMALLINT NOT NULL,
    PRIMARY KEY (condicao_id),
    FOREIGN KEY (regra_id) REFERENCES regra_qualificacao (regra_id) ON DELETE CASCADE,
    CHECK (operador IN ('EQ','NEQ','GT','GTE','LT','LTE','IN','EXISTS')),
    CHECK (dimensao IN ('PERFIL','ENGAJAMENTO','INTENCAO','CAPACIDADE','URGENCIA','ADERENCIA')),
    CHECK (peso BETWEEN -100 AND 100)
);
CREATE INDEX idx_condicao_regra ON condicao_regra (regra_id);

-- schema: empresa
CREATE TABLE maturity_score (
    maturity_score_id UUID NOT NULL DEFAULT gen_random_uuid(),
    lead_id        UUID NOT NULL,
    valor_agregado SMALLINT NOT NULL,
    versao_regra   INT NOT NULL,
    hash_sinais    VARCHAR(64) NOT NULL,
    assist_ia      BOOLEAN NOT NULL DEFAULT false,
    calculado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (maturity_score_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE,
    UNIQUE (lead_id),
    CHECK (valor_agregado BETWEEN 0 AND 100)
);
CREATE INDEX idx_score_versao ON maturity_score (versao_regra);
COMMENT ON COLUMN maturity_score.hash_sinais IS 'Hash of the signal set used; with lead_id+versao_regra forms the idempotency key (SPEC-05)';

-- schema: empresa
CREATE TABLE score_dimensao (
    maturity_score_id UUID NOT NULL,
    dimensao      VARCHAR(20) NOT NULL,
    valor         SMALLINT NOT NULL,
    contribuintes JSONB NOT NULL DEFAULT '[]'::jsonb,
    PRIMARY KEY (maturity_score_id, dimensao),
    FOREIGN KEY (maturity_score_id) REFERENCES maturity_score (maturity_score_id) ON DELETE CASCADE,
    CHECK (dimensao IN ('PERFIL','ENGAJAMENTO','INTENCAO','CAPACIDADE','URGENCIA','ADERENCIA')),
    CHECK (valor BETWEEN 0 AND 100)
);

-- schema: empresa
CREATE TABLE segmento (
    segmento_id UUID NOT NULL DEFAULT gen_random_uuid(),
    nome        VARCHAR(120) NOT NULL,
    predicado   JSONB NOT NULL DEFAULT '{}'::jsonb,
    ativo       BOOLEAN NOT NULL DEFAULT true,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (segmento_id),
    UNIQUE (nome)
);
COMMENT ON COLUMN segmento.predicado IS 'JSON predicate over perfil+score evaluated by SegmentEvaluator';

-- schema: empresa
CREATE TABLE lead_segmento (
    lead_id     UUID NOT NULL,
    segmento_id UUID NOT NULL,
    entrou_em   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (lead_id, segmento_id),
    FOREIGN KEY (lead_id) REFERENCES lead (lead_id) ON DELETE CASCADE,
    FOREIGN KEY (segmento_id) REFERENCES segmento (segmento_id) ON DELETE CASCADE
);
CREATE INDEX idx_lead_segmento_seg ON lead_segmento (segmento_id);
