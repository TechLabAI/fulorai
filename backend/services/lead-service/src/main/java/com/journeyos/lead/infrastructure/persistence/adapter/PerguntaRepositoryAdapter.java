package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.PerguntaRepositoryPort;
import com.journeyos.lead.domain.model.Pergunta;
import com.journeyos.lead.infrastructure.persistence.repository.PerguntaJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class PerguntaRepositoryAdapter implements PerguntaRepositoryPort {

    private final PerguntaJpaRepository repository;

    @Override
    public Pergunta save(Pergunta entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<Pergunta> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<Pergunta> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
