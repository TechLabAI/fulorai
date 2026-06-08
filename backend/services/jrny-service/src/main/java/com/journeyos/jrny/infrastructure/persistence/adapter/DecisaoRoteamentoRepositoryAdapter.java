package com.journeyos.jrny.infrastructure.persistence.adapter;

import com.journeyos.jrny.application.port.out.DecisaoRoteamentoRepositoryPort;
import com.journeyos.jrny.domain.model.DecisaoRoteamento;
import com.journeyos.jrny.infrastructure.persistence.repository.DecisaoRoteamentoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class DecisaoRoteamentoRepositoryAdapter implements DecisaoRoteamentoRepositoryPort {

    private final DecisaoRoteamentoJpaRepository repository;

    @Override
    public DecisaoRoteamento save(DecisaoRoteamento entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<DecisaoRoteamento> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<DecisaoRoteamento> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
