package com.journeyos.wrks.infrastructure.persistence.adapter;

import com.journeyos.wrks.application.port.out.UsuarioTeamRepositoryPort;
import com.journeyos.wrks.domain.model.UsuarioTeam;
import com.journeyos.wrks.infrastructure.persistence.repository.UsuarioTeamJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class UsuarioTeamRepositoryAdapter implements UsuarioTeamRepositoryPort {

    private final UsuarioTeamJpaRepository repository;

    @Override
    public UsuarioTeam save(UsuarioTeam entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<UsuarioTeam> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<UsuarioTeam> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
