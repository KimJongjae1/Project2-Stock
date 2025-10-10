package com.stock.survive.dto;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class StockEndDayDto {
    private String ticker;
    private String companyName;
    private Integer startPrice;
    private Integer endPrice;
    private Double rate;
    private Long volume;
    private String categoryName;
    private Long marketCap;

    // 쿼리에 맞는 생성자로 수정
    public StockEndDayDto(String ticker, String companyName, Integer startPrice,
                          Integer endPrice, Long volume, String categoryName, Long marketCap) {
        this.ticker = ticker;
        this.companyName = companyName;
        this.startPrice = startPrice;
        this.endPrice = endPrice;
        this.volume = volume;
        this.categoryName = categoryName;
        this.marketCap = marketCap;
    }
}