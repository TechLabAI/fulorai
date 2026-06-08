package com.journeyos.wrks;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@EnableFeignClients
@SpringBootApplication
public class WrksApplication {

    public static void main(String[] args) {
        SpringApplication.run(WrksApplication.class, args);
    }
}
