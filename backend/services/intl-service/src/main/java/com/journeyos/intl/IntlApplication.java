package com.journeyos.intl;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@EnableFeignClients
@SpringBootApplication
public class IntlApplication {

    public static void main(String[] args) {
        SpringApplication.run(IntlApplication.class, args);
    }
}
