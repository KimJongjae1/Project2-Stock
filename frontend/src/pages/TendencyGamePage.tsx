import SummaryStats from "../components/TendencyGame/SummaryStats";
import type { SummaryStatItem } from "../components/TendencyGame/SummaryStats";
import TradePanel from "../components/TendencyGame/TradePanel";
import TradeRecord from "../components/TendencyGame/TradeRecord";
import StockOverview from "../components/TendencyGame/StockOverview";
import StockHighlights from "../components/TendencyGame/StockHighlights";
import TradeSuccessModal from '../components/TendencyGame/TradeSuccessModal';
import GameFinishModal from '../components/TendencyGame/GameFinishModal';
import LoginRequiredModal from '../components/TendencyGame/LoginRequiredModal';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { useTendencyGame } from "../hooks/useTendencyGame";
import { useAuth } from "../stores/auth";
import { useEffect, useMemo, useState } from "react";
import { extractKeywords, getStockInfo } from "../api/StockInfosApi";
import { useNavigate } from 'react-router';

export default function TendencyGamePage() {
  const { 
    state, 
    loading, 
    error, 
    summaryItems, 
    tradeAmount, 
    setTradeAmount, 
    order, 
    nextWeek, 
    finish, 
    tradeSuccessModal, 
    closeTradeSuccessModal, 
    gameFinishModal, 
    closeGameFinishModal,
    nextWeekLoading
  } = useTendencyGame();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loginRequiredModal, setLoginRequiredModal] = useState(false);

  const handleGoHome = () => {
    navigate('/');
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
        navigate('/');
      }, 2000); // 2초 후 홈으로 이동
      
      return () => clearTimeout(timer);
    }
  }, [user, navigate]);

  const [currentChartData, setCurrentChartData] = useState(null);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [news, setNews] = useState<Array<{ title: string; url: string; date: string }>>([]);
  const [keywordsLoading, setKeywordsLoading] = useState(false);

  const so = state?.stockOverview;

  const startDate = useMemo(() => {
    if (!so?.currentDate) return null;
    const currentDate = new Date(so.currentDate);
    // 현재 날짜부터 일주일 전까지의 범위로 설정
    const weekAgo = new Date(currentDate);
    weekAgo.setDate(currentDate.getDate() - 6);
    return weekAgo.toISOString().slice(0, 10);
  }, [so?.currentDate]);
  
  const endDate = useMemo(() => so?.currentDate, [so?.currentDate]);

  // 회사명 익명화 유틸 - 페이지 단계에서 제목을 변환
  const escapeRegExp = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const anonymizeTitle = (title: string, company: string) => {
    if (!company) return title;
    let out = title;
    try {
      // 전체 명칭 치환
      out = out.replace(new RegExp(escapeRegExp(company), 'g'), '익명 기업');
      // 공백 단위로 쪼개서 2글자 이상 토큰도 치환
      const tokens = company.split(' ').filter((t) => t.length > 1);
      tokens.forEach((t) => {
        out = out.replace(new RegExp(escapeRegExp(t), 'g'), '익명 기업');
      });
      // 한글 기업명에서 자주 쓰는 접미사 제거 버전도 시도 (예: 전자, 화학 등)
      const simplified = company.replace(/\s+/g, '');
      if (simplified.length > 1) {
        out = out.replace(new RegExp(escapeRegExp(simplified), 'g'), '익명 기업');
      }

      // 한글 기업명 변형 대응: 공통 접두(루트)만으로도 치환 (예: 동원산업 ↔ 동원그룹)
      const korSuffixes = [
        '그룹','산업','전자','화학','건설','리테일','홀딩스','지주','투자','시스템','테크',
        '엔터테인먼트','게임즈','제약','바이오','자동차','모터스','물산','증권','캐피탈','카드','은행',
        '생명','화재','해운','항공','철강','중공업','발전','에너지','유통','식품','제과','치킨','편의점',
        '마트','백화점','면세점','호텔','리츠','미디어','방송','통신','모바일','반도체'
      ];
      let root = simplified;
      for (const suf of korSuffixes) {
        if (root.endsWith(suf) && root.length - suf.length >= 2) {
          root = root.slice(0, root.length - suf.length);
          break;
        }
      }
      if (root && root.length >= 2) {
        // 예: 동원그룹, 동원-그룹, 동원 홀딩스 등 변형 치환
        const rootPattern = new RegExp(escapeRegExp(root) + '(?:\s*[-_]?\s*[가-힣A-Za-z0-9]{1,6})?', 'g');
        out = out.replace(rootPattern, '익명 기업');
      }
    } catch {
      // 정규식 에러 시 원문 유지
    }
    return out;
  };

  useEffect(() => {
    if (!so?.ticker || !startDate || !endDate) return;

    const run = async () => {
      setKeywordsLoading(true);
      let originalCompanyName: string;
      
      try {
        // ticker로 최신 회사명(원본) 조회
        const infos = await getStockInfo(so.ticker);
        const latest = (infos ?? []).reduce((prev, curr) => {
          if (!prev) return curr;
          return new Date(curr.date) > new Date(prev.date) ? curr : prev;
        }, undefined as any);
        originalCompanyName = latest?.companyName ?? so.companyAlias;

        // 원본 회사명으로 키워드/뉴스 요청
        const res = await extractKeywords(so.ticker, originalCompanyName, startDate, endDate);
        
        // keywords는 Record<string, number> -> string[]로 변환
        const extractedKeywords = Object.keys(res.keywords || {})
          .sort((a, b) => (res.keywords[b] || 0) - (res.keywords[a] || 0)) // 빈도수로 정렬
          .slice(0, 5); // 상위 5개만 선택
        setKeywords(extractedKeywords);

        // 뉴스 데이터 처리 - topNewsArticles 사용
        const newsData = res.topNewsArticles || [];
        const anonNews = newsData.map((n) => ({
          title: anonymizeTitle(n.title, originalCompanyName),
          url: n.url,
          date: n.date,
        }));
        setNews(anonNews);
      } catch (error) {
        console.error("❌ 키워드/뉴스 추출 실패:", error);
        console.error("🔍 에러 상세:", {
          ticker: so.ticker,
          companyName: originalCompanyName!,
          startDate,
          endDate
        });
        setKeywords([]);
        setNews([]);
      } finally {
        setKeywordsLoading(false);
      }
    };
    void run();
  }, [so?.ticker, so?.companyAlias, startDate, endDate]);

  useEffect(() => {
    if (state && state.stockOverview) {
      const so = state.stockOverview;

      // 💡 state.currentWeek 대신 state.week를 사용합니다.
      const currentWeekIndex = state.week ?? 1;
      const chartLabels = so.chart.labels.slice(0, currentWeekIndex);
      const chartPrices = so.chart.prices.slice(0, currentWeekIndex);

      setCurrentChartData({
        labels: chartLabels,
        datasets: [{ label: 'Price', data: chartPrices }],
      } as any);
    }
  }, [state]);

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

  if (loading && !state) return <div className="min-h-screen grid place-items-center">불러오는 중…</div>;
  if (error && !state) return <div className="min-h-screen grid place-items-center text-red-600">{error}</div>;
  if (!state || !so) return null;

  const tp = state.tradePanel;

  return (
    <div className="min-h-screen p-5">
      <SummaryStats items={summaryItems as SummaryStatItem[]} />

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="space-y-4 lg:col-span-2">
          {currentChartData && (
            <StockOverview
              companyName={so.companyAlias}
              currentWeek={so.currentDate}
              nextWeek={so.finalWeek ? '종료' : so.nextDate ?? ''}
              price={so.price}
              change={so.change}
              rate={so.changeRate}
              chartData={currentChartData}
            />
           )}
           {(nextWeekLoading || keywordsLoading) ? (
             <div className="rounded-xl bg-slate-900 p-5">
               <div className="mb-3 flex items-center justify-between">
                 <div className="font-semibold text-white">주요 키워드 & 뉴스</div>
               </div>
               <div className="flex items-center justify-center py-8">
                 <LoadingSpinner 
                   size="md" 
                   textColor="dark"
                   text={nextWeekLoading ? "다음 주 데이터를 불러오는 중..." : "키워드와 뉴스를 불러오는 중..."} 
                 />
               </div>
             </div>
           ) : (
             <StockHighlights keywords={keywords} news={news} />
           )}
         </section>
        <section className="space-y-4">
          <TradePanel
            stockCount={tp.stockCount}
            totalValue={tp.stockValuation}
            averageCost={tp.averageCost}
            evaluationProfit={tp.evaluationProfit}
            evaluationRate={tp.evaluationRate}
            tradeAmount={tradeAmount}
            onTradeAmountChange={setTradeAmount}
            onBuy={() => order('BUY', tradeAmount)}
            onSell={() => order('SELL', tradeAmount)}
            onNextWeek={nextWeek}
            onEndGame={async () => {
              await finish();
            }}
            term="0주"
            onTermChange={() => {}}
            maxAffordable={tp.maxAffordable}
            maxSellable={tp.maxSellable}
            currentWeek={state?.week || 1}
            maxWeek={state?.maxWeek || 10}
          />
          <TradeRecord
            items={state.trades.map((t) => ({
              gameTradeType: t.type,
              gameTradePrice: t.price,
              gameTradeDate: t.tradeDate,
              qty: t.quantity,
            }))}
          />
        </section>
      </div>

      <TradeSuccessModal
        isOpen={tradeSuccessModal.isOpen}
        onClose={closeTradeSuccessModal}
        tradeType={tradeSuccessModal.tradeType}
        quantity={tradeSuccessModal.quantity}
        price={tradeSuccessModal.price}
      />

       <GameFinishModal
         isOpen={gameFinishModal.isOpen}
         onClose={closeGameFinishModal}
         onGoHome={handleGoHome}
         result={gameFinishModal.result}
       />

       <LoginRequiredModal
         isOpen={loginRequiredModal}
         onClose={handleCloseLoginModal}
         onGoHome={handleGoHome}
       />
     </div>
   );
 }
