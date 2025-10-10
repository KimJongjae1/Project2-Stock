package com.stock.survive.serviceImpl;

import com.stock.survive.dto.tendency.TendencyGameFinishRequest;
import com.stock.survive.dto.tendency.TendencyGameOrderRequest;
import com.stock.survive.dto.tendency.TendencyGameResponse;
import com.stock.survive.dto.tendency.TendencyGameStateResponse;
import com.stock.survive.dto.tendency.TendencyGameStartRequest;
import com.stock.survive.entity.StockInfos;
import com.stock.survive.entity.StockItems;
import com.stock.survive.entity.User;
import com.stock.survive.entity.tendency.TendencyGameChart;
import com.stock.survive.entity.tendency.TendencyGameNews;
import com.stock.survive.entity.tendency.TendencyGameSession;
import com.stock.survive.entity.tendency.TendencyGameStatus;
import com.stock.survive.entity.tendency.TendencyGameTrade;
import com.stock.survive.entity.tendency.TendencyGameTradeType;
import com.stock.survive.entity.tendency.TendencyGameWeek;
import com.stock.survive.repository.tendency.GameChartsRepository;
import com.stock.survive.repository.StockInfosRepository;
import com.stock.survive.repository.StockItemRepository;
import com.stock.survive.repository.UserRepository;
import com.stock.survive.service.TendencyGameService;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

@Slf4j
@Service
@Transactional
@RequiredArgsConstructor
public class TendencyGameServiceImpl implements TendencyGameService {
    
    private static final int DEFAULT_INITIAL_CASH = 1_000_000;
    private static final int DEFAULT_MAX_WEEK = 10;
    private static final double VOLATILITY_THRESHOLD = 10.0d;
    private static final double YIELD_THRESHOLD = 3.0d;
    
    private final UserRepository userRepository;
    private final StockItemRepository stockItemRepository;
    private final StockInfosRepository stockInfosRepository;
    private final GameChartsRepository gameChartsRepository;
    
    private final ConcurrentHashMap<Long, TendencyGameSession> sessions = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Long, List<TendencyGameWeek>> weeksBySession = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<Long, List<TendencyGameTrade>> tradesBySession = new ConcurrentHashMap<>();
    private final AtomicLong sessionSeq = new AtomicLong(1L);
    private final AtomicLong tradeSeq = new AtomicLong(1L);
    
    @PersistenceContext
    private EntityManager entityManager;
    
    @Override
    public TendencyGameStateResponse start(Long userId, TendencyGameStartRequest request) {
        User user = fetchUser(userId);
        
        TendencyGameChart selectedChart = selectGameChart();
        StockItems stockItem = stockItemRepository.findById(selectedChart.getItemNo())
                .orElseThrow(() -> new IllegalStateException("게임 차트에 해당하는 종목이 없습니다."));
        
        List<StockInfos> timeline = stockInfosRepository.findByStockItem_ItemNoAndDateBetween(
                stockItem.getItemNo(), selectedChart.getStartDate(), selectedChart.getEndDate());
        
        if (timeline.size() < DEFAULT_MAX_WEEK) {
            throw new IllegalStateException("선택된 차트 기간의 데이터가 10주차 미만입니다. 데이터베이스를 확인하세요.");
        }
        
        long newId = sessionSeq.getAndIncrement();
        TendencyGameSession session = TendencyGameSession.builder()
                .id(newId)
                .user(user)
                .ticker(stockItem.getTicker())
                .datasetId(stockItem.getTicker() + "-" + selectedChart.getStartDate())
                .companyAlias(generateAlias(stockItem.getCompanyName()))
                .initialCash(DEFAULT_INITIAL_CASH)
                .cash(DEFAULT_INITIAL_CASH)
                .stockQuantity(0)
                .averageCost(0)
                .realizedProfit(0L)
                .currentWeek(1)
                .maxWeek(DEFAULT_MAX_WEEK)
                .status(TendencyGameStatus.IN_PROGRESS)
                .startedAt(LocalDateTime.now())
                .decisionElapsedMillis(0L)
                .volatileBuyCount(0)
                .volatileSellCount(0)
                .sellDominantWeekCount(0)
                .build();
        
        buildWeeks(session, timeline);
        sessions.put(session.getId(), session);
        
        return buildStateResponse(session);
    }
    
    @Override
    @Transactional(Transactional.TxType.SUPPORTS)
    public TendencyGameStateResponse getState(Long userId, Long sessionId) {
        TendencyGameSession session = fetchSession(userId, sessionId);
        return buildStateResponse(session);
    }
    
    @Override
    public TendencyGameStateResponse placeOrder(Long userId, Long sessionId, TendencyGameOrderRequest request) {
        TendencyGameSession session = fetchSession(userId, sessionId);
        ensureInProgress(session);
        
        TendencyGameWeek currentWeek = currentWeek(session);
        int price = safePrice(currentWeek.getClosePrice());
        
        if (request.type() == TendencyGameTradeType.BUY) {
            applyBuy(session, request.quantity(), price);
        } else {
            applySell(session, request.quantity(), price);
        }
        
        boolean volatileContext = Math.abs(currentWeek.getChangeRate()) >= VOLATILITY_THRESHOLD;
        if (volatileContext) {
            if (request.type() == TendencyGameTradeType.BUY) {
                session.setVolatileBuyCount(session.getVolatileBuyCount() + 1);
            } else {
                session.setVolatileSellCount(session.getVolatileSellCount() + 1);
            }
        }
        
        TendencyGameTrade trade = TendencyGameTrade.builder()
                .id(tradeSeq.getAndIncrement())
                .session(session)
                .type(request.type())
                .price(price)
                .quantity(request.quantity())
                .weekIndex(session.getCurrentWeek())
                .executedAt(LocalDateTime.now())
                .executedDate(LocalDate.parse(request.tradeDate()))
                .volatilityContext(volatileContext)
                .build();
        getTrades(session.getId()).add(trade);
        
        sessions.put(session.getId(), session);
        return buildStateResponse(session);
    }
    
    @Override
    public TendencyGameStateResponse proceedNextWeek(Long userId, Long sessionId) {
        TendencyGameSession session = fetchSession(userId, sessionId);
        ensureInProgress(session);
        
        if (session.getCurrentWeek() >= session.getMaxWeek()) {
            throw new IllegalStateException("이미 마지막 주차입니다. 다음 주로 이동할 수 없습니다.");
        }
        
        updateSellDominantMetric(session, session.getCurrentWeek());
        session.setCurrentWeek(session.getCurrentWeek() + 1);
        session.setDecisionElapsedMillis(Duration.between(session.getStartedAt(), LocalDateTime.now()).toMillis());
        sessions.put(session.getId(), session);
        return buildStateResponse(session);
    }
    
    @Override
    public TendencyGameResponse finish(Long userId, TendencyGameFinishRequest request) {
        TendencyGameSession session = fetchSession(userId, request.sessionId());
        ensureInProgress(session);
        
        if (!session.getCurrentWeek().equals(session.getMaxWeek())) {
            throw new IllegalStateException("10주차까지 진행해야 결과를 확인할 수 있습니다.");
        }
        
        updateSellDominantMetric(session, session.getCurrentWeek());
        List<TendencyGameWeek> weeks = getWeeks(session.getId());
        if (weeks.size() < session.getMaxWeek()) {
            throw new IllegalStateException("주간 데이터가 올바르지 않습니다.");
        }
        
        TendencyGameWeek finalWeek = weeks.get(session.getMaxWeek() - 1);
        int finalPrice = safePrice(finalWeek.getClosePrice());
        long stockValuation = (long) session.getStockQuantity() * finalPrice;
        long totalAsset = session.getCash() + stockValuation;
        double totalYield = calculateYield(session.getInitialCash(), totalAsset);
        
        session.setFinishedAt(LocalDateTime.now());
        session.setDecisionElapsedMillis(Duration.between(session.getStartedAt(), session.getFinishedAt()).toMillis());
        session.setStatus(TendencyGameStatus.FINISHED);
        sessions.put(session.getId(), session); // 최종 상태를 인메모리에 반영
        
        // 💡 MBTI 성향 지표 계산
        long totalGameTimeSeconds = session.getDecisionElapsedMillis() / 1000;
        int volatileTradeCount = session.getVolatileBuyCount() + session.getVolatileSellCount();
        int sellDominantWeekCount = session.getSellDominantWeekCount();
        
        // --- MBTI 계산 로직 ---
        int calculatedI = Math.min(100, Math.max(0, (volatileTradeCount * 10 + 10)));
        int calculatedE = 100 - calculatedI;
        
        int calculatedS = Math.min(100, Math.max(0, (int) (totalGameTimeSeconds / 2)));
        int calculatedN = 100 - calculatedS;
        
        int calculatedF = Math.min(100, Math.max(0, (sellDominantWeekCount * 10)));
        int calculatedT = 100 - calculatedF;
        
        double baseYield = 3.0;
        int calculatedJ = (int) Math.min(100, Math.max(0, (baseYield - totalYield) * 10));
        int calculatedP = 100 - calculatedJ;
        
        // 💡 최종 4자리 MBTI 문자열 (tendencyResult) 결정
        String calculatedResult = resolveMbtiResult(
                calculatedI, calculatedE,
                calculatedS, calculatedN,
                calculatedT, calculatedF,
                calculatedJ, calculatedP
        );
        
        // 💡 TendencyType과 Recommendation 결정 (복구)
        TendencyProfile finalProfile = resolveTendencyProfile(totalYield, volatileTradeCount, sellDominantWeekCount);
        
        // 💡 TendencyGameResponse에 계산된 모든 값을 담아 반환
        return TendencyGameResponse.builder()
                .sessionId(session.getId())
                .maxWeek(session.getMaxWeek())
                .finalWeek(session.getCurrentWeek())
                .totalAsset(Math.toIntExact(totalAsset))
                .realizedProfit(session.getRealizedProfit())
                .totalYield(totalYield)
                .yieldAboveThreshold(totalYield >= YIELD_THRESHOLD)
                .tendencyType(finalProfile.getType())
                .recommendation(finalProfile.getRecommendation())
                .decisionElapsedSeconds(totalGameTimeSeconds)
                .volatileBuyCount(session.getVolatileBuyCount())
                .volatileSellCount(session.getVolatileSellCount())
                .sellDominantWeekCount(session.getSellDominantWeekCount())
                .startedAt(session.getStartedAt())
                .finishedAt(session.getFinishedAt())
                .tendencyI(calculatedI)
                .tendencyE(calculatedE)
                .tendencyS(calculatedS)
                .tendencyN(calculatedN)
                .tendencyF(calculatedF)
                .tendencyT(calculatedT)
                .tendencyJ(calculatedJ)
                .tendencyP(calculatedP)
                .tendencyResult(calculatedResult)
                .build();
    }
    
    // 💡 MBTI 성향 지표 점수를 기반으로 최종 4자리 유형 문자열을 결정하는 헬퍼 메서드
    private String resolveMbtiResult(
            int i, int e,
            int s, int n,
            int t, int f,
            int j, int p
    ) {
        StringBuilder mbti = new StringBuilder();
        
        // 1. E/I 결정: E가 I보다 높으면 E, 같거나 낮으면 I (요구사항: 같으면 I)
        mbti.append(e > i ? 'E' : 'I');
        
        // 2. S/N 결정: S가 N보다 높거나 같으면 S, 아니면 N (요구사항: 같으면 S)
        mbti.append(s >= n ? 'S' : 'N');
        
        // 3. T/F 결정: T가 F보다 높으면 T, 아니면 F (요구사항: 같으면 F)
        mbti.append(t > f ? 'T' : 'F');
        
        // 4. J/P 결정: J가 P보다 높거나 같으면 J, 아니면 P (요구사항: 같으면 J)
        mbti.append(j >= p ? 'J' : 'P');
        
        return mbti.toString();
    }
    
    // ===== In-memory helpers (start/state/order/nextWeek에서 사용) =====
    private List<TendencyGameWeek> getWeeks(Long sessionId) {
        return weeksBySession.computeIfAbsent(sessionId, k -> new ArrayList<>());
    }
    
    private List<TendencyGameTrade> getTrades(Long sessionId) {
        return tradesBySession.computeIfAbsent(sessionId, k -> new ArrayList<>());
    }
    
    private List<TendencyGameTrade> getTradesByWeek(Long sessionId, int weekIndex) {
        return getTrades(sessionId).stream()
                .filter(t -> t.getWeekIndex() == weekIndex)
                .sorted(Comparator.comparing(TendencyGameTrade::getExecutedAt))
                .collect(Collectors.toList());
    }
    
    private void buildWeeks(TendencyGameSession session, List<StockInfos> selected) {
        List<TendencyGameWeek> list = new ArrayList<>();
        
        int dataStep = selected.size() / session.getMaxWeek();
        if (dataStep == 0) {
            throw new IllegalStateException("주간 데이터를 생성할 수 없습니다.");
        }
        
        for (int i = 0; i < session.getMaxWeek(); i++) {
            StockInfos current = selected.get(i * dataStep);
            int closePrice = safePrice(Optional.ofNullable(current.getEndPrice()).orElse(0));
            int previousPrice = closePrice;
            if (i > 0) {
                previousPrice = safePrice(Optional.ofNullable(selected.get((i - 1) * dataStep).getEndPrice()).orElse(closePrice));
            }
            int change = closePrice - previousPrice;
            double changeRate = previousPrice == 0 ? 0.0 : (change * 100.0) / previousPrice;
            
            TendencyGameWeek week = TendencyGameWeek.builder()
                    .session(session)
                    .weekIndex(i + 1)
                    .startDate(current.getDate())
                    .endDate(current.getDate().plusDays(6))
                    .closePrice(closePrice)
                    .changePrice(change)
                    .changeRate(changeRate)
                    .keywords(generateKeywords(i + 1))
                    .news(generateNews(current.getDate(), i + 1))
                    .build();
            list.add(week);
        }
        weeksBySession.put(session.getId(), list);
    }
    
    private List<String> generateKeywords(int weekIndex) {
        List<String> keywords = new ArrayList<>();
        for (int i = 1; i <= 5; i++) {
            keywords.add("Keyword " + weekIndex + "-" + i);
        }
        return keywords;
    }
    
    private List<TendencyGameNews> generateNews(LocalDate baseDate, int weekIndex) {
        List<TendencyGameNews> news = new ArrayList<>();
        for (int i = 1; i <= 3; i++) {
            news.add(TendencyGameNews.builder()
                    .title("Week " + weekIndex + " 뉴스 " + i)
                    .url("https://example.com/news/" + weekIndex + "/" + i)
                    .summary(baseDate + " 관련 요약 " + i)
                    .build());
        }
        return news;
    }
    
    private String generateAlias(String companyName) {
        char suffix = (char) (ThreadLocalRandom.current().nextInt(0, 26) + 'A');
        return "익명 기업 " + suffix;
    }
    
    private TendencyGameChart selectGameChart() {
        List<TendencyGameChart> charts = gameChartsRepository.findAll();
        if (charts.isEmpty()) {
            throw new IllegalStateException("게임 차트 데이터가 존재하지 않습니다. 게임을 시작할 수 없습니다.");
        }
        int randomIndex = ThreadLocalRandom.current().nextInt(charts.size());
        return charts.get(randomIndex);
    }
    
    private User fetchUser(Long userId) {
        return userRepository.findById(userId.longValue())
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));
    }
    
    private TendencyGameSession fetchSession(Long userId, Long sessionId) {
        TendencyGameSession s = sessions.get(sessionId);
        if (s == null || s.getUser() == null || !s.getUser().getId().equals(userId.longValue())) {
            throw new IllegalArgumentException("진행 중인 게임 세션을 찾을 수 없습니다.");
        }
        return s;
    }
    
    private void ensureInProgress(TendencyGameSession session) {
        if (session.getStatus() != TendencyGameStatus.IN_PROGRESS) {
            throw new IllegalStateException("종료된 게임입니다. 작업을 수행할 수 없습니다.");
        }
    }
    
    private TendencyGameWeek currentWeek(TendencyGameSession session) {
        List<TendencyGameWeek> weeks = getWeeks(session.getId());
        if (weeks.size() < session.getCurrentWeek()) {
            throw new IllegalStateException("주간 데이터가 부족합니다.");
        }
        return weeks.get(session.getCurrentWeek() - 1);
    }
    
    private void applyBuy(TendencyGameSession session, int quantity, int price) {
        long cost = (long) quantity * price;
        if (cost > session.getCash()) {
            throw new IllegalArgumentException("보유 현금이 부족합니다.");
        }
        long remaining = session.getCash() - cost;
        if (remaining < 0 || remaining > Integer.MAX_VALUE) {
            throw new IllegalArgumentException("현금 계산 중 오버플로우가 발생했습니다.");
        }
        
        int previousQuantity = session.getStockQuantity();
        int newQuantity = previousQuantity + quantity;
        long totalCostBefore = (long) previousQuantity * session.getAverageCost();
        int newAverage = newQuantity == 0 ? 0 : (int) Math.round((double) (totalCostBefore + cost) / newQuantity);
        
        session.setCash((int) remaining);
        session.setStockQuantity(newQuantity);
        session.setAverageCost(newAverage);
    }
    
    private void applySell(TendencyGameSession session, int quantity, int price) {
        if (session.getStockQuantity() < quantity) {
            throw new IllegalArgumentException("보유 수량보다 많이 매도할 수 없습니다.");
        }
        long revenue = (long) quantity * price;
        long newCash = session.getCash() + revenue;
        if (newCash > Integer.MAX_VALUE) {
            throw new IllegalArgumentException("현금 계산 중 오버플로우가 발생했습니다.");
        }
        
        int remaining = session.getStockQuantity() - quantity;
        long profit = (long) (price - session.getAverageCost()) * quantity;
        
        session.setCash((int) newCash);
        session.setStockQuantity(remaining);
        session.setRealizedProfit(session.getRealizedProfit() + profit);
        if (remaining == 0) {
            session.setAverageCost(0);
        }
    }
    
    private void updateSellDominantMetric(TendencyGameSession session, int weekIndex) {
        List<TendencyGameTrade> trades = getTradesByWeek(session.getId(), weekIndex);
        if (trades.isEmpty()) {
            return;
        }
        int buyQty = trades.stream()
                .filter(trade -> trade.getType() == TendencyGameTradeType.BUY)
                .mapToInt(TendencyGameTrade::getQuantity)
                .sum();
        int sellQty = trades.stream()
                .filter(trade -> trade.getType() == TendencyGameTradeType.SELL)
                .mapToInt(TendencyGameTrade::getQuantity)
                .sum();
        if (sellQty > buyQty) {
            session.setSellDominantWeekCount(session.getSellDominantWeekCount() + 1);
        }
    }
    
    private TendencyGameStateResponse buildStateResponse(TendencyGameSession session) {
        List<TendencyGameWeek> weeks = getWeeks(session.getId());
        weeks.sort(Comparator.comparingInt(TendencyGameWeek::getWeekIndex));
        
        TendencyGameWeek currentWeek = weeks.get(Math.max(0, session.getCurrentWeek() - 1));
        int price = safePrice(currentWeek.getClosePrice());
        
        int stockValuation = session.getStockQuantity() * price;
        long totalAsset = session.getCash() + stockValuation;
        double totalYield = calculateYield(session.getInitialCash(), totalAsset);
        
        TendencyGameStateResponse.Summary summary = new TendencyGameStateResponse.Summary(
                session.getCash(),
                session.getStockQuantity(),
                stockValuation,
                Math.toIntExact(totalAsset),
                session.getRealizedProfit(),
                totalYield
        );
        
        List<String> labels = weeks.stream()
                .map(w -> w.getStartDate().toString())
                .collect(Collectors.toList());
        List<Integer> prices = weeks.stream().map(w -> safePrice(w.getClosePrice())).collect(Collectors.toList());
        
        LocalDate nextDate = null;
        if (session.getCurrentWeek() < session.getMaxWeek()) {
            nextDate = weeks.get(session.getCurrentWeek()).getStartDate();
        }
        
        TendencyGameStateResponse.ChartData chart = new TendencyGameStateResponse.ChartData(labels, prices);
        TendencyGameStateResponse.StockOverviewBlock stockOverview = new TendencyGameStateResponse.StockOverviewBlock(
                session.getCompanyAlias(),
                session.getTicker(),
                currentWeek.getStartDate(),
                nextDate,
                price,
                currentWeek.getChangePrice(),
                currentWeek.getChangeRate(),
                chart,
                session.getCurrentWeek().equals(session.getMaxWeek())
        );
        
        long evaluationProfit = (long) session.getStockQuantity() * (price - session.getAverageCost());
        double evaluationRate = session.getAverageCost() == 0 ? 0.0 : ((double) price - session.getAverageCost()) / session.getAverageCost() * 100.0;
        int maxAffordable = price == 0 ? 0 : session.getCash() / price;
        
        TendencyGameStateResponse.TradePanelBlock tradePanel = new TendencyGameStateResponse.TradePanelBlock(
                session.getStockQuantity(),
                stockValuation,
                session.getAverageCost(),
                evaluationProfit,
                evaluationRate,
                maxAffordable,
                session.getStockQuantity()
        );
        
        List<TendencyGameTrade> trades = getTrades(session.getId());
        List<TendencyGameStateResponse.TradeRecord> tradeRecords = trades.stream()
                .sorted(Comparator.comparing(TendencyGameTrade::getExecutedAt).reversed())
                .map(trade -> new TendencyGameStateResponse.TradeRecord(
                        trade.getId(),
                        trade.getType(),
                        trade.getPrice(),
                        trade.getQuantity(),
                        trade.getExecutedDate(),
                        trade.getExecutedAt()
                ))
                .collect(Collectors.toList());
        
        TendencyGameStateResponse.Highlights highlights = new TendencyGameStateResponse.Highlights(
                currentWeek.getKeywords(),
                currentWeek.getNews().stream()
                        .map(n -> new TendencyGameStateResponse.NewsItem(n.getTitle(), n.getUrl(), n.getSummary()))
                        .collect(Collectors.toList()),
                currentWeek.getStartDate() + " 주차 키워드 요약"
        );
        
        return new TendencyGameStateResponse(
                session.getId(),
                session.getCurrentWeek(),
                session.getMaxWeek(),
                session.getStatus() == TendencyGameStatus.FINISHED,
                summary,
                stockOverview,
                tradePanel,
                tradeRecords,
                highlights
        );
    }
    
    private int safePrice(Integer value) {
        return value == null ? 0 : value;
    }
    
    private double calculateYield(int initialCash, long totalAsset) {
        if (initialCash == 0) {
            return 0.0;
        }
        return ((double) totalAsset - initialCash) / initialCash * 100.0;
    }
    
    // 💡 TendencyProfile 결정 로직 복구
    private TendencyProfile resolveTendencyProfile(double totalYield, int volatileTrades, int sellDominantWeeks) {
        if (totalYield >= 5.0 || volatileTrades >= 6) {
            return new TendencyProfile("AGGRESSIVE", "공격적인 성향으로 적극적인 투자를 선호합니다.");
        }
        if (sellDominantWeeks >= 5 || totalYield < 0) {
            return new TendencyProfile("DEFENSIVE", "안정성을 중시하며 위험을 회피하는 성향입니다.");
        }
        return new TendencyProfile("BALANCED", "수익과 리스크를 균형 있게 고려하는 성향입니다.");
    }
    
    // 💡 TendencyProfile 클래스 복구
    private static class TendencyProfile {
        private final String type;
        private final String recommendation;
        
        public TendencyProfile(String type, String recommendation) {
            this.type = type;
            this.recommendation = recommendation;
        }
        
        public String getType() {
            return type;
        }
        
        public String getRecommendation() {
            return recommendation;
        }
    }
}