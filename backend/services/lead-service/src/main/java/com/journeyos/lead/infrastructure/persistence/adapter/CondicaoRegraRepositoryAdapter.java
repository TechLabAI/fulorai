package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.CondicaoRegraRepositoryPort;
import com.journeyos.lead.domain.model.CondicaoRegra;
import com.journeyos.lead.infrastructure.persistence.repository.CondicaoRegraJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class CondicaoRegraRepositoryAdapter implements CondicaoRegraRepositoryPort {

    private final CondicaoRegraJpaRepository repository;

    @Override
    public CondicaoRegra save(CondicaoRegra entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<CondicaoRegra> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<CondicaoRegra> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
