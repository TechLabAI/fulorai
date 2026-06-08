package com.journeyos.intl.infrastructure.persistence.repository;

import com.journeyos.intl.infrastructure.persistence.entity.NoConhecimentoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface NoConhecimentoJpaRepository extends JpaRepository<NoConhecimentoJpaEntity, UUID> {

    List<NoConhecimentoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
