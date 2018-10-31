package org.chengxj.hello.service;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.web.bind.annotation.RestController;

@RestController
@EnableDiscoveryClient
@SpringBootApplication
public class HelloApplication {
	
	public static void main(String[] args) {
		SpringApplication.run(HelloApplication.class, args);
	}
	
}