package com.stock.survive;

import com.stock.survive.dto.UserStockHoldingDto;
import com.stock.survive.service.AccountService;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
@Log4j2
public class AccountTest {

    @Autowired
    AccountService accountService;

    @Test
    void test() {

        Long userNo = 2L;
        String ticker = "005930";
        UserStockHoldingDto userStockHoldingDto = accountService.getUserStockHolding(userNo, ticker);
        log.info(userStockHoldingDto.getTicker());
        log.info(userStockHoldingDto.getQuantity());
        log.info(userStockHoldingDto.getAvgBuyPrice());


    }
}
