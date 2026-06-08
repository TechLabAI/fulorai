package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.CitacaoRepositoryPort;
import com.journeyos.intl.domain.model.Citacao;
import com.journeyos.intl.infrastructure.persistence.repository.CitacaoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class CitacaoRepositoryAdapter implements CitacaoRepositoryPort {

    private final CitacaoJpaRepository repository;

    @Override
    public Citacao save(Citacao entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Citacao> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Citacao> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
