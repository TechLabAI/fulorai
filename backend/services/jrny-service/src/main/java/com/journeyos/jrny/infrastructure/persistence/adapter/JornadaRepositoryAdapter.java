package com.journeyos.jrny.infrastructure.persistence.adapter;

import com.journeyos.jrny.application.port.out.JornadaRepositoryPort;
import com.journeyos.jrny.domain.model.Jornada;
import com.journeyos.jrny.infrastructure.persistence.repository.JornadaJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class JornadaRepositoryAdapter implements JornadaRepositoryPort {

    private final JornadaJpaRepository repository;

    @Override
    public Jornada save(Jornada entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Jornada> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Jornada> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
