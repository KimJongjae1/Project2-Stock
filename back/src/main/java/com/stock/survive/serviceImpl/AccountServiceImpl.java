package com.stock.survive.serviceImpl;

import com.stock.survive.dto.UserStockHoldingDto;
import com.stock.survive.entity.StockItems;
import com.stock.survive.entity.TradeHistory;
import com.stock.survive.enumType.TradeType;
import com.stock.survive.repository.StockItemRepository;
import com.stock.survive.repository.TradeHistoryRepository;
import com.stock.survive.service.AccountService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class AccountServiceImpl implements AccountService {

    private final TradeHistoryRepository tradeHistoryRepository;
    private final StockItemRepository stockItemRepository;


    @Override
    public UserStockHoldingDto getUserStockHolding(Long userNo, String ticker) {
        // 1. 종목 정보 조회
        StockItems stockItem = stockItemRepository.findByTicker(ticker);

        // 2. 유저의 해당 종목 거래 내역 조회
        List<TradeHistory> trades = tradeHistoryRepository.findByUserAndStockItem(userNo, stockItem.getItemNo());

        // 3. 현재 보유 수량 계산
        int quantity = 0;
        double totalCost = 0.0; // 총 매입 금액
        for (TradeHistory trade : trades) {
            if (trade.getTradeType() == TradeType.BUY) {
                quantity += trade.getVolume();
                totalCost += trade.getPrice() * trade.getVolume();
            } else if (trade.getTradeType() == TradeType.SELL) {
                quantity -= trade.getVolume();
                totalCost -= trade.getPrice() * trade.getVolume(); // 단순화, 평균 계산용
            }
        }

        double avgBuyPrice = quantity > 0 ? totalCost / quantity : 0;

        // 4. DTO로 반환
        return UserStockHoldingDto.builder()
                .ticker(ticker)
                .quantity(quantity)
                .avgBuyPrice(avgBuyPrice)
                .build();
    }


    @Override
    public int calculateHoldingQuantity(List<TradeHistory> trades) {
        int quantity = 0;
        for (TradeHistory trade : trades) {
            if (trade.getTradeType() == TradeType.BUY) {
                quantity += trade.getVolume();
            } else if (trade.getTradeType() == TradeType.SELL) {
                quantity -= trade.getVolume();
            }
        }
        return quantity;
    }
}

