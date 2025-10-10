import { api } from './client';

export interface OrderRequest {
  userNo: number;
  stockNo: number;
  type: 'BUY' | 'SELL';
  orderType: 'MARKET' | 'LIMIT' | 'STOP_LOSS' | 'TAKE_PROFIT' | 'TIME_LIMIT';
  price: number;
  volume: number;
  triggerPrice?: number;
  expiresAt?: string;
}

export interface OrderResponse {
  tradeNo: number;
  userNo: number;
  stockNo: number;
  type: 'BUY' | 'SELL';
  orderType: 'MARKET' | 'LIMIT' | 'STOP_LOSS' | 'TAKE_PROFIT' | 'TIME_LIMIT';
  price: number;
  volume: number;
  status: 'PENDING' | 'PARTIAL_FILLED' | 'FILLED' | 'CANCELLED' | 'EXPIRED';
  triggerPrice?: number;
  expiresAt?: string;
  createdAt: string;
  message: string;
  success: boolean;
}

// 주문 생성
export const createOrder = async (orderData: OrderRequest): Promise<OrderResponse> => {
  return await api.post<OrderResponse>('/api/orders', orderData);
};

// 주문 취소
export const cancelOrder = async (tradeNo: number, userNo: number): Promise<OrderResponse> => {
  return await api.del<OrderResponse>(`/api/orders/${tradeNo}?userNo=${userNo}`);
};

// 사용자 주문 조회
export const getUserOrders = async (userNo: number): Promise<OrderResponse[]> => {
  return await api.get<OrderResponse[]>(`/api/orders/user/${userNo}`);
};

// 대기 주문 조회
export const getPendingOrders = async (): Promise<OrderResponse[]> => {
  return await api.get<OrderResponse[]>('/api/orders/pending');
};

// 주문 조회
export const getOrder = async (tradeNo: number): Promise<OrderResponse> => {
  return await api.get<OrderResponse>(`/api/orders/${tradeNo}`);
};
