package com.stock.survive.controller;

import com.stock.survive.dto.UserStockHoldingDto;
import com.stock.survive.service.AccountService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ExtendWith(MockitoExtension.class)
class AccountControllerTest {

    @Mock
    private AccountService accountService;

    @InjectMocks
    private AccountController accountController;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.standaloneSetup(accountController).build();
    }

    @Test
    @DisplayName("보유 종목 조회 요청이 성공하면 200과 DTO를 반환한다")
    void getHoldingReturnsOk() throws Exception {
        UserStockHoldingDto dto = UserStockHoldingDto.builder()
                .ticker("005930")
                .quantity(7)
                .avgBuyPrice(571.42)
                .build();

        when(accountService.getUserStockHolding(eq(2L), eq("005930"))).thenReturn(dto);

        mockMvc.perform(
                        get("/api/trade/holding/005930")
                                .principal(() -> "2")
                                .accept(MediaType.APPLICATION_JSON)
                )
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ticker").value("005930"))
                .andExpect(jsonPath("$.quantity").value(7))
                .andExpect(jsonPath("$.avgBuyPrice").value(571.42));
    }
}
