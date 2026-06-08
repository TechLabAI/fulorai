package com.journeyos.wrks.infrastructure.persistence.adapter;

import com.journeyos.wrks.application.port.out.BusinessUnitRepositoryPort;
import com.journeyos.wrks.domain.model.BusinessUnit;
import com.journeyos.wrks.infrastructure.persistence.repository.BusinessUnitJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class BusinessUnitRepositoryAdapter implements BusinessUnitRepositoryPort {

    private final BusinessUnitJpaRepository repository;

    @Override
    public BusinessUnit save(BusinessUnit entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<BusinessUnit> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<BusinessUnit> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
