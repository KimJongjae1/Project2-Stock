package com.stock.survive.dto.tendency;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;

public record TendencyGameStartRequest(
        @Pattern(regexp = "^[A-Za-z0-9]{1,10}$", message = "ticker는 영문/숫자 10자 이하입니다.")
        String ticker,
        @Min(value = 1, message = "itemNo는 1 이상이어야 합니다.")
        Integer itemNo
) {
}
