package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.NoConhecimentoPort;
import com.journeyos.intl.domain.model.NoConhecimento;
import com.journeyos.intl.infrastructure.persistence.entity.NoConhecimentoEntity;
import com.journeyos.intl.infrastructure.persistence.repository.NoConhecimentoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class NoConhecimentoJpaAdapter implements NoConhecimentoPort {

    private final NoConhecimentoRepository repository;

    @Override
    public NoConhecimento save(NoConhecimento domain) {
        return toDomain(repository.save(toEntity(domain)));
    }

    @Override
    public Optional<NoConhecimento> findById(UUID id) {
        return repository.findById(id).map(this::toDomain);
    }

    @Override
    public void deleteById(UUID id) {
        repository.deleteById(id);
    }

    private NoConhecimento toDomain(NoConhecimentoEntity e) {
        // TODO: implement — return new NoConhecimento(e.getId(), ...)
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }

    private NoConhecimentoEntity toEntity(NoConhecimento d) {
        // TODO: implement — set each field from domain record
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }
}
