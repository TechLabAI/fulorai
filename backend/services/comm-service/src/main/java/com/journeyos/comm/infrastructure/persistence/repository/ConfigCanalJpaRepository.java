package com.journeyos.comm.infrastructure.persistence.repository;

import com.journeyos.comm.infrastructure.persistence.entity.ConfigCanalJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface ConfigCanalJpaRepository extends JpaRepository<ConfigCanalJpaEntity, UUID> {

    List<ConfigCanalJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
