import { api } from './client';

export type Holding = {
  stockNo: number;
  ticker: string;
  companyName: string;
  quantity: number;
  avgPrice: number; // BigDecimal serialized as number
  currentPrice: number;
  invested: number;
  marketValue: number;
  pnl: number;
  pnlRate: number;
};

export type PortfolioSummary = {
  holdings: Holding[];
  totalInvested: number;
  totalMarketValue: number;
  totalPnl: number;
  totalPnlRate: number;
};

export const PortfolioApi = {
  getHoldings: () => api.get<PortfolioSummary>('/api/portfolio/holdings'),
};

