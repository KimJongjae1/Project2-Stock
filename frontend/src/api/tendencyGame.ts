import { api } from "./client";

// 서버 DTO와 맞춘 타입들
export type TradeType = "BUY" | "SELL";

export interface TendencyGameStateResponse {
  sessionId: number;
  week: number;
  maxWeek: number;
  finished: boolean;
  summary: {
    cash: number;
    stockQuantity: number;
    stockValuation: number;
    totalAsset: number;
    realizedProfit: number;
    totalYield: number;
  };
  stockOverview: {
    companyAlias: string;
    ticker: string;
    currentDate: string; // ISO date
    nextDate: string | null; // ISO date or null at final week
    price: number;
    change: number;
    changeRate: number;
    chart: { labels: string[]; prices: number[] };
    finalWeek: boolean;
  };
  tradePanel: {
    stockCount: number;
    stockValuation: number;
    averageCost: number;
    evaluationProfit: number;
    evaluationRate: number;
    maxAffordable: number;
    maxSellable: number;
  };
  trades: Array<{
    tradeId: number;
    type: TradeType;
    price: number;
    quantity: number;
    tradeDate: string; // ISO date
    executedAt: string; // ISO datetime
  }>;
  highlights: {
    keywords: string[];
    news: Array<{ title: string; url: string; summary: string }>;
    summary: string;
  };
}

export interface StartRequest {
  ticker?: string;
  itemNo?: number;
}

export interface OrderRequest {
  type: TradeType;
  quantity: number;
  tradeDate?: string; // 클라이언트에서 현재 주차 날짜를 명시적으로 전달
}

export interface FinishResultResponse {
  sessionId: number;
  maxWeek: number;
  finalWeek: number;
  totalAsset: number;
  realizedProfit: number;
  totalYield: number;
  yieldAboveThreshold: boolean;
  tendencyType: string;
  recommendation: string;
  decisionElapsedSeconds: number;
  volatileBuyCount: number;
  volatileSellCount: number;
  sellDominantWeekCount: number;
  startedAt: string;
  finishedAt: string;
}

export const tendencyGameApi = {
  start: (body?: StartRequest) => api.post<TendencyGameStateResponse>("/api/games/tendency", body ?? {}),
  getState: (sessionId: number) => api.get<TendencyGameStateResponse>(`/api/games/tendency/${sessionId}`),
  order: (sessionId: number, body: OrderRequest) =>
    api.post<TendencyGameStateResponse>(`/api/games/tendency/${sessionId}/orders`, body),
  nextWeek: (sessionId: number) => api.post<TendencyGameStateResponse>(`/api/games/tendency/${sessionId}/next-week`, {}),
  finish: (sessionId: number) => api.post<FinishResultResponse>("/api/games", { sessionId }),
};

