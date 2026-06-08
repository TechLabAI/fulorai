package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.LeadJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface LeadJpaRepository extends JpaRepository<LeadJpaEntity, UUID> {

    List<LeadJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
