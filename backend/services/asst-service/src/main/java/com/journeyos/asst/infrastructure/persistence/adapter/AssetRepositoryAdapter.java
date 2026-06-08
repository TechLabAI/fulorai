package com.journeyos.asst.infrastructure.persistence.adapter;

import com.journeyos.asst.application.port.out.AssetRepositoryPort;
import com.journeyos.asst.domain.model.Asset;
import com.journeyos.asst.infrastructure.persistence.repository.AssetJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class AssetRepositoryAdapter implements AssetRepositoryPort {

    private final AssetJpaRepository repository;

    @Override
    public Asset save(Asset entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Asset> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Asset> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
