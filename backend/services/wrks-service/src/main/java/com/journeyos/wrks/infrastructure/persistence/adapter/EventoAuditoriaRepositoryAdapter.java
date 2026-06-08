package com.journeyos.wrks.infrastructure.persistence.adapter;

import com.journeyos.wrks.application.port.out.EventoAuditoriaRepositoryPort;
import com.journeyos.wrks.domain.model.EventoAuditoria;
import com.journeyos.wrks.infrastructure.persistence.repository.EventoAuditoriaJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class EventoAuditoriaRepositoryAdapter implements EventoAuditoriaRepositoryPort {

    private final EventoAuditoriaJpaRepository repository;

    @Override
    public EventoAuditoria save(EventoAuditoria entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<EventoAuditoria> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<EventoAuditoria> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
