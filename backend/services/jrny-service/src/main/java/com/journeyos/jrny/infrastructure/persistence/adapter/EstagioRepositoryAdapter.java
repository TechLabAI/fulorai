package com.journeyos.jrny.infrastructure.persistence.adapter;

import com.journeyos.jrny.application.port.out.EstagioRepositoryPort;
import com.journeyos.jrny.domain.model.Estagio;
import com.journeyos.jrny.infrastructure.persistence.repository.EstagioJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class EstagioRepositoryAdapter implements EstagioRepositoryPort {

    private final EstagioJpaRepository repository;

    @Override
    public Estagio save(Estagio entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Estagio> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Estagio> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
