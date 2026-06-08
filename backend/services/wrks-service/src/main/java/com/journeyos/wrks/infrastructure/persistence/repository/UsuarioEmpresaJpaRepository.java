package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.UsuarioEmpresaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface UsuarioEmpresaJpaRepository extends JpaRepository<UsuarioEmpresaJpaEntity, UUID> {

    List<UsuarioEmpresaJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
