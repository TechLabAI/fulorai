package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.RegraQualificacaoJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface RegraQualificacaoJpaRepository extends JpaRepository<RegraQualificacaoJpaEntity, UUID> {

    List<RegraQualificacaoJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
