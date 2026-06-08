package com.journeyos.jrny.infrastructure.persistence.entity;

import jakarta.persistence.*;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

/**
 * JPA mapping for table {@code estagio} (schema {@code emp_<slug>}).
 * Columns mirror V1__create_initial_schema.sql exactly (ddl-auto=validate).
 * Ordered, typed stage within a journey; {@code assetRefId} is a logical
 * reference to a published ASST asset (no physical FK).
 */
@Entity
@Table(name = "estagio")
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class EstagioJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", nullable = false, updatable = false)
    private UUID id;

    @Column(name = "empresa_id", nullable = false)
    private UUID empresaId;

    @Column(name = "jornada_id", nullable = false)
    private UUID jornadaId;

    @Column(name = "ordem", nullable = false)
    private Integer ordem;

    /** CAPTURA | NUTRICAO | QUALIFICACAO | OFERTA | FECHAMENTO | POS_VENDA (CHECK in DDL). */
    @Column(name = "tipo_estagio", nullable = false, length = 20)
    private String tipoEstagio;

    @Column(name = "nome", nullable = false, length = 180)
    private String nome;

    /** Logical ref to ASST published asset; refreshed on journey-os.asset.versao.publicada. */
    @Column(name = "asset_ref_id")
    private UUID assetRefId;

    /** Marks a final stage; reaching it concludes the inscricao. */
    @Column(name = "terminal", nullable = false)
    private boolean terminal;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "config", nullable = false)
    private String config;

    @Column(name = "criado_em", nullable = false)
    private OffsetDateTime criadoEm;

    @Column(name = "atualizado_em")
    private OffsetDateTime atualizadoEm;
}
