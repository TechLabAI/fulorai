package com.journeyos.asst.infrastructure.persistence.repository;

import com.journeyos.asst.infrastructure.persistence.entity.TagAssetJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface TagAssetJpaRepository extends JpaRepository<TagAssetJpaEntity, UUID> {

    List<TagAssetJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
