package com.journeyos.wrks.infrastructure.persistence.adapter;

import com.journeyos.wrks.application.port.out.PapelPermissaoRepositoryPort;
import com.journeyos.wrks.domain.model.PapelPermissao;
import com.journeyos.wrks.infrastructure.persistence.repository.PapelPermissaoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class PapelPermissaoRepositoryAdapter implements PapelPermissaoRepositoryPort {

    private final PapelPermissaoJpaRepository repository;

    @Override
    public PapelPermissao save(PapelPermissao entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<PapelPermissao> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<PapelPermissao> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
