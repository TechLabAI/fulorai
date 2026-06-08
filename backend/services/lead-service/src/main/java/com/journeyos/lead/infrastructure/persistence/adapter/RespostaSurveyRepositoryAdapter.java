package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.RespostaSurveyRepositoryPort;
import com.journeyos.lead.domain.model.RespostaSurvey;
import com.journeyos.lead.infrastructure.persistence.repository.RespostaSurveyJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class RespostaSurveyRepositoryAdapter implements RespostaSurveyRepositoryPort {

    private final RespostaSurveyJpaRepository repository;

    @Override
    public RespostaSurvey save(RespostaSurvey entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<RespostaSurvey> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<RespostaSurvey> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
