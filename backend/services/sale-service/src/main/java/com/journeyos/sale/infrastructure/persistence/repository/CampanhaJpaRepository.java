package com.journeyos.sale.infrastructure.persistence.repository;

import com.journeyos.sale.infrastructure.persistence.entity.CampanhaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface CampanhaJpaRepository extends JpaRepository<CampanhaJpaEntity, UUID> {

    List<CampanhaJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
