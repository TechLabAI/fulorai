package com.journeyos.asst.infrastructure.config;

import com.journeyos.asst.domain.service.AssetDomainService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DomainServiceConfig {

    @Bean
    public AssetDomainService assetDomainService() {
        return new AssetDomainService();
    }
}
