package com.journeyos.jrny.infrastructure.persistence.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.*;

/**
 * JPA mapping for table {@code jornada} (schema {@code emp_<slug>}).
 * Columns mirror V1__create_initial_schema.sql exactly (ddl-auto=validate).
 * Aggregate root: versioned funnel definition; {@code estadoJornada} drives the
 * publication state machine (ADR-005). Schema resolved at runtime via the
 * hibernate multi-tenancy provider (TenantContextHolder).
 */
@Entity
@Table(name = "jornada")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class JornadaJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    /** Tenant guard (redundant to schema isolation) = EmpresaContextHolder.require(). */
    @Column(name = "empresa_id", nullable = false)
    private UUID empresaId;

    @Column(name = "nome", nullable = false, length = 180)
    private String nome;

    @Column(name = "descricao", columnDefinition = "text")
    private String descricao;

    /** RASCUNHO | PUBLICADA | ARQUIVADA (CHECK constraint in DDL). */
    @Column(name = "estado_jornada", nullable = false, length = 20)
    private String estadoJornada;

    @Column(name = "versao", nullable = false)
    private Integer versao;

    @Column(name = "criado_por", nullable = false)
    private UUID criadoPor;

    @Column(name = "criado_em", nullable = false)
    private OffsetDateTime criadoEm;

    @Column(name = "atualizado_em")
    private OffsetDateTime atualizadoEm;
}
