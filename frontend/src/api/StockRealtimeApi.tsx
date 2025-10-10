import axios from "axios";
import type {
  BackendRealtime,
  EndDay,
  PageResponseDto,
} from "../types/StockRealtime";
import { url } from "./config";

const prefix = url('/api/stock');

export const getStockRealtimeWithPage = async (
  page: number,
  size: number
): Promise<PageResponseDto<BackendRealtime>> => {
  const res = await axios.get(`${prefix}/realtime?page=${page}&size=${size}`);
  return res.data;
};
export const getEndDayWithPage = async (
  page: number,
  size: number
): Promise<PageResponseDto<EndDay>> => {
  console.log("📌 요청 page, size:", page, size);
  const res = await axios.get(`${prefix}/endDay?page=${page}&size=${size}`);
  return res.data;
};
