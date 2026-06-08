package com.journeyos.intl.infrastructure.persistence.repository;

import com.journeyos.intl.infrastructure.persistence.entity.MensagemCopilotoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface MensagemCopilotoJpaRepository extends JpaRepository<MensagemCopilotoJpaEntity, UUID> {

    List<MensagemCopilotoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
