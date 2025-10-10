import { useCallback, useEffect, useMemo, useState } from "react";
import { tendencyGameApi, type TendencyGameStateResponse, type FinishResultResponse, type TradeType } from "../api/tendencyGame";

export function useTendencyGame() {
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [state, setState] = useState<TendencyGameStateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tradeAmount, setTradeAmount] = useState(1);
  const [finishResult, setFinishResult] = useState<FinishResultResponse | null>(null);
  const [tradeSuccessModal, setTradeSuccessModal] = useState<{
    isOpen: boolean;
    tradeType: "BUY" | "SELL";
    quantity: number;
    price: number;
  }>({
    isOpen: false,
    tradeType: "BUY",
    quantity: 0,
    price: 0,
  });
  const [gameFinishModal, setGameFinishModal] = useState<{
    isOpen: boolean;
    result: FinishResultResponse | null;
  }>({
    isOpen: false,
    result: null,
  });
  const [nextWeekLoading, setNextWeekLoading] = useState(false);

  const start = useCallback(async (opts?: { ticker?: string; itemNo?: number }) => {
    setLoading(true);
    setError(null);
    try {
      const res = await tendencyGameApi.start(opts);
      setSessionId(res.sessionId);
      setState(res);
    } catch (e: any) {
      setError(e?.message ?? "게임 시작에 실패했습니다");
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await tendencyGameApi.getState(sessionId);
      setState(res);
    } catch (e: any) {
      setError(e?.message ?? "상태 조회 실패");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const order = useCallback(
    async (type: TradeType, qty?: number) => {
      if (!sessionId) return;
      setLoading(true);
      setError(null);
      try {
        const res = await tendencyGameApi.order(sessionId, {
          type,
          quantity: Math.max(1, Math.floor(qty ?? tradeAmount)),
          tradeDate: (state?.stockOverview.currentDate ?? new Date().toISOString().slice(0, 10)),
        });
        setState(res);
        
        // 거래 성공 모달 표시
        setTradeSuccessModal({
          isOpen: true,
          tradeType: type,
          quantity: Math.max(1, Math.floor(qty ?? tradeAmount)),
          price: res.stockOverview.price,
        });
      } catch (e: any) {
        setError(e?.message ?? "주문 실패");
      } finally {
        setLoading(false);
      }
    },
    [sessionId, tradeAmount, state?.stockOverview.currentDate],
  );

  const nextWeek = useCallback(async () => {
    if (!sessionId) return;
    setNextWeekLoading(true);
    setError(null);
    try {
      const res = await tendencyGameApi.nextWeek(sessionId);
      setState(res);
    } catch (e: any) {
      setError(e?.message ?? "다음 주 이동 실패");
    } finally {
      setNextWeekLoading(false);
    }
  }, [sessionId]);

  const finish = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await tendencyGameApi.finish(sessionId);
      setFinishResult(res);
      
      // 게임 종료 모달 표시
      setGameFinishModal({
        isOpen: true,
        result: res,
      });
      
      return res;
    } catch (e: any) {
      setError(e?.message ?? "게임 종료 실패");
      return null;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const closeTradeSuccessModal = useCallback(() => {
    setTradeSuccessModal(prev => ({ ...prev, isOpen: false }));
  }, []);

  const closeGameFinishModal = useCallback(() => {
    setGameFinishModal(prev => ({ ...prev, isOpen: false }));
  }, []);

  useEffect(() => {
    // 첫 진입 시 바로 시작(랜덤 종목/기간)
    if (sessionId == null) void start();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const summaryItems = useMemo(() => {
    if (!state) return [] as Array<{ id: string; label: string; value: string; helper?: string; tone?: "positive" | "negative" | "default" }>;
    const s = state.summary;
    const evalProfit = s.totalAsset - s.cash - 0 + 0; // not used, kept for compatibility
    return [
      { id: "cash", label: "보유 현금", value: new Intl.NumberFormat("ko-KR").format(s.cash) + "원" },
      {
        id: "stock",
        label: "보유 주식",
        value: `${new Intl.NumberFormat("ko-KR").format(s.stockQuantity)}주`,
        helper: new Intl.NumberFormat("ko-KR").format(s.stockValuation) + "원",
      },
      { id: "asset", label: "총 자산", value: new Intl.NumberFormat("ko-KR").format(s.totalAsset) + "원" },
      { id: "realized", label: "실현 손익", value: new Intl.NumberFormat("ko-KR").format(s.realizedProfit) + "원" },
      {
        id: "yield",
        label: "전체 수익률",
        value: `${s.totalYield > 0 ? "+" : ""}${s.totalYield.toFixed(2)}%`,
        helper: new Intl.NumberFormat("ko-KR").format(s.totalAsset - s.cash) + "원",
        tone: s.totalYield >= 0 ? "positive" : "negative",
      },
    ];
  }, [state]);

  return {
    sessionId,
    state,
    loading,
    error,
    tradeAmount,
    setTradeAmount,
    summaryItems,
    start,
    refresh,
    order,
    nextWeek,
    finish,
    finishResult,
    tradeSuccessModal,
    closeTradeSuccessModal,
    gameFinishModal,
    closeGameFinishModal,
    nextWeekLoading,
  };
}

