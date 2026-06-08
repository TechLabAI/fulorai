package com.journeyos.asst.infrastructure.persistence.adapter;

import com.journeyos.asst.application.port.out.AprovacaoRepositoryPort;
import com.journeyos.asst.domain.model.Aprovacao;
import com.journeyos.asst.infrastructure.persistence.repository.AprovacaoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class AprovacaoRepositoryAdapter implements AprovacaoRepositoryPort {

    private final AprovacaoJpaRepository repository;

    @Override
    public Aprovacao save(Aprovacao entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Aprovacao> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Aprovacao> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
