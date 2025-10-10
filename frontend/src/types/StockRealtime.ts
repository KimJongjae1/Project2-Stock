export interface WebSocketRealtime {
  ticker: string;
  price: string;
  rate: number;
}

export interface BackendRealtime {
  ticker: string;
  companyName: string;
  volume: number;
  marketCap: number;
  categoryName: string;
}

export interface EndDay {
  ticker: string;
  companyName: string;
  endPrice: number;
  rate: number;
  volume: number;
  marketCap: number;
  categoryName: string;
}

export interface PageResponseDto<T> {
  dtoList: T[];
  pageRequestDto: {
    page: number;
    size: number;
  };
  totalCount: number;
  prev: boolean;
  next: boolean;
  pageNumberList: number[];
  prevPage: number;
  nextPage: number;
  totalPage: number;
  current: number;
}
