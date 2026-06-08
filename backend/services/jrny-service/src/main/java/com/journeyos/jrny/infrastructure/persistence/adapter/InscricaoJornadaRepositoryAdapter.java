package com.journeyos.jrny.infrastructure.persistence.adapter;

import com.journeyos.jrny.application.port.out.InscricaoJornadaRepositoryPort;
import com.journeyos.jrny.domain.model.InscricaoJornada;
import com.journeyos.jrny.infrastructure.persistence.repository.InscricaoJornadaJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class InscricaoJornadaRepositoryAdapter implements InscricaoJornadaRepositoryPort {

    private final InscricaoJornadaJpaRepository repository;

    @Override
    public InscricaoJornada save(InscricaoJornada entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<InscricaoJornada> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<InscricaoJornada> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
