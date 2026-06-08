package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.PapelJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface PapelJpaRepository extends JpaRepository<PapelJpaEntity, UUID> {

    List<PapelJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
