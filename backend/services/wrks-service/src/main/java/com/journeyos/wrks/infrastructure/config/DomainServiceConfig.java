package com.journeyos.wrks.infrastructure.config;

import com.journeyos.wrks.domain.service.EmpresaDomainService;
import com.journeyos.wrks.domain.service.UsuarioDomainService;
import com.journeyos.wrks.domain.service.PapelDomainService;
import com.journeyos.wrks.domain.service.PermissaoDomainService;
import com.journeyos.wrks.domain.service.ModeloAcessoVersaoDomainService;
import com.journeyos.wrks.domain.service.EventoAuditoriaDomainService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DomainServiceConfig {

    @Bean
    public EmpresaDomainService empresaDomainService() {
        return new EmpresaDomainService();
    }

    @Bean
    public UsuarioDomainService usuarioDomainService() {
        return new UsuarioDomainService();
    }

    @Bean
    public PapelDomainService papelDomainService() {
        return new PapelDomainService();
    }

    @Bean
    public PermissaoDomainService permissaoDomainService() {
        return new PermissaoDomainService();
    }

    @Bean
    public ModeloAcessoVersaoDomainService modeloAcessoVersaoDomainService() {
        return new ModeloAcessoVersaoDomainService();
    }

    @Bean
    public EventoAuditoriaDomainService eventoAuditoriaDomainService() {
        return new EventoAuditoriaDomainService();
    }
}
