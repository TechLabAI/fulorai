package com.journeyos.intl.infrastructure.persistence.repository;

import com.journeyos.intl.infrastructure.persistence.entity.CitacaoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface CitacaoJpaRepository extends JpaRepository<CitacaoJpaEntity, UUID> {

    List<CitacaoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
