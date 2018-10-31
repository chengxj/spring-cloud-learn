package org.chengxj.eureka.server.ha;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.client.ServiceInstance;
import org.springframework.cloud.client.discovery.DiscoveryClient;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
	
	@Autowired
	private DiscoveryClient client;
	
	@RequestMapping(value = "/hello")
	public String index() {
		List<String> services = client.getServices();
		if (services != null && services.size() >0) {
			for (String serviceId:services) {
				List<ServiceInstance> instances = client.getInstances(serviceId);
			    if (instances != null && instances.size() > 0 ) {
			        System.out.println("==" + instances.get(0).getUri());
			    }

			}
		}
		return "hello world!";
	}
	

}
