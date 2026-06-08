package com.journeyos.comm.infrastructure.persistence.repository;

import com.journeyos.comm.infrastructure.persistence.entity.TemplateMensagemJpaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.UUID;

public interface TemplateMensagemJpaRepository extends JpaRepository<TemplateMensagemJpaEntity, UUID> {

    List<TemplateMensagemJpaEntity> findByTenantId(String tenantId);

    // TODO: add domain-specific query methods
}
