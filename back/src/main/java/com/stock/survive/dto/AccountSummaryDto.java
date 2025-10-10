package com.stock.survive.dto;

import lombok.*;

@Getter @Setter
@Builder
@NoArgsConstructor @AllArgsConstructor
public class AccountSummaryDto {
    private Long originalMoney;
    private Long cash;
    private Long haveStock;
    private Integer totalReward;

    private Long totalAsset;      // 총자산
    private Double returnPct;     // 수익률

    public static AccountSummaryDto from(com.stock.survive.entity.Account a) {
        long cash = a.getCash() == null ? 0L : a.getCash();
        long hold = a.getHaveStock() == null ? 0L : a.getHaveStock();
        long ori  = a.getOriginalMoney() == null ? 0L : a.getOriginalMoney();
        long total = cash + hold;

        Double pct = null;
        if (ori > 0) pct = ((total - ori) * 100.0) / ori;

        return AccountSummaryDto.builder()
                .originalMoney(ori)
                .cash(cash)
                .haveStock(hold)
                .totalReward(a.getTotalReward())
                .totalAsset(total)
                .returnPct(pct)
                .build();
    }
}
