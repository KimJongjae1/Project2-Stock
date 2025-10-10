package com.stock.survive.service;

import com.stock.survive.dto.FavoriteDto;
import com.stock.survive.dto.PageRequestDto;
import com.stock.survive.dto.PageResponseDto;
import com.stock.survive.dto.StockEndDayDto;
import jakarta.transaction.Transactional;

import java.time.LocalDate;

@Transactional
public interface StockItemService {
    PageResponseDto<StockEndDayDto> getEndDayData(PageRequestDto pageRequestDto, LocalDate targetDate);

    LocalDate getLatestDataDate();

    FavoriteDto getFavoriteStatus(Long userId, String ticker);

}
