package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.OfertaRepositoryPort;
import com.journeyos.sale.domain.model.Oferta;
import com.journeyos.sale.infrastructure.persistence.repository.OfertaJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class OfertaRepositoryAdapter implements OfertaRepositoryPort {

    private final OfertaJpaRepository repository;

    @Override
    public Oferta save(Oferta entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Oferta> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Oferta> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
