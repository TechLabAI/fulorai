package com.journeyos.sale.infrastructure.persistence.repository;

import com.journeyos.sale.infrastructure.persistence.entity.OportunidadeJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface OportunidadeJpaRepository extends JpaRepository<OportunidadeJpaEntity, UUID> {

    List<OportunidadeJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
