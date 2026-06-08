package com.journeyos.wrks.infrastructure.persistence.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "modelo_acesso_versao")
// Schema resolvido via hibernate.default_schema por profile + TenantContextHolder em runtime
@Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class ModeloAcessoVersaoJpaEntity {

    @Id
    @GeneratedValue
    @Column(name = "modelo_acesso_versao_id")
    private UUID id;

    @Column(name = "tenant_id", nullable = false)
    private String tenantId;

    @Column(name = "status")
    private String status;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt;

    // TODO: complete fields from data-model.md
}
