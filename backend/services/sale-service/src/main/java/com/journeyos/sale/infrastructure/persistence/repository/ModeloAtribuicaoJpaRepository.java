package com.journeyos.sale.infrastructure.persistence.repository;

import com.journeyos.sale.infrastructure.persistence.entity.ModeloAtribuicaoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface ModeloAtribuicaoJpaRepository extends JpaRepository<ModeloAtribuicaoJpaEntity, UUID> {

    List<ModeloAtribuicaoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
