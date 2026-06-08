package com.journeyos.jrny.infrastructure.persistence.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

/**
 * JPA mapping for table {@code decisao_roteamento} (schema {@code emp_<slug>}).
 * Columns mirror V1__create_initial_schema.sql exactly (ddl-auto=validate).
 * IMMUTABLE decision log (write-once): the auditable "why" of every routing
 * decision. No UPDATE/DELETE in the domain (ADR-005) — hence {@code @Column(updatable=false)}.
 */
@Entity
@Table(name = "decisao_roteamento")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class DecisaoRoteamentoJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    @Column(name = "empresa_id", nullable = false, updatable = false)
    private UUID empresaId;

    @Column(name = "lead_id", nullable = false, updatable = false)
    private UUID leadId;

    @Column(name = "inscricao_id", updatable = false)
    private UUID inscricaoId;

    @Column(name = "jornada_id", updatable = false)
    private UUID jornadaId;

    /** Origin event of the decision (e.g. lead.qualificado, lead.score.atualizado). */
    @Column(name = "gatilho", nullable = false, updatable = false, length = 60)
    private String gatilho;

    /** Score/dimensoes/segmento/atributos at decision time — provenance of the decision. */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "snapshot_entrada", nullable = false, updatable = false)
    private String snapshotEntrada;

    @Column(name = "regra_id", updatable = false)
    private UUID regraId;

    /** USADO | IGNORADO | INDISPONIVEL (CHECK constraint in DDL). */
    @Column(name = "assist_ia", nullable = false, updatable = false, length = 20)
    private String assistIa;

    /** ROTEADO | SEM_MUDANCA | NAO_ROTEADO (CHECK constraint in DDL). */
    @Column(name = "resultado", nullable = false, updatable = false, length = 20)
    private String resultado;

    @Column(name = "estagio_alvo_id", updatable = false)
    private UUID estagioAlvoId;

    @Column(name = "motivo", nullable = false, updatable = false, columnDefinition = "text")
    private String motivo;

    @Column(name = "decidido_em", nullable = false, updatable = false)
    private OffsetDateTime decididoEm;
}
