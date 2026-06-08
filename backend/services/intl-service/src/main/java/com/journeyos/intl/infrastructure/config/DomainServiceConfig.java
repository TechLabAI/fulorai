package com.journeyos.intl.infrastructure.config;

import com.journeyos.intl.domain.service.BaseConhecimentoDomainService;
import com.journeyos.intl.domain.service.FonteConhecimentoDomainService;
import com.journeyos.intl.domain.service.ConversaCopilotoDomainService;
import com.journeyos.intl.domain.service.EventoIndexadoDomainService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DomainServiceConfig {

    @Bean
    public BaseConhecimentoDomainService baseConhecimentoDomainService() {
        return new BaseConhecimentoDomainService();
    }

    @Bean
    public FonteConhecimentoDomainService fonteConhecimentoDomainService() {
        return new FonteConhecimentoDomainService();
    }

    @Bean
    public ConversaCopilotoDomainService conversaCopilotoDomainService() {
        return new ConversaCopilotoDomainService();
    }

    @Bean
    public EventoIndexadoDomainService eventoIndexadoDomainService() {
        return new EventoIndexadoDomainService();
    }
}
