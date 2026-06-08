package com.journeyos.comm.infrastructure.config;

import com.journeyos.comm.domain.service.TemplateMensagemDomainService;
import com.journeyos.comm.domain.service.MensagemDomainService;
import com.journeyos.comm.domain.service.RegraRoteamentoDomainService;
import com.journeyos.comm.domain.service.ConfigCanalDomainService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DomainServiceConfig {

    @Bean
    public TemplateMensagemDomainService templateMensagemDomainService() {
        return new TemplateMensagemDomainService();
    }

    @Bean
    public MensagemDomainService mensagemDomainService() {
        return new MensagemDomainService();
    }

    @Bean
    public RegraRoteamentoDomainService regraRoteamentoDomainService() {
        return new RegraRoteamentoDomainService();
    }

    @Bean
    public ConfigCanalDomainService configCanalDomainService() {
        return new ConfigCanalDomainService();
    }
}
