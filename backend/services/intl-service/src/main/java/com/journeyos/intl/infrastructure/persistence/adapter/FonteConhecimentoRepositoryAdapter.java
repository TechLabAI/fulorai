package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.FonteConhecimentoRepositoryPort;
import com.journeyos.intl.domain.model.FonteConhecimento;
import com.journeyos.intl.infrastructure.persistence.repository.FonteConhecimentoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class FonteConhecimentoRepositoryAdapter implements FonteConhecimentoRepositoryPort {

    private final FonteConhecimentoJpaRepository repository;

    @Override
    public FonteConhecimento save(FonteConhecimento entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<FonteConhecimento> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<FonteConhecimento> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
