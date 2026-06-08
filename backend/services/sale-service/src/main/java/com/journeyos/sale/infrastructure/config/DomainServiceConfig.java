package com.journeyos.sale.infrastructure.config;

import com.journeyos.sale.domain.service.OportunidadeDomainService;
import com.journeyos.sale.domain.service.OfertaDomainService;
import com.journeyos.sale.domain.service.CompraDomainService;
import com.journeyos.sale.domain.service.ModeloAtribuicaoDomainService;
import com.journeyos.sale.domain.service.CampanhaDomainService;
import com.journeyos.sale.domain.service.LtvDomainService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DomainServiceConfig {

    @Bean
    public OportunidadeDomainService oportunidadeDomainService() {
        return new OportunidadeDomainService();
    }

    @Bean
    public OfertaDomainService ofertaDomainService() {
        return new OfertaDomainService();
    }

    @Bean
    public CompraDomainService compraDomainService() {
        return new CompraDomainService();
    }

    @Bean
    public ModeloAtribuicaoDomainService modeloAtribuicaoDomainService() {
        return new ModeloAtribuicaoDomainService();
    }

    @Bean
    public CampanhaDomainService campanhaDomainService() {
        return new CampanhaDomainService();
    }

    @Bean
    public LtvDomainService ltvDomainService() {
        return new LtvDomainService();
    }
}
