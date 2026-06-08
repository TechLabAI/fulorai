package com.journeyos.lead.infrastructure.persistence.adapter;

import com.journeyos.lead.application.port.out.RegraQualificacaoRepositoryPort;
import com.journeyos.lead.domain.model.RegraQualificacao;
import com.journeyos.lead.infrastructure.persistence.repository.RegraQualificacaoJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class RegraQualificacaoRepositoryAdapter implements RegraQualificacaoRepositoryPort {

    private final RegraQualificacaoJpaRepository repository;

    @Override
    public RegraQualificacao save(RegraQualificacao entity) {
        // TODO: map domain model → JPA entity → save → map back
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public Optional<RegraQualificacao> findById(UUID id) {
        // TODO: map JPA entity → domain model
        throw new UnsupportedOperationException("not implemented");
    }

    @Override
    public List<RegraQualificacao> findByTenantId(String tenantId) {
        // TODO: map JPA entities → domain models
        throw new UnsupportedOperationException("not implemented");
    }
}
