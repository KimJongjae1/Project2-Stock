package com.stock.survive.controller;

import com.stock.survive.dto.FavoriteDto;
import com.stock.survive.dto.PageRequestDto;
import com.stock.survive.dto.PageResponseDto;
import com.stock.survive.dto.StockEndDayDto;
import com.stock.survive.service.StockItemService;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/stock")
@RequiredArgsConstructor
@Log4j2
public class StockItemsController {

    private final StockItemService stockItemService;

    // 장 마감 데이터 조회 (페이지네이션 적용)
    @GetMapping("/endDay")
    public ResponseEntity<PageResponseDto<StockEndDayDto>> getEndOfDayData(
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "21") int size
    ) {

        // date가 null이면 DB에서 가장 최신 날짜 사용
        LocalDate targetDate = (date != null) ? date : stockItemService.getLatestDataDate();

        PageRequestDto pageRequestDto = PageRequestDto.builder()
                .page(page)
                .size(size)
                .build();

        PageResponseDto<StockEndDayDto> response = stockItemService.getEndDayData(pageRequestDto, targetDate);



        return ResponseEntity.ok(response);
    }

    @GetMapping("/favorites/{ticker}")
    public ResponseEntity<FavoriteDto> getFavorite(
            @AuthenticationPrincipal Long userId,
            @PathVariable String ticker) {

        FavoriteDto dto = stockItemService.getFavoriteStatus(userId, ticker);
        return ResponseEntity.ok(dto);
    }

}
