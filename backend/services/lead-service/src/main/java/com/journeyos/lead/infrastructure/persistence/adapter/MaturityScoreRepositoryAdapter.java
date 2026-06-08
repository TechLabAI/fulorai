package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.MaturityScoreRepositoryPort;
import com.journeyos.lead.domain.model.MaturityScore;
import com.journeyos.lead.infrastructure.persistence.repository.MaturityScoreJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class MaturityScoreRepositoryAdapter implements MaturityScoreRepositoryPort {

    private final MaturityScoreJpaRepository repository;

    @Override
    public MaturityScore save(MaturityScore entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<MaturityScore> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<MaturityScore> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
