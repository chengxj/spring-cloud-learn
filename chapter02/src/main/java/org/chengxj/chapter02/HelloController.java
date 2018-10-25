package org.chengxj.chapter02;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
	
	@Autowired
//	private CounterService counterService;

	@RequestMapping("/hello")
	public String index() {
		return "Hello World";
	}

}
