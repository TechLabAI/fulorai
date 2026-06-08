package com.journeyos.lead;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@EnableFeignClients
@SpringBootApplication
public class LeadApplication {

    public static void main(String[] args) {
        SpringApplication.run(LeadApplication.class, args);
    }
}
