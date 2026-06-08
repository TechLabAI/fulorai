package com.journeyos.comm;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.openfeign.EnableFeignClients;

@EnableFeignClients
@SpringBootApplication
public class CommApplication {

    public static void main(String[] args) {
        SpringApplication.run(CommApplication.class, args);
    }
}
