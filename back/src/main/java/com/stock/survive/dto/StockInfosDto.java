package com.stock.survive.dto;


import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StockInfosDto {
    private String ticker;
    private String companyName;
    private Integer endPrice;
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate date;

}
