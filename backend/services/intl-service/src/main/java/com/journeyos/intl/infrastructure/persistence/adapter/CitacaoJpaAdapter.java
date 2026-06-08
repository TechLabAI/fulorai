package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.CitacaoPort;
import com.journeyos.intl.domain.model.Citacao;
import com.journeyos.intl.infrastructure.persistence.entity.CitacaoEntity;
import com.journeyos.intl.infrastructure.persistence.repository.CitacaoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class CitacaoJpaAdapter implements CitacaoPort {

    private final CitacaoRepository repository;

    @Override
    public Citacao save(Citacao domain) {
        return toDomain(repository.save(toEntity(domain)));
    }

    @Override
    public Optional<Citacao> findById(UUID id) {
        return repository.findById(id).map(this::toDomain);
    }

    @Override
    public void deleteById(UUID id) {
        repository.deleteById(id);
    }

    private Citacao toDomain(CitacaoEntity e) {
        // TODO: implement — return new Citacao(e.getId(), ...)
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }

    private CitacaoEntity toEntity(Citacao d) {
        // TODO: implement — set each field from domain record
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }
}
