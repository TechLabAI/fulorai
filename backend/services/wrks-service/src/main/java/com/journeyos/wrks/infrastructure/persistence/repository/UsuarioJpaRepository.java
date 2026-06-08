package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.UsuarioJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface UsuarioJpaRepository extends JpaRepository<UsuarioJpaEntity, UUID> {

    List<UsuarioJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
