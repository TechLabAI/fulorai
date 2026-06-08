package com.journeyos.jrny.infrastructure.config;

import com.journeyos.jrny.domain.service.JornadaDomainService;
import com.journeyos.jrny.domain.service.InscricaoJornadaDomainService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DomainServiceConfig {

    @Bean
    public JornadaDomainService jornadaDomainService() {
        return new JornadaDomainService();
    }

    @Bean
    public InscricaoJornadaDomainService inscricaoJornadaDomainService() {
        return new InscricaoJornadaDomainService();
    }
}
