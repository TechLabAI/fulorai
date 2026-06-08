package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.PapelPermissaoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface PapelPermissaoJpaRepository extends JpaRepository<PapelPermissaoJpaEntity, UUID> {

    List<PapelPermissaoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
