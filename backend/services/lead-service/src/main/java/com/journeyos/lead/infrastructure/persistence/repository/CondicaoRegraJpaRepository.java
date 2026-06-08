package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.CondicaoRegraJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface CondicaoRegraJpaRepository extends JpaRepository<CondicaoRegraJpaEntity, UUID> {

    List<CondicaoRegraJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
