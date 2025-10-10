import { useEffect, useState, useMemo } from "react";
import { useParams, useNavigate } from "react-router";
import ChartHeader from "../components/Chart/ChartHeader";
import TimeTerm from "../components/Chart/TimeTerm";
import NewsCard from "../components/NewsCard";
import ChartMain from "../components/Chart/ChartMain";
import DateModal from "./DateModal";
import ChartNews from "../components/Chart/ChartNews";
import LoginRequiredModal from "../components/TendencyGame/LoginRequiredModal";

import {
  TermText,
  type Term,
  type News,
  type StockInfos,
  type Keyword,
} from "../types/StockInfos";

import {
  extractKeywords,
  fetchFavorite,
  getStockInfo,
} from "../api/StockInfosApi";

import {
  getEndDayWithPage,
  getStockRealtimeWithPage,
} from "../api/StockRealtimeApi";
import type {
  EndDay,
  BackendRealtime,
  PageResponseDto,
} from "../types/StockRealtime";
import { useRealtimeStore } from "../stores/RealtimeState";
import { useAuth } from "../stores/auth";
import TradeKeywords from "../components/Trade/TradeKeywords";
import TradeCard from "../components/Trade/TradeCard";
import {
  type UserAsset,
  type UserStockHoldingDto,
  type UserTradeHistory,
} from "../types/Trade";
import TradeHistory from "../components/Trade/TradeHistory";
import {
  getUserStockHolding,
  userAsset,
  userTradeHistory,
} from "../api/TradeApi"; // userAsset import

function isMarketOpen(): boolean {
  const now = new Date();
  const totalMinutes = now.getHours() * 60 + now.getMinutes();
  return totalMinutes >= 9 * 60 && totalMinutes <= 15 * 60 + 30;
}

function TradeInfoPage() {
  const { ticker } = useParams<{ ticker: string }>();
  const navigate = useNavigate();
  const marketOpen = isMarketOpen();
  const [userTrade, setUserTrade] = useState<UserAsset>({
    cash: 0,
    haveStock: 0,
    originalMoney: 0,
  }); // 초기값 설정
  // 자산 정보 상태

  const realtime = useRealtimeStore((s) => s.data[ticker ?? ""]);
  const connectRealtime = useRealtimeStore((s) => s.connect);

  const [backendInfo, setBackendInfo] = useState<BackendRealtime | null>(null);
  const [endDayData, setEndDayData] = useState<EndDay | null>(null);

  const [selectedTerm, setSelectedTerm] = useState<Term>(TermText[0]);
  const [stockData, setStockData] = useState<StockInfos[]>([]);
  const [customModalOpen, setCustomModalOpen] = useState(false);
  const [customStartDate, setCustomStartDate] = useState<Date | null>(null);
  const [customEndDate, setCustomEndDate] = useState<Date | null>(null);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [news, setNews] = useState<News[]>([]);
  const [aiAnalysis, setAiAnalysis] = useState<string>("");
  const [userHolding, setUserHolding] = useState<UserStockHoldingDto | null>(
    null
  );

  const [isFavorite, setIsFavorite] = useState(false);

  const { user } = useAuth();
  const isLoggedIn = Boolean(user);
  const [loginRequiredModal, setLoginRequiredModal] = useState(false);

  const [tradeHistory, setTradeHistory] = useState<UserTradeHistory[]>([]);
  const [dailyNewsCount, setDailyNewsCount] = useState<Record<string, number>>(
    {}
  );

  const handleGoHome = () => {
    navigate("/");
  };

  const handleCloseLoginModal = () => {
    setLoginRequiredModal(false);
  };

  // 로그인하지 않은 사용자는 모달을 띄우고 홈으로 리다이렉트
  useEffect(() => {
    if (!user) {
      setLoginRequiredModal(true);
      // 모달을 보여준 후 홈으로 이동
      const timer = setTimeout(() => {
        navigate("/");
      }, 2000); // 2초 후 홈으로 이동

      return () => clearTimeout(timer);
    }
  }, [user, navigate]);

  useEffect(() => {
    if (!isLoggedIn || !ticker) return;
    (async () => {
      try {
        const res = await userTradeHistory(ticker);
        setTradeHistory(res); // API에서 받은 실제 거래 내역
      } catch (err) {
        console.error("사용자 거래 내역 로드 실패:", err);
        setTradeHistory([]);
      }
    })();
  }, [ticker, isLoggedIn]);

  // 사용자 자산 정보 가져오기
  useEffect(() => {
    if (!isLoggedIn) return; // 로그인 상태일 때만 실행
    (async () => {
      try {
        const res = await userAsset(); // 실제 데이터 호출
        setUserTrade(res); // 자산 데이터를 상태에 저장
      } catch (err) {
        console.error("사용자 자산 데이터 가져오기 실패:", err);
      }
    })();
  }, [isLoggedIn]); // 로그인 상태가 변경될 때마다 호출

  // 관심목록 상태 조회
  useEffect(() => {
    if (!isLoggedIn || !ticker) return;
    (async () => {
      try {
        const fav = await fetchFavorite(ticker);
        setIsFavorite(fav);
      } catch (err) {
        console.error("즐겨찾기 상태 로드 실패:", err);
      }
    })();
  }, [ticker, isLoggedIn]);

  // WS 연결
  useEffect(() => {
    if (marketOpen) connectRealtime();
  }, [marketOpen, connectRealtime]);

  // 장중 데이터
  useEffect(() => {
    if (!ticker || !marketOpen) return;
    (async () => {
      try {
        const res: PageResponseDto<BackendRealtime> =
          await getStockRealtimeWithPage(1, 1000);
        const stock = res.dtoList.find((s) => s.ticker === ticker);
        if (stock) setBackendInfo(stock);
      } catch (err) {
        console.error("❌ BackendRealtime 로드 실패:", err);
      }
    })();
  }, [ticker, marketOpen]);

  // 종가 데이터
  useEffect(() => {
    if (!ticker || marketOpen) return;
    (async () => {
      try {
        const res: PageResponseDto<EndDay> = await getEndDayWithPage(1, 1000);
        const stock = res.dtoList.find((s) => s.ticker === ticker);
        if (stock) setEndDayData(stock);
      } catch (err) {
        console.error("❌ 종가 데이터 로드 실패:", err);
      }
    })();
  }, [ticker, marketOpen]);

  // 차트 기간 계산
  const { startDate, endDate } = useMemo(() => {
    const today = new Date();
    let start: Date;
    let end: Date = today;
    if (
      selectedTerm.text === "사용자 지정" &&
      customStartDate &&
      customEndDate
    ) {
      start = customStartDate;
      end = customEndDate;
    } else {
      start = new Date(today);
      switch (selectedTerm.text) {
        case "1 주":
          start.setDate(start.getDate() - 7);
          break;
        case "1개월":
          start.setMonth(start.getMonth() - 1);
          break;
        case "3개월":
          start.setMonth(start.getMonth() - 3);
          break;
        case "6개월":
          start.setMonth(start.getMonth() - 6);
          break;
        case "1 년":
          start.setFullYear(start.getFullYear() - 1);
          break;
        case "3 년":
          start.setFullYear(start.getFullYear() - 3);
          break;
        case "5 년":
          start.setFullYear(start.getFullYear() - 5);
          break;
        default:
          start.setDate(start.getDate() - 7);
      }
    }
    return { startDate: start, endDate: end };
  }, [selectedTerm, customStartDate, customEndDate]);

  // 주식 데이터
  useEffect(() => {
    if (!ticker) return;
    (async () => {
      const data = await getStockInfo(ticker);
      setStockData(data);
    })();
  }, [ticker]);

  const latestStock = useMemo(() => {
    if (!stockData.length) return null;
    return stockData.reduce((prev, curr) =>
      new Date(curr.date) > new Date(prev.date) ? curr : prev
    );
  }, [stockData]);

  const filteredData = useMemo(() => {
    if (!startDate || !endDate) return [];
    return stockData
      .filter(
        (d) => new Date(d.date) >= startDate && new Date(d.date) <= endDate
      )
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());
  }, [stockData, startDate, endDate]);

  useEffect(() => {
    if (!isLoggedIn || !ticker) return;
    (async () => {
      try {
        const res = await getUserStockHolding(ticker);
        setUserHolding(res);
      } catch (err) {
        console.error("보유 수량 로드 실패:", err);
        setUserHolding(null);
      }
    })();
  }, [ticker, isLoggedIn]);

  // 키워드 & 뉴스 & 분석
  useEffect(() => {
    if (!latestStock || !startDate || !endDate) return;

    (async () => {
      try {
        const response = await extractKeywords(
          latestStock.ticker,
          latestStock.companyName,
          startDate.toISOString().slice(0, 10),
          endDate.toISOString().slice(0, 10)
        );

        // keywords는 Record<string, number> -> Keyword[]로 변환
        const keywordList: Keyword[] = Object.entries(response.keywords).map(
          ([keyword, count]) => ({ keyword, count })
        );

        setKeywords(keywordList);
        setNews(response.topNewsArticles ?? []);
        setAiAnalysis(response.aiAnalysis);
        setDailyNewsCount(response.dailyNewsCount ?? {}); // 새로 추가한 상태
        console.log("📰 dailyNewsCount:", response.dailyNewsCount);
      } catch (err) {
        console.error("키워드 & 뉴스 추출 실패:", err);
        setKeywords([]);
        setNews([]);
        setAiAnalysis("");
        setDailyNewsCount({});
      }
    })();
  }, [latestStock, startDate, endDate]);

  // 실시간 가격 반영된 차트 데이터
  const chartData = useMemo(() => {
    if (!filteredData.length) return [];

    if (!marketOpen || !realtime?.price) {
      return filteredData;
    }

    // 마지막 데이터 복사해서 실시간 가격 적용
    const lastData = filteredData[filteredData.length - 1];
    const updatedLastData = {
      ...lastData,
      endPrice: Number(realtime.price), // 종가 대신 실시간 가격 반영
    };

    return [...filteredData.slice(0, -1), updatedLastData];
  }, [filteredData, marketOpen, realtime]);

  const handleSelect = (term: Term) => {
    setSelectedTerm(term);
    if (term.text === "사용자 지정") setCustomModalOpen(true);
  };

  if (
    !ticker ||
    (!marketOpen && !endDayData) ||
    (marketOpen && (!realtime || !backendInfo))
  )
    return <div>데이터 로딩 중...</div>;

  const displayPrice = marketOpen
    ? Number(realtime?.price ?? backendInfo?.volume ?? 0)
    : endDayData!.endPrice;

  const displayRate = marketOpen ? realtime?.rate ?? 0 : endDayData!.rate;

  const companyName = marketOpen
    ? backendInfo!.companyName
    : endDayData!.companyName;

  const displayDate = marketOpen
    ? new Date().toISOString()
    : new Date(new Date().setHours(15, 30, 0, 0)).toISOString();

  const pastPrice = filteredData[0]?.endPrice ?? displayPrice;

  const handleTrade = (type: "BUY" | "SELL", volume: number) => {
    const now = new Date();
    const trade: UserTradeHistory = {
      ticker: ticker!,
      tradeType: type,
      price: displayPrice, // 주당 가격
      volume, // ✅ 수량(주)
      createdAt: now,
    };
    console.log(trade.volume);
    setUserTrade((prev) => {
      const stockValue = displayPrice * volume; // ✅ 총 금액(가격 * 수량)

      let newCash = prev.cash;
      let newStock = prev.haveStock;

      if (type === "BUY") {
        newCash -= stockValue; // 현금에서 총 금액 차감
        newStock += stockValue; // 보유 주식 금액 증가
      } else {
        newCash += stockValue; // 현금에 총 금액 추가
        newStock -= stockValue; // 보유 주식 금액 감소
      }

      const totalMoney = newCash + newStock;
      const marginPercent =
        ((totalMoney - prev.originalMoney) / prev.originalMoney) * 100;

      return {
        ...prev,
        cash: newCash,
        haveStock: newStock,
        totalMoney,
        marginPercent,
      };
    });

    setTradeHistory((prev) => [trade, ...prev]);
  };

  // 로그인하지 않은 사용자는 모달만 표시
  if (!user) {
    return (
      <div className="min-h-screen">
        <LoginRequiredModal
          isOpen={loginRequiredModal}
          onClose={handleCloseLoginModal}
          onGoHome={handleGoHome}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br py-8 px-6 from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          {/* 왼쪽 메인 콘텐츠 영역 */}
          <div className="xl:col-span-2 space-y-6">
            {/* 차트 섹션 */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 text-white rounded-2xl shadow-xl p-6 border border-slate-600">
              <ChartHeader
                ticker={ticker!}
                companyName={companyName}
                endPrice={displayPrice}
                rate={displayRate}
                termText={selectedTerm.text}
                pastPrice={pastPrice}
                date={displayDate}
                isLoggedIn={isLoggedIn}
                isFavorite={isFavorite}
                setIsFavorite={setIsFavorite}
              />

              <div className="mt-4 ml-3 hidden">
                <TimeTerm
                  terms={TermText}
                  selectedTerm={selectedTerm}
                  onSelect={handleSelect}
                />
              </div>

              <DateModal
                isOpen={customModalOpen}
                onClose={() => setCustomModalOpen(false)}
                onConfirm={(start, end) => {
                  setCustomStartDate(start);
                  setCustomEndDate(end);
                }}
              />

              <div className="mt-4">
                <ChartMain
                  term={selectedTerm.text}
                  data={chartData}
                  dailyNewsCount={dailyNewsCount}
                />
              </div>
            </div>

            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-xl p-6 border border-slate-600">
              <h2 className="font-bold mb-6 text-white text-xl flex items-center gap-2">
                주요 키워드
              </h2>
              <TradeKeywords keywords={keywords} />
            </div>

            {/* AI 뉴스 요약 */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-xl p-6 border border-slate-600">
              <h2 className="font-bold mb-6 text-white text-xl flex items-center gap-2">
                AI 뉴스 요약
              </h2>
              <ChartNews analysis={aiAnalysis} />
            </div>

            {/* 관련 뉴스 */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-xl p-6 border border-slate-600">
              <h2 className="font-bold mb-6 text-white text-xl flex items-center gap-2">
                관련 뉴스
              </h2>
              <NewsCard news={news} />
            </div>
          </div>

          {/* 오른쪽 사이드바 - 거래 관련 */}
          <div className="xl:col-span-1 space-y-6">
            {/* 거래 카드 */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-xl p-6 border border-slate-600">
              <h2 className="font-bold mb-6 text-amber-400 text-xl flex items-center gap-2">
                나의 자산
              </h2>
              <TradeCard
                ticker={ticker!}
                stockPrice={displayPrice}
                userTrade={userTrade}
                userHolding={userHolding}
                setUserHolding={setUserHolding}
                onTrade={handleTrade}
                onTradeSuccess={() => {
                  console.log("거래가 성공적으로 완료되었습니다.");
                }}
                marketOpen={marketOpen} // ✅ 여기에 추가
              />
            </div>

            {/* 거래 히스토리 */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-xl p-6 border border-slate-600">
              <h2 className="font-bold mb-6 text-amber-400 text-xl flex items-center gap-2">
                투자 거래 내역
              </h2>
              <TradeHistory tradeHistory={tradeHistory} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TradeInfoPage;
