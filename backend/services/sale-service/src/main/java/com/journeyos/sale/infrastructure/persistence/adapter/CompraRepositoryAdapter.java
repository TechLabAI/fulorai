package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.CompraRepositoryPort;
import com.journeyos.sale.domain.model.Compra;
import com.journeyos.sale.infrastructure.persistence.repository.CompraJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class CompraRepositoryAdapter implements CompraRepositoryPort {

    private final CompraJpaRepository repository;

    @Override
    public Compra save(Compra entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Compra> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Compra> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
