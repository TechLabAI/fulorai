package com.journeyos.intl.infrastructure.persistence.adapter;

import com.journeyos.intl.application.port.out.EventoIndexadoPort;
import com.journeyos.intl.domain.model.EventoIndexado;
import com.journeyos.intl.infrastructure.persistence.entity.EventoIndexadoEntity;
import com.journeyos.intl.infrastructure.persistence.repository.EventoIndexadoRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class EventoIndexadoJpaAdapter implements EventoIndexadoPort {

    private final EventoIndexadoRepository repository;

    @Override
    public EventoIndexado save(EventoIndexado domain) {
        return toDomain(repository.save(toEntity(domain)));
    }

    @Override
    public Optional<EventoIndexado> findById(UUID id) {
        return repository.findById(id).map(this::toDomain);
    }

    @Override
    public void deleteById(UUID id) {
        repository.deleteById(id);
    }

    private EventoIndexado toDomain(EventoIndexadoEntity e) {
        // TODO: implement — return new EventoIndexado(e.getEventoId(), ...)
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }

    private EventoIndexadoEntity toEntity(EventoIndexado d) {
        // TODO: implement — set each field from domain record
        throw new UnsupportedOperationException("Not implemented — see 02b-be-logic");
    }
}
