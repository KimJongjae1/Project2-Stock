import { api } from './client';
import type { OrderRequest, OrderResponse } from '../types/order';

export const OrdersApi = {
  create: (req: OrderRequest) => api.post<OrderResponse>('/api/orders', req),
  cancel: (tradeNo: number, userNo: number) =>
    api.del<OrderResponse>(`/api/orders/${tradeNo}?userNo=${userNo}`),
  getUserPending: (userNo: number) => api.get<OrderResponse[]>(`/api/orders/user/${userNo}`),
  getPendingAll: () => api.get<OrderResponse[]>(`/api/orders/pending`),
};

