package org.chengxj.hello.service;

import java.util.Arrays;
import java.util.List;
import java.util.Random;

import org.chengxj.hello.service.api.HelloService;
import org.chengxj.hello.service.api.User;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RefactorHelloController implements HelloService {

	@Override
	public String hello(String name) {
		return "Hello" + name;
	}

	@Override
	public User hello(String name, int age) {
		return new User(name, age);
	}

	@Override
	public String hello(User user) {
		return "name" + user.getName() + ", age=" + user.getAge();
	}

	@Override
	public String hello() {
		List<String> greetings = Arrays.asList("Hi there", "Greetings", "Salutations");
		Random rand = new Random();
		int randomNum = rand.nextInt(greetings.size());
		return greetings.get(randomNum);
	}

}
