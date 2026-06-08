package com.journeyos.sale.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class LeadScoreAtualizadoConsumer {


    @JmsListener(destination = "journey-os.lead.score.atualizado", containerFactory = "jmsListenerContainerFactory")
    public void handle(String payload) {
        // TODO: deserialize journey-os.lead.score.atualizado event and apply domain logic
        log.info("[JMS] journey-os.lead.score.atualizado received");
        throw new UnsupportedOperationException("not implemented");
    }
}
