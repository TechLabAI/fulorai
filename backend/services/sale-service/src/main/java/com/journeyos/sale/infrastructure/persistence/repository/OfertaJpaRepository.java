package com.journeyos.sale.infrastructure.persistence.repository;

import com.journeyos.sale.infrastructure.persistence.entity.OfertaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface OfertaJpaRepository extends JpaRepository<OfertaJpaEntity, UUID> {

    List<OfertaJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
