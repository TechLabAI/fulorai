package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.AtributoPerfilRepositoryPort;
import com.journeyos.lead.domain.model.AtributoPerfil;
import com.journeyos.lead.infrastructure.persistence.repository.AtributoPerfilJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class AtributoPerfilRepositoryAdapter implements AtributoPerfilRepositoryPort {

    private final AtributoPerfilJpaRepository repository;

    @Override
    public AtributoPerfil save(AtributoPerfil entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<AtributoPerfil> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<AtributoPerfil> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
