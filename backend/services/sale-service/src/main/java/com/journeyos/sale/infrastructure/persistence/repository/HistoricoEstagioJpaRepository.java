package com.journeyos.sale.infrastructure.persistence.repository;

import com.journeyos.sale.infrastructure.persistence.entity.HistoricoEstagioJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface HistoricoEstagioJpaRepository extends JpaRepository<HistoricoEstagioJpaEntity, UUID> {

    List<HistoricoEstagioJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
