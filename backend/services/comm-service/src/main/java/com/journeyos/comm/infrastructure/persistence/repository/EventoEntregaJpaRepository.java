package com.journeyos.comm.infrastructure.persistence.repository;

import com.journeyos.comm.infrastructure.persistence.entity.EventoEntregaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface EventoEntregaJpaRepository extends JpaRepository<EventoEntregaJpaEntity, UUID> {

    List<EventoEntregaJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
