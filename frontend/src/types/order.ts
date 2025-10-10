export type TradeType = 'BUY' | 'SELL';
export type OrderType = 'MARKET' | 'LIMIT' | 'STOP_LOSS' | 'TAKE_PROFIT' | 'TIME_LIMIT';
export type OrderStatus = 'PENDING' | 'PARTIAL_FILLED' | 'FILLED' | 'CANCELLED' | 'EXPIRED';

export interface OrderRequest {
  userNo: number;
  stockNo: number;
  type: TradeType;
  orderType: OrderType;
  price?: number | null;
  volume: number;
  triggerPrice?: number | null;
  expiresAt?: string | null; // ISO datetime
}

export interface OrderResponse {
  tradeNo: number;
  userNo: number;
  stockNo: number;
  type: TradeType;
  orderType: OrderType;
  price: number;
  volume: number;
  status: OrderStatus;
  triggerPrice?: number | null;
  expiresAt?: string | null;
  createdAt: string;
  message?: string;
  success?: boolean;
}

