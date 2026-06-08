package com.journeyos.comm.infrastructure.persistence.adapter;

import com.journeyos.comm.application.port.out.EventoEntregaRepositoryPort;
import com.journeyos.comm.domain.model.EventoEntrega;
import com.journeyos.comm.infrastructure.persistence.repository.EventoEntregaJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class EventoEntregaRepositoryAdapter implements EventoEntregaRepositoryPort {

    private final EventoEntregaJpaRepository repository;

    @Override
    public EventoEntrega save(EventoEntrega entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<EventoEntrega> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<EventoEntrega> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
