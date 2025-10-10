package com.stock.survive.serviceImpl;

import com.stock.survive.dto.ExtractKeywordsDto;
import com.stock.survive.dto.StockInfosDto;
import com.stock.survive.dto.TopNewsArticleDto;
import com.stock.survive.entity.StockInfos;
import com.stock.survive.entity.StockItems;
import com.stock.survive.entity.User;
import com.stock.survive.repository.StockInfosRepository;
import com.stock.survive.repository.StockItemRepository;
import com.stock.survive.repository.UserRepository;
import com.stock.survive.service.StockInfosService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.server.ResponseStatusException;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

@Slf4j
@Service
@RequiredArgsConstructor
public class StockInfosServiceImpl implements StockInfosService {

    private final StockInfosRepository stockInfosRepository;
    private final StockItemRepository stockItemRepository;
    private final WebClient webClient; // WebClient 주입
    private final UserRepository userRepository;


    @Value("${keywords.api.url}")
    private String keywordsApiUrl; // application.properties나 application.yml에서 설정

    @Override
    public boolean toggleFavorite(Long userId, Long itemNo) {
        User u = userRepository.findWithFavoritesById(userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "USER_NOT_FOUND"));

        StockItems item = stockItemRepository.findById(itemNo)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "ITEM_NOT_FOUND"));

        Set<StockItems> favs = u.getFavorites();
        if (favs.contains(item)) {
            favs.remove(item);
            return false;
        } else {
            favs.add(item);
            return true;
        }
    }

    @Override
    public List<StockInfosDto> getStock( String ticker) {
        List<StockInfos> infos = stockInfosRepository.findRecent6YearsByTicker(ticker);

        return infos.stream()
                .map(stockInfos -> StockInfosDto.builder()
                        .ticker(stockInfos.getStockItem().getTicker())
                        .companyName(stockInfos.getStockItem().getCompanyName())
                        .endPrice(stockInfos.getEndPrice())
                        .date(stockInfos.getDate())
                        .build())
                .toList();
    }


    @Override
    public ExtractKeywordsDto getKeywords(String ticker, ExtractKeywordsDto requestDto) {
        // 1️⃣ DB에서 companyName 조회
        String companyName = stockItemRepository.findCompanyNameByTicker(ticker)
                .map(StockItems::getCompanyName)
                .orElseThrow(() -> new IllegalArgumentException("존재하지 않는 ticker: " + ticker));

        // 2️⃣ 프론트에서 받은 값 활용 (없으면 기본값)
        String startDate = requestDto.getStartDate() != null
                ? requestDto.getStartDate().replace("-", "")
                : LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String endDate = requestDto.getEndDate() != null
                ? requestDto.getEndDate().replace("-", "")
                : startDate;
        int topKeywords = requestDto.getTopKeywords() != null ? requestDto.getTopKeywords() : 10;
        boolean useAiFilter = requestDto.isUseAiFilter();
        String analysis = requestDto.getAiAnalysis() != null ? requestDto.getAiAnalysis() : "";


        // 3️⃣ 외부 API 호출 payload 구성
        var payload = Map.of(
                "company_name", companyName,
                "start_date", startDate,
                "end_date", endDate,
                "top_keywords", topKeywords,
                "use_ai_filter", useAiFilter,
                "ai_analysis",analysis
        );

        // 4️⃣ WebClient로 외부 API 호출
        Map response = webClient.post()
                .uri(keywordsApiUrl + "/extract-keywords/ticker")
                .bodyValue(payload)
                .retrieve()
                .bodyToMono(Map.class) // 외부 API가 JSON으로 반환
                .block(); // 동기 호출

        // 5️⃣ 결과 매핑
        Map<String, Integer> keywords = (Map<String, Integer>) response.get("keywords");
        List<Map<String, Object>> topNews = (List<Map<String, Object>>) response.get("top_news_articles");
        List<TopNewsArticleDto> topNewsArticles = topNews.stream().map(news -> TopNewsArticleDto.builder()
                        .title((String) news.get("title"))
                        .date((String) news.get("date"))
                        .url((String) news.get("url"))
                        .matchedKeywordsCount((Integer) news.get("matched_keywords_count"))
                        .matchedKeywords((List<String>) news.get("matched_keywords"))
                        .build())
                .toList();

        String aiAnalysis = (String) response.get("ai_analysis");
        Map<String, Integer> dailyNewsCount = (Map<String, Integer>) response.get("daily_news_count");


        // 6️⃣ 최종 DTO 반환
        return ExtractKeywordsDto.builder()
                .companyName(companyName)
                .startDate(startDate)
                .endDate(endDate)
                .topKeywords(topKeywords)
                .useAiFilter(useAiFilter)
                .keywords(keywords)
                .topNewsArticles(topNewsArticles)
                .aiAnalysis(aiAnalysis)
                .dailyNewsCount(dailyNewsCount)
                .build();
    }
    
    @Override
    public Optional<Integer> getLatestEndPrice(Long itemNo) {
        return stockInfosRepository.findLatestEndPriceByItemNo(itemNo);
    }
}
