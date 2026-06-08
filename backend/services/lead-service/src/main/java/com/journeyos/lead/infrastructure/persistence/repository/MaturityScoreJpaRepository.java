package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.MaturityScoreJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface MaturityScoreJpaRepository extends JpaRepository<MaturityScoreJpaEntity, UUID> {

    List<MaturityScoreJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
