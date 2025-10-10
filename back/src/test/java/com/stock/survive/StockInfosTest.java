package com.stock.survive;

import com.stock.survive.dto.StockInfosDto;
import com.stock.survive.entity.StockInfos;
import com.stock.survive.repository.StockInfosRepository;
import com.stock.survive.service.StockInfosService;
import jakarta.transaction.Transactional;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

@SpringBootTest
@Log4j2
public class StockInfosTest {

    @Autowired
    StockInfosRepository stockInfosRepository;

    @Autowired
    StockInfosService stockInfosService;

    @Test
    public void repoTest() {
        Assertions.assertNotNull(stockInfosRepository);
        log.info(stockInfosRepository.getClass().getName());
    }

    @Test
    @Transactional
    public void getTest() {
        List<StockInfos> list = stockInfosRepository.findAll();
        for (StockInfos stockInfos : list) {
            log.info(stockInfos.getStockItem().getCompanyName() + ", " + stockInfos.getStockItem().getTicker() + ", " + stockInfos.getVolume() + ", " + stockInfos.getMarketCap());
        }
    }

    @Test
    @Transactional
    public void getStockTest() {
        String ticker = "005930";
        List<StockInfosDto> list = stockInfosService.getStock(ticker);

        for (StockInfosDto stockInfosDto : list) {
            log.info(stockInfosDto.getTicker() + ", " + stockInfosDto.getCompanyName() + ", " + stockInfosDto.getEndPrice()+ ", " +stockInfosDto.getDate());

        }
    }

//    @Test
//    @Transactional
//    public void getLatestEndPriceTest() {
//        Long itemNo = 1L; // 실제 DB에 있는 itemNo로 바꿔주세요
//        Integer latestPrice = stockInfosService.getLatestEndPrice(itemNo);
//
//        Assertions.assertNotNull(latestPrice, "최신 종가가 존재해야 합니다");
//        log.info("itemNo={} 최신 종가={}", itemNo, latestPrice);
//    }



}