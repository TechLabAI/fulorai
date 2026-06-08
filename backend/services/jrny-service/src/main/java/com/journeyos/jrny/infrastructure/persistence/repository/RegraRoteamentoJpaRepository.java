package com.journeyos.jrny.infrastructure.persistence.repository;

import com.journeyos.jrny.infrastructure.persistence.entity.RegraRoteamentoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface RegraRoteamentoJpaRepository extends JpaRepository<RegraRoteamentoJpaEntity, UUID> {

    List<RegraRoteamentoJpaEntity> findByEmpresaId(UUID empresaId);

    // TODO: add domain-specific query methods
}
