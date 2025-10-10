package com.stock.survive.dto.tendency;

import lombok.Builder;
import java.time.LocalDateTime;

@Builder
public record TendencyGameResponse(
        Long sessionId,
        int maxWeek,
        int finalWeek,
        int totalAsset,
        long realizedProfit,
        double totalYield,
        boolean yieldAboveThreshold,
        String tendencyType,
        String recommendation,
        long decisionElapsedSeconds,
        int volatileBuyCount,
        int volatileSellCount,
        int sellDominantWeekCount,
        LocalDateTime startedAt,
        LocalDateTime finishedAt,
        
        Integer tendencyI,
        Integer tendencyE,
        Integer tendencyS,
        Integer tendencyN,
        Integer tendencyF,
        Integer tendencyT,
        Integer tendencyJ,
        Integer tendencyP,
        String tendencyResult
) {
}