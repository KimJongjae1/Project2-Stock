export type TradeType = 'BUY' | 'SELL';

export interface TradeItem {
  type: TradeType;
  price: number;
  qty?: number;
  date: string; // ISO string 'YYYY-MM-DD'
}

export interface NewsItem {
  id: string;
  title: string;
  summary?: string;
}

export interface ChartLineDataset {
  label: string;
  data: number[];
}

export interface ChartLineData {
  labels: string[];
  datasets: ChartLineDataset[];
}

