package com.stock.survive.controller;

import com.stock.survive.dto.PageRequestDto;
import com.stock.survive.dto.PageResponseDto;
import com.stock.survive.dto.StockRealtimeDto;
import com.stock.survive.service.StockRealtimeService;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/stock")
@RequiredArgsConstructor
@Log4j2
public class StockRealtimeController {

    private final StockRealtimeService stockRealtimeService;

    @GetMapping("/realtime")
    public PageResponseDto<StockRealtimeDto> getStockItems(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "21") int size
    ) {
        PageRequestDto pageRequestDto = PageRequestDto.builder()
                .page(page)
                .size(size)
                .build();

        return stockRealtimeService.getList(pageRequestDto);
    }
}

