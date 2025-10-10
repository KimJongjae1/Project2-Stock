package com.stock.survive.service;

import com.stock.survive.dto.ExtractKeywordsDto;
import com.stock.survive.dto.StockInfosDto;
import jakarta.transaction.Transactional;

import java.util.List;
import java.util.Optional;

@Transactional
public interface StockInfosService {

    boolean toggleFavorite(Long userId, Long itemNo);

    List<StockInfosDto> getStock( String ticker);

    ExtractKeywordsDto getKeywords(String ticker,ExtractKeywordsDto requestDto);
    
    Optional<Integer> getLatestEndPrice(Long itemNo);

}
