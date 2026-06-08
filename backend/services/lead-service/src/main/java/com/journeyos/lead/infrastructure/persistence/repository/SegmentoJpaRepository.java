package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.SegmentoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface SegmentoJpaRepository extends JpaRepository<SegmentoJpaEntity, UUID> {

    List<SegmentoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
