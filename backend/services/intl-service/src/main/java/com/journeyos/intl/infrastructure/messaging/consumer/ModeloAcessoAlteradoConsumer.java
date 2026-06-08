package com.journeyos.intl.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class ModeloAcessoAlteradoConsumer {


    @JmsListener(destination = "journey-os.modelo.acesso.alterado", containerFactory = "jmsListenerContainerFactory")
    public void handle(String payload) {
        // TODO: deserialize journey-os.modelo.acesso.alterado event and apply domain logic
        log.info("[JMS] journey-os.modelo.acesso.alterado received");
        throw new UnsupportedOperationException("not implemented");
    }
}
