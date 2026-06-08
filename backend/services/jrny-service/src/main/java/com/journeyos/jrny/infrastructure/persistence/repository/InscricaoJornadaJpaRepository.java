package com.journeyos.jrny.infrastructure.persistence.repository;

import com.journeyos.jrny.infrastructure.persistence.entity.InscricaoJornadaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface InscricaoJornadaJpaRepository extends JpaRepository<InscricaoJornadaJpaEntity, UUID> {

    List<InscricaoJornadaJpaEntity> findByEmpresaId(UUID empresaId);

    // TODO: add domain-specific query methods
}
