package org.chengxj.hello.service.api;

import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;

@RequestMapping("/refactor")
public interface HelloService {
	
	@RequestMapping(value="/hello", method=RequestMethod.GET)
	String hello();
	
	@RequestMapping(value="/hello4", method=RequestMethod.GET)
	String hello(@RequestParam("name") String name);
	
	@RequestMapping(value="/hello5", method=RequestMethod.GET)
	User hello(@RequestHeader("name") String name, @RequestHeader("age") int age);
	
	@RequestMapping(value="/hello6", method=RequestMethod.POST)
	String hello(@RequestBody User user);
}
