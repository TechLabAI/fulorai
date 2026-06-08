package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.MensagemCopilotoPort;
import com.journeyos.intl.domain.model.MensagemCopiloto;
import com.journeyos.intl.infrastructure.persistence.entity.MensagemCopilotoEntity;
import com.journeyos.intl.infrastructure.persistence.repository.MensagemCopilotoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class MensagemCopilotoJpaAdapter implements MensagemCopilotoPort {

    private final MensagemCopilotoRepository repository;

    @Override
    public MensagemCopiloto save(MensagemCopiloto domain) {
        return toDomain(repository.save(toEntity(domain)));
    }

    @Override
    public Optional<MensagemCopiloto> findById(UUID id) {
        return repository.findById(id).map(this::toDomain);
    }

    @Override
    public void deleteById(UUID id) {
        repository.deleteById(id);
    }

    private MensagemCopiloto toDomain(MensagemCopilotoEntity e) {
        // TODO: implement — return new MensagemCopiloto(e.getId(), ...)
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }

    private MensagemCopilotoEntity toEntity(MensagemCopiloto d) {
        // TODO: implement — set each field from domain record
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }
}
