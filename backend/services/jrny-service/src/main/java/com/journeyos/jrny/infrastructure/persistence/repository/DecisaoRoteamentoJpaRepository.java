package com.journeyos.jrny.infrastructure.persistence.repository;

import com.journeyos.jrny.infrastructure.persistence.entity.DecisaoRoteamentoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface DecisaoRoteamentoJpaRepository extends JpaRepository<DecisaoRoteamentoJpaEntity, UUID> {

    List<DecisaoRoteamentoJpaEntity> findByEmpresaId(UUID empresaId);

    // TODO: add domain-specific query methods
}
