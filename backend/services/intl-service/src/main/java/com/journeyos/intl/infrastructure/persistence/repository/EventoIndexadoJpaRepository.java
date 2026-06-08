package com.journeyos.intl.infrastructure.persistence.repository;

import com.journeyos.intl.infrastructure.persistence.entity.EventoIndexadoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface EventoIndexadoJpaRepository extends JpaRepository<EventoIndexadoJpaEntity, UUID> {

    List<EventoIndexadoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
