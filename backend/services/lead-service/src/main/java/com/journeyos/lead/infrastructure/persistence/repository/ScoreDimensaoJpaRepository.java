package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.ScoreDimensaoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface ScoreDimensaoJpaRepository extends JpaRepository<ScoreDimensaoJpaEntity, UUID> {

    List<ScoreDimensaoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
