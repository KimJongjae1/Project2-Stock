import { api } from './client';

export type StockItemOption = { itemNo: number; ticker: string; companyName: string };
export type StockPricePoint = { date: string; endPrice: number };
export type StockCandlePoint = { date: string; open: number; high: number; low: number; close: number; volume: number };

export const StocksApi = {
  listItems: () => api.get<StockItemOption[]>('/api/stock/items'),
  history: (itemNo: number, from?: string, to?: string) => {
    const params = new URLSearchParams({ itemNo: String(itemNo) });
    if (from) params.set('from', from);
    if (to) params.set('to', to);
    return api.get<StockPricePoint[]>(`/api/stock/history?${params.toString()}`);
  },
  candleHistory: (itemNo: number, from?: string, to?: string) => {
    const params = new URLSearchParams({ itemNo: String(itemNo) });
    if (from) params.set('from', from);
    if (to) params.set('to', to);
    return api.get<StockCandlePoint[]>(`/api/stock/history/candle?${params.toString()}`);
  },
};
