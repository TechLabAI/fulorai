package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.ConversaCopilotoPort;
import com.journeyos.intl.domain.model.ConversaCopiloto;
import com.journeyos.intl.infrastructure.persistence.entity.ConversaCopilotoEntity;
import com.journeyos.intl.infrastructure.persistence.repository.ConversaCopilotoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class ConversaCopilotoJpaAdapter implements ConversaCopilotoPort {

    private final ConversaCopilotoRepository repository;

    @Override
    public ConversaCopiloto save(ConversaCopiloto domain) {
        return toDomain(repository.save(toEntity(domain)));
    }

    @Override
    public Optional<ConversaCopiloto> findById(UUID id) {
        return repository.findById(id).map(this::toDomain);
    }

    @Override
    public void deleteById(UUID id) {
        repository.deleteById(id);
    }

    private ConversaCopiloto toDomain(ConversaCopilotoEntity e) {
        // TODO: implement — return new ConversaCopiloto(e.getId(), ...)
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }

    private ConversaCopilotoEntity toEntity(ConversaCopiloto d) {
        // TODO: implement — set each field from domain record
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }
}
