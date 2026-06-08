package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.AtributoPerfilJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface AtributoPerfilJpaRepository extends JpaRepository<AtributoPerfilJpaEntity, UUID> {

    List<AtributoPerfilJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
