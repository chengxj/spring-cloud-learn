package org.chengxj.eureka.server;

import org.chengxj.hello.service.api.HelloService;
import org.springframework.cloud.openfeign.FeignClient;

@FeignClient(value="HELLO-SERVICE")
public interface RefactorHelloService extends HelloService {

}
