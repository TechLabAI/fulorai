package com.journeyos.intl.infrastructure.persistence.repository;

import com.journeyos.intl.infrastructure.persistence.entity.FonteConhecimentoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface FonteConhecimentoJpaRepository extends JpaRepository<FonteConhecimentoJpaEntity, UUID> {

    List<FonteConhecimentoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
