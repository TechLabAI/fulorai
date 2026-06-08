package com.journeyos.jrny.infrastructure.persistence.repository;

import com.journeyos.jrny.infrastructure.persistence.entity.JornadaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface JornadaJpaRepository extends JpaRepository<JornadaJpaEntity, UUID> {

    List<JornadaJpaEntity> findByEmpresaId(UUID empresaId);

    // TODO: add domain-specific query methods
}
