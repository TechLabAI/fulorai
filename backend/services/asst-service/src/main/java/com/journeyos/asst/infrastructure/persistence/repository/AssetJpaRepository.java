package com.journeyos.asst.infrastructure.persistence.repository;

import com.journeyos.asst.infrastructure.persistence.entity.AssetJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface AssetJpaRepository extends JpaRepository<AssetJpaEntity, UUID> {

    List<AssetJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
