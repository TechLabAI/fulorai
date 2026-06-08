package com.journeyos.jrny.infrastructure.persistence.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.*;

/**
 * JPA mapping for table {@code inscricao_jornada} (schema {@code emp_<slug>}).
 * Columns mirror V1__create_initial_schema.sql exactly (ddl-auto=validate).
 * Lead execution state in a journey; pins {@code jornadaVersao} at entry so
 * active enrolments are immune to new journey versions (ADR-005).
 */
@Entity
@Table(name = "inscricao_jornada")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class InscricaoJornadaJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    @Column(name = "empresa_id", nullable = false)
    private UUID empresaId;

    @Column(name = "lead_id", nullable = false)
    private UUID leadId;

    @Column(name = "jornada_id", nullable = false)
    private UUID jornadaId;

    @Column(name = "jornada_versao", nullable = false)
    private Integer jornadaVersao;

    @Column(name = "estagio_corrente_id", nullable = false)
    private UUID estagioCorrenteId;

    /** ATIVA | CONCLUIDA | ENCERRADA (CHECK constraint in DDL). */
    @Column(name = "estado", nullable = false, length = 20)
    private String estado;

    @Column(name = "entrou_em", nullable = false)
    private OffsetDateTime entrouEm;

    @Column(name = "atualizado_em")
    private OffsetDateTime atualizadoEm;
}
