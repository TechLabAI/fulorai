package com.journeyos.lead.infrastructure.persistence.repository;

import com.journeyos.lead.infrastructure.persistence.entity.PerguntaJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface PerguntaJpaRepository extends JpaRepository<PerguntaJpaEntity, UUID> {

    List<PerguntaJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
