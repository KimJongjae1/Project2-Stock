package com.stock.survive.service;

import com.stock.survive.dto.UserStockHoldingDto;
import com.stock.survive.entity.TradeHistory;

import java.util.List;

public interface AccountService {

    UserStockHoldingDto getUserStockHolding(Long userNo, String ticker);

    int calculateHoldingQuantity(List<TradeHistory> trades);
}
