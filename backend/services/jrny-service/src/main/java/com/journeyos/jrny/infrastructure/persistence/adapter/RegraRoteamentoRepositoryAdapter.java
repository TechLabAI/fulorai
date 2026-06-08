package com.journeyos.jrny.infrastructure.persistence.adapter;

import com.journeyos.jrny.application.port.out.RegraRoteamentoRepositoryPort;
import com.journeyos.jrny.domain.model.RegraRoteamento;
import com.journeyos.jrny.infrastructure.persistence.repository.RegraRoteamentoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class RegraRoteamentoRepositoryAdapter implements RegraRoteamentoRepositoryPort {

    private final RegraRoteamentoJpaRepository repository;

    @Override
    public RegraRoteamento save(RegraRoteamento entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<RegraRoteamento> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<RegraRoteamento> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
