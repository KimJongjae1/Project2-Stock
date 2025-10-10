package com.stock.survive.controller.tendency;

import com.stock.survive.dto.tendency.StockInfoResponse;
import com.stock.survive.entity.StockInfos;
import com.stock.survive.repository.StockInfosRepository;
import com.stock.survive.repository.StockItemRepository;
import jakarta.validation.constraints.Pattern;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequiredArgsConstructor
public class StockInfoQueryController {

    private final StockItemRepository stockItemRepository;
    private final StockInfosRepository stockInfosRepository;

    @GetMapping("/api/stocks/info/{ticker}")
    public ResponseEntity<StockInfoResponse> stockInfo(
            @PathVariable
            @Pattern(regexp = "^[A-Za-z0-9]{1,10}$", message = "ticker는 영문/숫자 10자 이하입니다.") String ticker,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
            @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to
    ) {
        var item = stockItemRepository.findAll().stream()
                .filter(stock -> stock.getTicker().equalsIgnoreCase(ticker))
                .findFirst()
                .orElseThrow(() -> new IllegalArgumentException("해당 티커의 종목을 찾을 수 없습니다."));

        List<StockInfos> infos = stockInfosRepository.findRecent6YearsByTicker(item.getTicker());
        if (from != null) {
            infos = infos.stream().filter(info -> !info.getDate().isBefore(from)).collect(Collectors.toList());
        }
        if (to != null) {
            infos = infos.stream().filter(info -> !info.getDate().isAfter(to)).collect(Collectors.toList());
        }

        if (infos.isEmpty()) {
            return ResponseEntity.ok(new StockInfoResponse(
                    item.getTicker(),
                    item.getCompanyName(),
                    from,
                    to,
                    List.of()
            ));
        }

        LocalDate minDate = infos.get(0).getDate();
        LocalDate maxDate = infos.get(infos.size() - 1).getDate();

        List<StockInfoResponse.PricePoint> prices = infos.stream()
                .map(info -> new StockInfoResponse.PricePoint(info.getDate(), info.getEndPrice()))
                .collect(Collectors.toList());

        return ResponseEntity.ok(new StockInfoResponse(
                item.getTicker(),
                item.getCompanyName(),
                Optional.ofNullable(from).orElse(minDate),
                Optional.ofNullable(to).orElse(maxDate),
                prices
        ));
    }
}
