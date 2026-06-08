package com.journeyos.intl.infrastructure.persistence.repository;

import com.journeyos.intl.infrastructure.persistence.entity.BaseConhecimentoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface BaseConhecimentoJpaRepository extends JpaRepository<BaseConhecimentoJpaEntity, UUID> {

    List<BaseConhecimentoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
