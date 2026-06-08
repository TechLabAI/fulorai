package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.EventoAuditoriaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface EventoAuditoriaJpaRepository extends JpaRepository<EventoAuditoriaJpaEntity, UUID> {

    List<EventoAuditoriaJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
