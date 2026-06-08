package com.journeyos.sale.infrastructure.persistence.adapter;

import com.journeyos.sale.application.port.out.ModeloAtribuicaoRepositoryPort;
import com.journeyos.sale.domain.model.ModeloAtribuicao;
import com.journeyos.sale.infrastructure.persistence.repository.ModeloAtribuicaoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ModeloAtribuicaoRepositoryAdapter implements ModeloAtribuicaoRepositoryPort {

    private final ModeloAtribuicaoJpaRepository repository;

    @Override
    public ModeloAtribuicao save(ModeloAtribuicao entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<ModeloAtribuicao> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<ModeloAtribuicao> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
