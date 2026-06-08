package com.journeyos.sale.infrastructure.persistence.repository;

import com.journeyos.sale.infrastructure.persistence.entity.AtribuicaoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface AtribuicaoJpaRepository extends JpaRepository<AtribuicaoJpaEntity, UUID> {

    List<AtribuicaoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
