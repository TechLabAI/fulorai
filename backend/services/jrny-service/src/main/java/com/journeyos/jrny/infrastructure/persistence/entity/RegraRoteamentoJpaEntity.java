package com.journeyos.jrny.infrastructure.persistence.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

/**
 * JPA mapping for table {@code regra_roteamento} (schema {@code emp_<slug>}).
 * Columns mirror V1__create_initial_schema.sql exactly (ddl-auto=validate).
 * Versioned routing rule; {@code condicao} is a deterministic JSONB predicate
 * over the lead qualification snapshot; lower {@code prioridade} wins (ADR-005).
 */
@Entity
@Table(name = "regra_roteamento")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class RegraRoteamentoJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    @Column(name = "empresa_id", nullable = false)
    private UUID empresaId;

    @Column(name = "jornada_id", nullable = false)
    private UUID jornadaId;

    /** NULL = entry rule (enrolment); non-null = jump rule from a given stage. */
    @Column(name = "estagio_origem_id")
    private UUID estagioOrigemId;

    @Column(name = "estagio_destino_id", nullable = false)
    private UUID estagioDestinoId;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "condicao", nullable = false)
    private String condicao;

    @Column(name = "prioridade", nullable = false)
    private Integer prioridade;

    @Column(name = "versao", nullable = false)
    private Integer versao;

    @Column(name = "ativa", nullable = false)
    private boolean ativa;

    @Column(name = "criado_por", nullable = false)
    private UUID criadoPor;

    @Column(name = "criado_em", nullable = false)
    private OffsetDateTime criadoEm;

    @Column(name = "atualizado_em")
    private OffsetDateTime atualizadoEm;
}
