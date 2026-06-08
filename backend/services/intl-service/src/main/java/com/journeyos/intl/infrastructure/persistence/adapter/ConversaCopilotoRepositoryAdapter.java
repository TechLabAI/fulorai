package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.ConversaCopilotoRepositoryPort;
import com.journeyos.intl.domain.model.ConversaCopiloto;
import com.journeyos.intl.infrastructure.persistence.repository.ConversaCopilotoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ConversaCopilotoRepositoryAdapter implements ConversaCopilotoRepositoryPort {

    private final ConversaCopilotoJpaRepository repository;

    @Override
    public ConversaCopiloto save(ConversaCopiloto entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<ConversaCopiloto> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<ConversaCopiloto> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
