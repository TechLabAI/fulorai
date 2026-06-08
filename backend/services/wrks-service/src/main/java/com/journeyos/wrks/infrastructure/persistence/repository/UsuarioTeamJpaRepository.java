package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.UsuarioTeamJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface UsuarioTeamJpaRepository extends JpaRepository<UsuarioTeamJpaEntity, UUID> {

    List<UsuarioTeamJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
