export interface Term {
  text: string;
  onSelect?: () => void;
}

export interface News {
  title: string;
  url: string;
  date: string;
}

export interface Keyword {
  keyword: string;
  count: number;
}

export interface StockInfos {
  ticker: string;
  companyName: string;
  date: string;
  endPrice: number;
}

export interface Chart {
  term: string;
  data: StockInfos[];
}

export interface ExtractKeywordsResponse {
  keywords: Record<string, number>;
  topNewsArticles?: News[];
  aiAnalysis: string; // 문자열로만 관리
  dailyNewsCount: Record<string, number>;
}

export const TermText: Term[] = [
  { text: "1 주" },
  { text: "1개월" },
  { text: "6개월" },
  { text: "1 년" },
  // { text: "3 년" },
  // { text: "5 년" },
  { text: "사용자 지정" },
];
