package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.FonteConhecimentoPort;
import com.journeyos.intl.domain.model.FonteConhecimento;
import com.journeyos.intl.infrastructure.persistence.entity.FonteConhecimentoEntity;
import com.journeyos.intl.infrastructure.persistence.repository.FonteConhecimentoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class FonteConhecimentoJpaAdapter implements FonteConhecimentoPort {

    private final FonteConhecimentoRepository repository;

    @Override
    public FonteConhecimento save(FonteConhecimento domain) {
        return toDomain(repository.save(toEntity(domain)));
    }

    @Override
    public Optional<FonteConhecimento> findById(UUID id) {
        return repository.findById(id).map(this::toDomain);
    }

    @Override
    public void deleteById(UUID id) {
        repository.deleteById(id);
    }

    private FonteConhecimento toDomain(FonteConhecimentoEntity e) {
        // TODO: implement — return new FonteConhecimento(e.getId(), ...)
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }

    private FonteConhecimentoEntity toEntity(FonteConhecimento d) {
        // TODO: implement — set each field from domain record
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }
}
