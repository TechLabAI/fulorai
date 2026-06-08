package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.TeamJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface TeamJpaRepository extends JpaRepository<TeamJpaEntity, UUID> {

    List<TeamJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
