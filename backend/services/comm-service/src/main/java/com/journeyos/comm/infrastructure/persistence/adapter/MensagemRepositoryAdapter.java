package com.journeyos.comm.infrastructure.persistence.adapter;

import com.journeyos.comm.application.port.out.MensagemRepositoryPort;
import com.journeyos.comm.domain.model.Mensagem;
import com.journeyos.comm.infrastructure.persistence.repository.MensagemJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class MensagemRepositoryAdapter implements MensagemRepositoryPort {

    private final MensagemJpaRepository repository;

    @Override
    public Mensagem save(Mensagem entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Mensagem> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Mensagem> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
