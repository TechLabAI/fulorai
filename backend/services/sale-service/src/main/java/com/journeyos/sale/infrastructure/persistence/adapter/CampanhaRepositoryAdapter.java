package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.CampanhaRepositoryPort;
import com.journeyos.sale.domain.model.Campanha;
import com.journeyos.sale.infrastructure.persistence.repository.CampanhaJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class CampanhaRepositoryAdapter implements CampanhaRepositoryPort {

    private final CampanhaJpaRepository repository;

    @Override
    public Campanha save(Campanha entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Campanha> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Campanha> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
