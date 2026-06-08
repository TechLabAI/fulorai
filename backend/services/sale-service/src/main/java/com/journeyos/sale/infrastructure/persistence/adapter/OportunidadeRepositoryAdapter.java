package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.OportunidadeRepositoryPort;
import com.journeyos.sale.domain.model.Oportunidade;
import com.journeyos.sale.infrastructure.persistence.repository.OportunidadeJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class OportunidadeRepositoryAdapter implements OportunidadeRepositoryPort {

    private final OportunidadeJpaRepository repository;

    @Override
    public Oportunidade save(Oportunidade entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Oportunidade> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Oportunidade> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
