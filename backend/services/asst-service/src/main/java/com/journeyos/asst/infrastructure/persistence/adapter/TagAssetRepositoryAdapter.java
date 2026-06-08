package com.journeyos.asst.infrastructure.persistence.adapter;

import com.journeyos.asst.application.port.out.TagAssetRepositoryPort;
import com.journeyos.asst.domain.model.TagAsset;
import com.journeyos.asst.infrastructure.persistence.repository.TagAssetJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class TagAssetRepositoryAdapter implements TagAssetRepositoryPort {

    private final TagAssetJpaRepository repository;

    @Override
    public TagAsset save(TagAsset entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<TagAsset> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<TagAsset> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
