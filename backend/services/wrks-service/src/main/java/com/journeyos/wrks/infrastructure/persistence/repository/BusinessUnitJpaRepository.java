package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.BusinessUnitJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface BusinessUnitJpaRepository extends JpaRepository<BusinessUnitJpaEntity, UUID> {

    List<BusinessUnitJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
