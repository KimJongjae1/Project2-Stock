import { useEffect, useState, useMemo } from "react";
import { useParams } from "react-router";
import ChartHeader from "../components/Chart/ChartHeader";
import TimeTerm from "../components/Chart/TimeTerm";
import KeywordRank from "../components/KeywordRank";
import NewsCard from "../components/NewsCard";
import ChartMain from "../components/Chart/ChartMain";
import DateModal from "./DateModal";
import ChartNews from "../components/Chart/ChartNews";

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

function isMarketOpen(): boolean {
  const now = new Date();
  const totalMinutes = now.getHours() * 60 + now.getMinutes();
  return totalMinutes >= 9 * 60 && totalMinutes <= 15 * 60 + 30;
}

export default function StockInfoPage() {
  const { ticker } = useParams<{ ticker: string }>();
  const marketOpen = isMarketOpen();

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
  const [dailyNewsCount, setDailyNewsCount] = useState<Record<string, number>>(
    {}
  );

  const [isFavorite, setIsFavorite] = useState(false);

  const { user } = useAuth();
  const isLoggedIn = Boolean(user);

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
  return (
    <div className="min-h-screen bg-gradient-to-br py-10 px-6 from-slate-900 via-slate-800 to-slate-900">
      <div className="max-w-7xl mx-auto space-y-10">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-3 space-y-6">
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

              <div className="mt-4 ml-3">
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
          </div>

          <div className="lg:col-span-1">
            <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-lg p-5 border border-slate-600">
              <h3 className="text-lg font-bold text-amber-400 mb-4">
                키워드 랭킹
              </h3>
              <KeywordRank keywords={keywords} />
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-xl p-6 border border-slate-600">
          <h2 className="font-bold mb-6 text-white text-2xl flex items-center gap-2">
            AI 뉴스 요약
          </h2>
          <div className="grid">
            <ChartNews analysis={aiAnalysis} />
          </div>
        </div>

        <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-2xl shadow-xl p-6 border border-slate-600">
          <h2 className="font-bold mb-6 text-white text-2xl flex items-center gap-2">
            관련 뉴스
          </h2>
          <NewsCard news={news} />
        </div>
      </div>
    </div>
  );
}
