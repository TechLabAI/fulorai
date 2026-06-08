package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.HistoricoEstagioRepositoryPort;
import com.journeyos.sale.domain.model.HistoricoEstagio;
import com.journeyos.sale.infrastructure.persistence.repository.HistoricoEstagioJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class HistoricoEstagioRepositoryAdapter implements HistoricoEstagioRepositoryPort {

    private final HistoricoEstagioJpaRepository repository;

    @Override
    public HistoricoEstagio save(HistoricoEstagio entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<HistoricoEstagio> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<HistoricoEstagio> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
