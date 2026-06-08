package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.BaseConhecimentoRepositoryPort;
import com.journeyos.intl.domain.model.BaseConhecimento;
import com.journeyos.intl.infrastructure.persistence.repository.BaseConhecimentoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class BaseConhecimentoRepositoryAdapter implements BaseConhecimentoRepositoryPort {

    private final BaseConhecimentoJpaRepository repository;

    @Override
    public BaseConhecimento save(BaseConhecimento entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<BaseConhecimento> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<BaseConhecimento> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
