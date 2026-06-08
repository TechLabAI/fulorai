package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.EmpresaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface EmpresaJpaRepository extends JpaRepository<EmpresaJpaEntity, UUID> {

    List<EmpresaJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
