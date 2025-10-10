package com.stock.survive.service;

import com.stock.survive.dto.PageRequestDto;
import com.stock.survive.dto.PageResponseDto;
import com.stock.survive.dto.StockRealtimeDto;
import jakarta.transaction.Transactional;

@Transactional
public interface StockRealtimeService {

    PageResponseDto<StockRealtimeDto> getList(PageRequestDto pageRequestDto);
    

}