package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.PerfilLeadJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface PerfilLeadJpaRepository extends JpaRepository<PerfilLeadJpaEntity, UUID> {

    List<PerfilLeadJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
