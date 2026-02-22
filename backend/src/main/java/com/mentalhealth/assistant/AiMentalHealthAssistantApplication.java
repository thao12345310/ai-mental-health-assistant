package com.mentalhealth.assistant;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class AiMentalHealthAssistantApplication {
    public static void main(String[] args) {
        SpringApplication.run(AiMentalHealthAssistantApplication.class, args);
    }
}
