package com.stock.survive.dto;

import com.stock.survive.enumType.TradeType;
import lombok.*;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TradeHistoryDto {
    private Long itemNo;
    private String companyName;

    private TradeType tradeType;
    private Long price;
    private Integer volume;
    private LocalDateTime createdAt;
}