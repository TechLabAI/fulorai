package com.journeyos.jrny;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@EnableFeignClients
@SpringBootApplication
public class JrnyApplication {

    public static void main(String[] args) {
        SpringApplication.run(JrnyApplication.class, args);
    }
}
