package com.journeyos.wrks.infrastructure.persistence.adapter;

import com.journeyos.wrks.application.port.out.UsuarioEmpresaRepositoryPort;
import com.journeyos.wrks.domain.model.UsuarioEmpresa;
import com.journeyos.wrks.infrastructure.persistence.repository.UsuarioEmpresaJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class UsuarioEmpresaRepositoryAdapter implements UsuarioEmpresaRepositoryPort {

    private final UsuarioEmpresaJpaRepository repository;

    @Override
    public UsuarioEmpresa save(UsuarioEmpresa entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<UsuarioEmpresa> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<UsuarioEmpresa> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
