package com.journeyos.comm.infrastructure.messaging.consumer;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jms.annotation.JmsListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class AssetVersaoPublicadaConsumer {


    @JmsListener(destination = "journey-os.asset.versao.publicada", containerFactory = "jmsListenerContainerFactory")
    public void handle(String payload) {
        // TODO: deserialize journey-os.asset.versao.publicada event and apply domain logic
        log.info("[JMS] journey-os.asset.versao.publicada received");
        throw new UnsupportedOperationException("not implemented");
    }
}
