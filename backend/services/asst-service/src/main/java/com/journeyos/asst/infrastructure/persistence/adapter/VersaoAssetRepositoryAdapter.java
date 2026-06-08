package com.journeyos.asst.infrastructure.persistence.adapter;

import com.journeyos.asst.application.port.out.VersaoAssetRepositoryPort;
import com.journeyos.asst.domain.model.VersaoAsset;
import com.journeyos.asst.infrastructure.persistence.repository.VersaoAssetJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class VersaoAssetRepositoryAdapter implements VersaoAssetRepositoryPort {

    private final VersaoAssetJpaRepository repository;

    @Override
    public VersaoAsset save(VersaoAsset entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<VersaoAsset> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<VersaoAsset> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
