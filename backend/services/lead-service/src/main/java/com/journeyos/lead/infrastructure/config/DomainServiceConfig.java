package com.journeyos.lead.infrastructure.config;

import com.journeyos.lead.domain.service.LeadDomainService;
import com.journeyos.lead.domain.service.SurveyDomainService;
import com.journeyos.lead.domain.service.RegraQualificacaoDomainService;
import com.journeyos.lead.domain.service.SegmentoDomainService;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class DomainServiceConfig {

    @Bean
    public LeadDomainService leadDomainService() {
        return new LeadDomainService();
    }

    @Bean
    public SurveyDomainService surveyDomainService() {
        return new SurveyDomainService();
    }

    @Bean
    public RegraQualificacaoDomainService regraQualificacaoDomainService() {
        return new RegraQualificacaoDomainService();
    }

    @Bean
    public SegmentoDomainService segmentoDomainService() {
        return new SegmentoDomainService();
    }
}
