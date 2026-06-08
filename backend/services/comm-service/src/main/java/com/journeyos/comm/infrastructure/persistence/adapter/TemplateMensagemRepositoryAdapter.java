package com.journeyos.comm.infrastructure.persistence.adapter;

import com.journeyos.comm.application.port.out.TemplateMensagemRepositoryPort;
import com.journeyos.comm.domain.model.TemplateMensagem;
import com.journeyos.comm.infrastructure.persistence.repository.TemplateMensagemJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class TemplateMensagemRepositoryAdapter implements TemplateMensagemRepositoryPort {

    private final TemplateMensagemJpaRepository repository;

    @Override
    public TemplateMensagem save(TemplateMensagem entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<TemplateMensagem> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<TemplateMensagem> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
