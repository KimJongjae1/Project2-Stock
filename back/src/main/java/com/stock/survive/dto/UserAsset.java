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
public class UserAsset {
    private String tradeType;  // "BUY" or "SELL"
    private Long price;
    private Integer volume;
    private Long totalPrice;
    private LocalDateTime createdAt; // 거래 날짜

}
