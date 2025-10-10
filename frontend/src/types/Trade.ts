export interface UserTradeHistory {
  ticker: string;
  tradeType: HistoryType;
  price: number;
  volume: number;
  createdAt: Date;
}

export interface TradeHistoryDto {
  tradeType: "BUY" | "SELL";
  price: number;
  volume: number;
  totalPrice: number;
  createAt: string; // LocalDateTime는 ISO 8601 문자열로 전송됨
}

export interface TradeRequest {
  ticker: string;
  price: number;
  volume: number;
}

export interface UserAsset {
  cash: number;
  haveStock: number;
  originalMoney: number;
}

type HistoryType = "BUY" | "SELL";

export interface UserStockHoldingDto {
  ticker: string;
  quantity: number;
  avgBuyPrice: number;
}
