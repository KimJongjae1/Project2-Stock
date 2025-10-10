package com.stock.survive.serviceImpl;

import com.stock.survive.dto.UserAsset;
import com.stock.survive.dto.UserAssetDto;
import com.stock.survive.dto.UserTradeHistoryDto;
import com.stock.survive.entity.StockItems;
import com.stock.survive.entity.TradeHistory;
import com.stock.survive.entity.User;
import com.stock.survive.enumType.TradeType;
import com.stock.survive.repository.StockItemRepository;
import com.stock.survive.repository.TradeHistoryRepository;
import com.stock.survive.repository.UserRepository;
import com.stock.survive.service.TradeHistoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class TradeHistoryServiceImpl implements TradeHistoryService {

    private final StockItemRepository stockItemRepository;
    private final UserRepository userRepository;
    private final TradeHistoryRepository tradeHistoryRepository;


    @Override
    public UserAssetDto getUserAssets(Long userNo) {
        Optional<User> user = userRepository.findById(userNo);
        return UserAssetDto.builder()
                .cash(user.get().getAccount().getCash())
                .haveStock(user.get().getAccount().getHaveStock())
                .originalMoney(user.get().getAccount().getOriginalMoney())
                .build();
    }


    @Transactional
    @Override
    public UserAsset processBuy(Long userNo, String ticker, Long price, Integer volume) {
        // 1. 티커로 주식 정보 조회
        StockItems stockItem = stockItemRepository.findByTicker(ticker);
        Optional<User> optionalUser = userRepository.findById(userNo);

        User user = optionalUser.get();

        // 2. 거래 금액 계산
        Long totalPrice = price * volume;

        // 3. 사용자 자산 업데이트
        Long setCash = user.getAccount().getCash() - totalPrice;
        Long setHaveStock = user.getAccount().getHaveStock() + totalPrice;

        // 4. 거래 내역 저장
        TradeHistory tradeHistory = TradeHistory.builder()
                .tradeType(TradeType.BUY)
                .price(price)
                .volume(volume)
                .totalPrice(totalPrice)
                .account(user.getAccount())
                .user(user)
                .stockItems(stockItem)
                .build();

        // 5. 거래 내역 저장 및 사용자 자산 업데이트
        tradeHistoryRepository.save(tradeHistory);
        userRepository.updateCashAndHaveStock(userNo, setCash, setHaveStock);


        // 6. 거래 내역을 DTO로 반환
        return UserAsset.builder()
                .tradeType("BUY")
                .price(price)
                .volume(volume)
                .totalPrice(totalPrice)
                .createdAt((tradeHistory.getCreatedAt())) // 거래 생성 시점
                .build();
    }

    @Transactional
    @Override
    public UserAsset processSell(Long userNo, String ticker, Long price, Integer volume) {
        // 1. 티커로 주식 정보 조회
        StockItems stockItem = stockItemRepository.findByTicker(ticker);
        Optional<User> optionalUser = userRepository.findById(userNo);


        User user = optionalUser.get();
        // 2. 거래 금액 계산
        Long totalPrice = price * volume;

        // 3. 사용자 자산 업데이트
        Long setCash = user.getAccount().getCash() + totalPrice;
        Long setHaveStock = user.getAccount().getHaveStock() - totalPrice;

        // 4. 거래 내역 저장
        TradeHistory tradeHistory = TradeHistory.builder()
                .tradeType(TradeType.SELL)
                .price(price)
                .volume(volume)
                .totalPrice(totalPrice)
                .account(user.getAccount())
                .user(user)
                .stockItems(stockItem)
                .build();

        // 5. 거래 내역 저장 및 사용자 자산 업데이트
        tradeHistoryRepository.save(tradeHistory);
        userRepository.updateCashAndHaveStock(userNo, setCash, setHaveStock);


        // 6. 거래 내역을 DTO로 반환
        return UserAsset.builder()
                .tradeType("SELL")
                .price(price)
                .volume(volume)
                .totalPrice(totalPrice)
                .createdAt(tradeHistory.getCreatedAt()) // 거래 생성 시점
                .build();
    }

    @Override
    public List<UserTradeHistoryDto> getUserTradeHistory(Long userNo, String ticker) {

        Optional<User> user = userRepository.findById(userNo);
        StockItems stockItem = stockItemRepository.findByTicker(ticker);

        return tradeHistoryRepository.findByUserAndStockItem(user.get().getId(), stockItem.getItemNo())
                .stream()
                .map(trade -> UserTradeHistoryDto.builder()
                        .tradeType(trade.getTradeType().name()) // "BUY" or "SELL"
                        .price(trade.getPrice())
                        .volume(trade.getVolume())
                        .createdAt(trade.getCreatedAt())
                        .build())
                .collect(Collectors.toList());
    }
}


