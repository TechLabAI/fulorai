package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.LeadRepositoryPort;
import com.journeyos.lead.domain.model.Lead;
import com.journeyos.lead.infrastructure.persistence.repository.LeadJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class LeadRepositoryAdapter implements LeadRepositoryPort {

    private final LeadJpaRepository repository;

    @Override
    public Lead save(Lead entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Lead> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Lead> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
