package com.stock.survive.dto;


import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserTradeHistoryDto {

    private String tradeType;  // "BUY" or "SELL"
    private Long price;
    private Integer volume;
    private LocalDateTime createdAt; // 거래 날짜
}
