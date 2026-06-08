package com.journeyos.lead.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class EmpresaProvisionadaConsumer {


    @JmsListener(destination = "journey-os.empresa.provisionada", containerFactory = "jmsListenerContainerFactory")
    public void handle(String payload) {
        // TODO: deserialize journey-os.empresa.provisionada event and apply domain logic
        log.info("[JMS] journey-os.empresa.provisionada received");
        throw new UnsupportedOperationException("not implemented");
    }
}
