package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.EventoIndexadoRepositoryPort;
import com.journeyos.intl.domain.model.EventoIndexado;
import com.journeyos.intl.infrastructure.persistence.repository.EventoIndexadoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class EventoIndexadoRepositoryAdapter implements EventoIndexadoRepositoryPort {

    private final EventoIndexadoJpaRepository repository;

    @Override
    public EventoIndexado save(EventoIndexado entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<EventoIndexado> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<EventoIndexado> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
