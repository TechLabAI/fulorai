package com.journeyos.sale.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class LeadQualificadoConsumer {


    @JmsListener(destination = "journey-os.lead.qualificado", containerFactory = "jmsListenerContainerFactory")
    public void handle(String payload) {
        // TODO: deserialize journey-os.lead.qualificado event and apply domain logic
        log.info("[JMS] journey-os.lead.qualificado received");
        throw new UnsupportedOperationException("not implemented");
    }
}
