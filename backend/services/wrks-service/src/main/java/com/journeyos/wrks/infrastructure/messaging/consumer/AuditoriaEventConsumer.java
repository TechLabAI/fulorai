package com.journeyos.wrks.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class AuditoriaEventConsumer {


    @JmsListener(destination = "journey-os.audit", containerFactory = "jmsListenerContainerFactory")
    public void handle(String payload) {
        // TODO: deserialize journey-os.* event and apply domain logic
        log.info("[JMS] journey-os.* received");
        throw new UnsupportedOperationException("not implemented");
    }
}
