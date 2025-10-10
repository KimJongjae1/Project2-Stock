package com.stock.survive.dto;


import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserAssetDto {

    private Long cash;
    private Long haveStock;
    private Long originalMoney;

}
