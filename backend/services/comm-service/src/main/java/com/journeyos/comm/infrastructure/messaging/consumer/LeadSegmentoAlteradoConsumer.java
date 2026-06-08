package com.journeyos.comm.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class LeadSegmentoAlteradoConsumer {


    @JmsListener(destination = "journey-os.lead.segmento.alterado", containerFactory = "jmsListenerContainerFactory")
    public void handle(String payload) {
        // TODO: deserialize journey-os.lead.segmento.alterado event and apply domain logic
        log.info("[JMS] journey-os.lead.segmento.alterado received");
        throw new UnsupportedOperationException("not implemented");
    }
}
