package com.stock.survive.dto.tendency;

import com.stock.survive.entity.tendency.TendencyGameTradeType;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

public record TendencyGameStateResponse(
        Long sessionId,
        int week,
        int maxWeek,
        boolean finished,
        Summary summary,
        StockOverviewBlock stockOverview,
        TradePanelBlock tradePanel,
        List<TradeRecord> trades,
        Highlights highlights
) {
    public record Summary(
            int cash,
            int stockQuantity,
            int stockValuation,
            int totalAsset,
            long realizedProfit,
            double totalYield
    ) {
    }

    public record StockOverviewBlock(
            String companyAlias,
            String ticker,
            LocalDate currentDate,
            LocalDate nextDate,
            int price,
            int change,
            double changeRate,
            ChartData chart,
            boolean finalWeek
    ) {
    }

    public record ChartData(
            List<String> labels,
            List<Integer> prices
    ) {
    }

    public record TradePanelBlock(
            int stockCount,
            int stockValuation,
            int averageCost,
            long evaluationProfit,
            double evaluationRate,
            int maxAffordable,
            int maxSellable
    ) {
    }

    public record TradeRecord(
            Long tradeId,
            TendencyGameTradeType type,
            int price,
            int quantity,
            LocalDate tradeDate,
            LocalDateTime executedAt
    ) {
    }

    public record Highlights(
            List<String> keywords,
            List<NewsItem> news,
            String summary
    ) {
    }

    public record NewsItem(
            String title,
            String url,
            String summary
    ) {
    }
}
