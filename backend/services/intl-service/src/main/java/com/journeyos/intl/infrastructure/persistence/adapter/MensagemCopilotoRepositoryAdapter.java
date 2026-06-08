package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.MensagemCopilotoRepositoryPort;
import com.journeyos.intl.domain.model.MensagemCopiloto;
import com.journeyos.intl.infrastructure.persistence.repository.MensagemCopilotoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class MensagemCopilotoRepositoryAdapter implements MensagemCopilotoRepositoryPort {

    private final MensagemCopilotoJpaRepository repository;

    @Override
    public MensagemCopiloto save(MensagemCopiloto entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<MensagemCopiloto> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<MensagemCopiloto> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
