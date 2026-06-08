package com.journeyos.jrny.infrastructure.persistence.repository;

import com.journeyos.jrny.infrastructure.persistence.entity.EstagioJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface EstagioJpaRepository extends JpaRepository<EstagioJpaEntity, UUID> {

    List<EstagioJpaEntity> findByEmpresaId(UUID empresaId);

    // TODO: add domain-specific query methods
}
