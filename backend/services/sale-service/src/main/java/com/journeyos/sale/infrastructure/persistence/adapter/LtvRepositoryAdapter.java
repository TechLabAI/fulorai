package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.LtvRepositoryPort;
import com.journeyos.sale.domain.model.Ltv;
import com.journeyos.sale.infrastructure.persistence.repository.LtvJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class LtvRepositoryAdapter implements LtvRepositoryPort {

    private final LtvJpaRepository repository;

    @Override
    public Ltv save(Ltv entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Ltv> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Ltv> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
