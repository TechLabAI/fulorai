package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.AtribuicaoRepositoryPort;
import com.journeyos.sale.domain.model.Atribuicao;
import com.journeyos.sale.infrastructure.persistence.repository.AtribuicaoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class AtribuicaoRepositoryAdapter implements AtribuicaoRepositoryPort {

    private final AtribuicaoJpaRepository repository;

    @Override
    public Atribuicao save(Atribuicao entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Atribuicao> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Atribuicao> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
