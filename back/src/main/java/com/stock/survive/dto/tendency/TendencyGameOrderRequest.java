package com.stock.survive.dto.tendency;

import com.stock.survive.entity.tendency.TendencyGameTradeType;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

public record TendencyGameOrderRequest(
        @NotNull(message = "type은 필수입니다.")
        TendencyGameTradeType type,
        @Min(value = 1, message = "quantity는 1 이상이어야 합니다.")
        int quantity,
        String tradeDate
) {
}
