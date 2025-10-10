package com.stock.survive.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserStockHoldingDto {
    private String ticker;
    private int quantity; // 현재 보유 수량
    private double avgBuyPrice;
}
