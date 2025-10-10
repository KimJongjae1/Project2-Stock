package com.stock.survive.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StockRealtimeDto {
    private String ticker;
    private String companyName;
    private Long volume;
    private Long marketCap;
    private String categoryName;
}