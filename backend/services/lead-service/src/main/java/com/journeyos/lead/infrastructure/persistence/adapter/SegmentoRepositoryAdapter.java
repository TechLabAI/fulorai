package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.SegmentoRepositoryPort;
import com.journeyos.lead.domain.model.Segmento;
import com.journeyos.lead.infrastructure.persistence.repository.SegmentoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class SegmentoRepositoryAdapter implements SegmentoRepositoryPort {

    private final SegmentoJpaRepository repository;

    @Override
    public Segmento save(Segmento entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Segmento> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Segmento> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
