package com.stock.survive.service;

import com.stock.survive.dto.UserStockHoldingDto;
import com.stock.survive.entity.StockCategory;
import com.stock.survive.entity.StockItems;
import com.stock.survive.entity.TradeHistory;
import com.stock.survive.enumType.TradeType;
import com.stock.survive.repository.StockItemRepository;
import com.stock.survive.repository.TradeHistoryRepository;
import com.stock.survive.serviceImpl.AccountServiceImpl;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AccountServiceImplTest {

    @Mock
    private TradeHistoryRepository tradeHistoryRepository;

    @Mock
    private StockItemRepository stockItemRepository;

    @InjectMocks
    private AccountServiceImpl accountService;

    @Test
    @DisplayName("매수/매도가 섞여도 보유수량과 평단가를 올바르게 계산한다")
    void calculateHoldingAndAvgPrice() {
        StockItems item = new StockItems(
                1L,
                new StockCategory(10L, "IT", new ArrayList<>()),
                "테스트회사",
                "000001",
                new ArrayList<>(),
                new ArrayList<>()
        );
        when(stockItemRepository.findByTicker("000001")).thenReturn(item);

        List<TradeHistory> trades = List.of(
                TradeHistory.builder()
                        .tradeType(TradeType.BUY)
                        .price(1_000L)
                        .volume(10)
                        .build(),
                TradeHistory.builder()
                        .tradeType(TradeType.SELL)
                        .price(2_000L)
                        .volume(3)
                        .build()
        );
        when(tradeHistoryRepository.findByUserAndStockItem(99L, 1L)).thenReturn(trades);

        UserStockHoldingDto result = accountService.getUserStockHolding(99L, "000001");

        assertEquals(7, result.getQuantity());
        assertEquals(571.428, result.getAvgBuyPrice(), 1e-3);
    }

    @Test
    @DisplayName("거래가 없으면 보유수량 0, 평단가 0으로 반환한다")
    void emptyTradesReturnsZero() {
        StockItems item = new StockItems(
                2L,
                new StockCategory(11L, "Finance", new ArrayList<>()),
                "빈회사",
                "000002",
                new ArrayList<>(),
                new ArrayList<>()
        );
        when(stockItemRepository.findByTicker("000002")).thenReturn(item);
        when(tradeHistoryRepository.findByUserAndStockItem(1L, 2L)).thenReturn(List.of());

        UserStockHoldingDto result = accountService.getUserStockHolding(1L, "000002");

        assertEquals(0, result.getQuantity());
        assertEquals(0.0, result.getAvgBuyPrice());
    }
}
