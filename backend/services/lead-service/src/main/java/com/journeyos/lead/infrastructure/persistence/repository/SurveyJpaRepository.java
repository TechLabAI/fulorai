package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.SurveyJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface SurveyJpaRepository extends JpaRepository<SurveyJpaEntity, UUID> {

    List<SurveyJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
