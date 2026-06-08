-- =============================================================================
-- Migration: V1__create_initial_schema.sql
-- Service:   jrny-service
-- Generated: 2026-06-05 by be-migration-generator.py
-- Source:    contracts/data-model.md (extraído de 5 blocos ```sql```)
--
-- ATENÇÃO: este arquivo é GERADO. Para alterar DDL:
--   1. Edite contracts/data-model.md (blocos ```sql```).
--   2. Re-rode: python scripts/be-migration-generator.py <service> --spec-dir <path> --force
-- =============================================================================

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
