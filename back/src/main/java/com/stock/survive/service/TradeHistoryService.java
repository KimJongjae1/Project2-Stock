package com.stock.survive.service;

import com.stock.survive.dto.UserAsset;
import com.stock.survive.dto.UserAssetDto;
import com.stock.survive.dto.UserTradeHistoryDto;

import java.util.List;


public interface TradeHistoryService {

    UserAssetDto getUserAssets(Long userNo);
    UserAsset processBuy(Long userNo, String ticker, Long price, Integer volume);
    UserAsset processSell(Long userNo, String ticker, Long price, Integer volume);
    List<UserTradeHistoryDto> getUserTradeHistory(Long userNo, String ticker);
}
