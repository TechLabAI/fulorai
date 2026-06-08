package com.journeyos.asst.infrastructure.persistence.repository;

import com.journeyos.asst.infrastructure.persistence.entity.VersaoAssetJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface VersaoAssetJpaRepository extends JpaRepository<VersaoAssetJpaEntity, UUID> {

    List<VersaoAssetJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
