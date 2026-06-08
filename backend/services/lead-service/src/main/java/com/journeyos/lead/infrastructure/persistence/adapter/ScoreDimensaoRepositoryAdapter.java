package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.ScoreDimensaoRepositoryPort;
import com.journeyos.lead.domain.model.ScoreDimensao;
import com.journeyos.lead.infrastructure.persistence.repository.ScoreDimensaoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ScoreDimensaoRepositoryAdapter implements ScoreDimensaoRepositoryPort {

    private final ScoreDimensaoJpaRepository repository;

    @Override
    public ScoreDimensao save(ScoreDimensao entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<ScoreDimensao> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<ScoreDimensao> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
