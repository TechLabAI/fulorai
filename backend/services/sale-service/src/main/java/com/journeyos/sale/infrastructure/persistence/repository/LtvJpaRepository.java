package com.journeyos.sale.infrastructure.persistence.repository;

import com.journeyos.sale.infrastructure.persistence.entity.LtvJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface LtvJpaRepository extends JpaRepository<LtvJpaEntity, UUID> {

    List<LtvJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
