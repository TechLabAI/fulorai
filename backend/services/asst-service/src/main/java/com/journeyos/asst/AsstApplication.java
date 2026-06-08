package com.journeyos.asst;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@EnableFeignClients
@SpringBootApplication
public class AsstApplication {

    public static void main(String[] args) {
        SpringApplication.run(AsstApplication.class, args);
    }
}
