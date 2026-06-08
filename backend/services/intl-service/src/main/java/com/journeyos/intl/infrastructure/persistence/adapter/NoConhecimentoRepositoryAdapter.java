package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.NoConhecimentoRepositoryPort;
import com.journeyos.intl.domain.model.NoConhecimento;
import com.journeyos.intl.infrastructure.persistence.repository.NoConhecimentoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class NoConhecimentoRepositoryAdapter implements NoConhecimentoRepositoryPort {

    private final NoConhecimentoJpaRepository repository;

    @Override
    public NoConhecimento save(NoConhecimento entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<NoConhecimento> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<NoConhecimento> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
