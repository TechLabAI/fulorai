package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.LeadSegmentoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface LeadSegmentoJpaRepository extends JpaRepository<LeadSegmentoJpaEntity, UUID> {

    List<LeadSegmentoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
