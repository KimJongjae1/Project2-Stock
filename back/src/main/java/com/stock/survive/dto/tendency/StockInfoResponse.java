package com.stock.survive.dto.tendency;

import java.time.LocalDate;
import java.util.List;

public record StockInfoResponse(
        String ticker,
        String companyName,
        LocalDate from,
        LocalDate to,
        List<PricePoint> prices
) {
    public record PricePoint(LocalDate date, Integer closePrice) {
    }
}
