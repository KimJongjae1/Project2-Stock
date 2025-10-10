// src/api/StockInfosApi.tsx
import axios from "axios";
import type { ExtractKeywordsResponse, StockInfos } from "../types/StockInfos";
import { getAccessToken } from "./tokenCache";

export const API_SERVER_HOST =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";
const prefix = `${API_SERVER_HOST}/api/stock`;

const accessToken = getAccessToken();
// 🔹 키워드 추출 API (백엔드 호출) - 토큰 추가 ✅
export const extractKeywords = async (
  ticker: string,
  companyName: string,
  startDate: string,
  endDate: string
): Promise<ExtractKeywordsResponse> => {
  // 반환 타입을 ExtractKeywordsResponse로
  const payload = {
    companyName,
    startDate,
    endDate,
    topKeywords: 10,
    useAiFilter: true,
  };

  const url = `${prefix}/extract-keywords/${ticker}`;
  const res = await axios.post<ExtractKeywordsResponse>(url, payload);
  console.log(res.data);

  // 그대로 반환
  return res.data; // keywords, topNewsArticles, aiAnalysis, dailyNewsCount 모두 포함
};

// 🔹 주식 정보 API - 토큰 추가 ✅
export const getStockInfo = async (ticker: string): Promise<StockInfos[]> => {
  // 토큰이 있는 경우에만 헤더에 포함
  // const headers = accessToken
  //   ? {
  //       Authorization: `Bearer ${accessToken}`,
  //     }
  //   : {};

  const res = await axios.get<StockInfos[]>(`${prefix}/info/${ticker}`, {});
  return res.data;
};

// src/api/FavoriteApi.ts
export async function toggleFavorite(ticker: string): Promise<boolean> {
  try {
    const res = await axios.post(
      `${API_SERVER_HOST}/api/stock/favorites/toggle`,
      null,
      {
        params: { ticker },
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    return res.data;
  } catch (err) {
    console.error("[toggleFavorite] Error:", err);
    throw err;
  }
}

export async function fetchFavorite(ticker: string): Promise<boolean> {
  if (!accessToken) throw new Error("No access token available");

  const res = await axios.get(
    `${API_SERVER_HOST}/api/stock/favorites/${ticker}`,
    {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    }
  );

  return res.data.isFavorite;
}
