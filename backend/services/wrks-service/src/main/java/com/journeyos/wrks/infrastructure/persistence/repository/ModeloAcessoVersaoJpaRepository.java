package com.journeyos.wrks.infrastructure.persistence.repository;

import com.journeyos.wrks.infrastructure.persistence.entity.ModeloAcessoVersaoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface ModeloAcessoVersaoJpaRepository extends JpaRepository<ModeloAcessoVersaoJpaEntity, UUID> {

    List<ModeloAcessoVersaoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
