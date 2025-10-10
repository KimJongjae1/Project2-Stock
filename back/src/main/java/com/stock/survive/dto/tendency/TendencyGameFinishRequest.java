package com.stock.survive.dto.tendency;

import jakarta.validation.constraints.NotNull;

public record TendencyGameFinishRequest(
        @NotNull(message = "sessionId는 필수입니다.")
        Long sessionId
) {
}
