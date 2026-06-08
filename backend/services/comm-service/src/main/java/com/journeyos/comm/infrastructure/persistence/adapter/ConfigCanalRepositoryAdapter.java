package com.journeyos.comm.infrastructure.persistence.adapter;

import com.journeyos.comm.application.port.out.ConfigCanalRepositoryPort;
import com.journeyos.comm.domain.model.ConfigCanal;
import com.journeyos.comm.infrastructure.persistence.repository.ConfigCanalJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ConfigCanalRepositoryAdapter implements ConfigCanalRepositoryPort {

    private final ConfigCanalJpaRepository repository;

    @Override
    public ConfigCanal save(ConfigCanal entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<ConfigCanal> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<ConfigCanal> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
