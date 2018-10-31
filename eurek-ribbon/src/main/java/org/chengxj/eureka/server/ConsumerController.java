package org.chengxj.eureka.server;

import org.chengxj.hello.service.api.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.netflix.hystrix.contrib.javanica.annotation.HystrixCommand;

@RestController
public class ConsumerController {
	
//	@Autowired
//	RestTemplate restTemplate;
	
	@Autowired
	RefactorHelloService refactorHelloService;
	
//	@HystrixCollapser(batchMethod = "findAll", collapserProperties= {
//			@HystrixProperty(name="timerDelayInMilliseconds", value = "100")
//	})
	@HystrixCommand(fallbackMethod = "error")
	@RequestMapping(value = "/ribbon-consumer")
	public String consumer() {
		return refactorHelloService.hello();			
	}
	
	@HystrixCommand(fallbackMethod = "error")
	@RequestMapping(value = "/feign-consumer")
	public String consumer1() {
		StringBuilder sb = new StringBuilder();
		sb.append(refactorHelloService.hello()).append("\n");
		sb.append(refactorHelloService.hello("DIDI")).append("\n");
		sb.append(refactorHelloService.hello("DIDI", 30)).append("\n");
		sb.append(refactorHelloService.hello(new User("DIDI", 32))).append("\n");
		return sb.toString();			
	}
	
	public String error() {
		return "error test";
	}
	
	public String findAll() {
		return "find all";
	}

}