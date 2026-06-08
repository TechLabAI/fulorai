package com.journeyos.intl.infrastructure.persistence.repository;

import com.journeyos.intl.infrastructure.persistence.entity.ConversaCopilotoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface ConversaCopilotoJpaRepository extends JpaRepository<ConversaCopilotoJpaEntity, UUID> {

    List<ConversaCopilotoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
