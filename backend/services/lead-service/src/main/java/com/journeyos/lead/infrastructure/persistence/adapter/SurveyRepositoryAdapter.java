package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.SurveyRepositoryPort;
import com.journeyos.lead.domain.model.Survey;
import com.journeyos.lead.infrastructure.persistence.repository.SurveyJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class SurveyRepositoryAdapter implements SurveyRepositoryPort {

    private final SurveyJpaRepository repository;

    @Override
    public Survey save(Survey entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Survey> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Survey> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
