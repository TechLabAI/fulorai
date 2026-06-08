package com.journeyos.wrks.infrastructure.persistence.adapter;

import com.journeyos.wrks.application.port.out.ModeloAcessoVersaoRepositoryPort;
import com.journeyos.wrks.domain.model.ModeloAcessoVersao;
import com.journeyos.wrks.infrastructure.persistence.repository.ModeloAcessoVersaoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ModeloAcessoVersaoRepositoryAdapter implements ModeloAcessoVersaoRepositoryPort {

    private final ModeloAcessoVersaoJpaRepository repository;

    @Override
    public ModeloAcessoVersao save(ModeloAcessoVersao entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<ModeloAcessoVersao> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<ModeloAcessoVersao> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
