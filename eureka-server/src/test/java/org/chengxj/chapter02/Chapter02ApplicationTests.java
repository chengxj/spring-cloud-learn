package org.chengxj.chapter02;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultHandlers.print;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.hamcrest.Matchers.equalTo;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.junit4.SpringRunner;
import org.springframework.test.web.servlet.MockMvc;

@RunWith(SpringRunner.class)
//@SpringBootTest(classes= {Chapter02Application.class,HelloController.class})
@AutoConfigureMockMvc
public class Chapter02ApplicationTests {
	
	@Autowired
	private MockMvc mvc;
	
	@Test
	public void contextLoads() throws Exception {
		mvc.perform(get("/hello").accept(MediaType.APPLICATION_JSON))
		.andExpect(status().isOk())
//		.andDo(print())
//		.andReturn();
		.andExpect(content().string(equalTo("Hello World")))
		.andDo(print());
	}

}
