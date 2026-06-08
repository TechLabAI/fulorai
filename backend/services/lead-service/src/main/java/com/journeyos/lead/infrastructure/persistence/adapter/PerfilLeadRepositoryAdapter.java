package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.PerfilLeadRepositoryPort;
import com.journeyos.lead.domain.model.PerfilLead;
import com.journeyos.lead.infrastructure.persistence.repository.PerfilLeadJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class PerfilLeadRepositoryAdapter implements PerfilLeadRepositoryPort {

    private final PerfilLeadJpaRepository repository;

    @Override
    public PerfilLead save(PerfilLead entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<PerfilLead> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<PerfilLead> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
