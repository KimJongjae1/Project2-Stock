package com.stock.survive;

import com.stock.survive.dto.UserAsset;
import com.stock.survive.dto.UserAssetDto;
import com.stock.survive.dto.UserTradeHistoryDto;
import com.stock.survive.entity.User;
import com.stock.survive.repository.UserRepository;
import com.stock.survive.service.TradeHistoryService;
import lombok.extern.log4j.Log4j2;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;
import java.util.Optional;

@SpringBootTest
@Log4j2
@Tag("integration")
public class TradeTest {
    @Autowired
    TradeHistoryService tradeHistoryService;

    @Autowired
    UserRepository userRepository;


    @Test
    void userAsset() {
        Long userNo = 1L;
        UserAssetDto userAssetDto = tradeHistoryService.getUserAssets(userNo);
        log.info(userAssetDto.getCash());
        log.info(userAssetDto.getHaveStock());
        log.info(userAssetDto.getOriginalMoney());

    }

    @Test
    void buyTest() {

        Long userNo = 1L;
        String ticker = "005930";

        Long price = 83000L;
        int volume = 3;

        UserAsset userAsset = tradeHistoryService.processBuy(userNo, ticker, price, volume);

        log.info(userAsset.getTradeType());
        log.info(userAsset.getPrice());
        log.info(userAsset.getVolume());
        log.info(userAsset.getTotalPrice());
        log.info("---------------------------");

        Optional<User> optionalUser = userRepository.findById(userNo);
        log.info(optionalUser.get().getAccount().getCash());
        log.info(optionalUser.get().getAccount().getHaveStock());

    }

    @Test
    void sellTest() {

        Long userNo = 1L;
        String ticker = "005930";

        Long price = 83000L;
        int volume = 3;

        UserAsset userAsset = tradeHistoryService.processSell(userNo, ticker, price, volume);

        log.info(userAsset.getTradeType());
        log.info(userAsset.getPrice());
        log.info(userAsset.getVolume());
        log.info(userAsset.getTotalPrice());
        log.info("---------------------------");

        Optional<User> optionalUser = userRepository.findById(userNo);
        log.info(optionalUser.get().getAccount().getCash());
        log.info(optionalUser.get().getAccount().getHaveStock());

    }

    @Test
    void historyTest() {
        Long userNo = 1L;
        String ticker = "005930";

        List<UserTradeHistoryDto> list = tradeHistoryService.getUserTradeHistory(userNo, ticker);

        for (UserTradeHistoryDto userTradeHistoryDto : list) {
            log.info(userTradeHistoryDto.getTradeType());
            log.info(userTradeHistoryDto.getPrice());
            log.info(userTradeHistoryDto.getVolume());
            log.info(userTradeHistoryDto.getCreatedAt());
            log.info("---------------------------");
        }

    }


}
