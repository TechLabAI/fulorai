package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.BaseConhecimentoPort;
import com.journeyos.intl.domain.model.BaseConhecimento;
import com.journeyos.intl.infrastructure.persistence.entity.BaseConhecimentoEntity;
import com.journeyos.intl.infrastructure.persistence.repository.BaseConhecimentoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class BaseConhecimentoJpaAdapter implements BaseConhecimentoPort {

    private final BaseConhecimentoRepository repository;

    @Override
    public BaseConhecimento save(BaseConhecimento domain) {
        return toDomain(repository.save(toEntity(domain)));
    }

    @Override
    public Optional<BaseConhecimento> findById(UUID id) {
        return repository.findById(id).map(this::toDomain);
    }

    @Override
    public void deleteById(UUID id) {
        repository.deleteById(id);
    }

    private BaseConhecimento toDomain(BaseConhecimentoEntity e) {
        // TODO: implement — return new BaseConhecimento(e.getId(), ...)
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }

    private BaseConhecimentoEntity toEntity(BaseConhecimento d) {
        // TODO: implement — set each field from domain record
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }
}
