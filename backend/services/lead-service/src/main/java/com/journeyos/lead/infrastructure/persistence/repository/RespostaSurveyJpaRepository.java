package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.RespostaSurveyJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface RespostaSurveyJpaRepository extends JpaRepository<RespostaSurveyJpaEntity, UUID> {

    List<RespostaSurveyJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
