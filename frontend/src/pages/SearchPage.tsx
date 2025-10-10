// src/pages/SearchPage.tsx
import { useEffect, useState, useMemo } from "react";
import { useSearchParams, Link } from "react-router";
import HomeCard from "../components/HomeCard";
import type {
  BackendRealtime,
  WebSocketRealtime,
  EndDay,
} from "../types/StockRealtime";
import {
  getStockRealtimeWithPage,
  getEndDayWithPage,
} from "../api/StockRealtimeApi";

export default function SearchPage() {
  const [backendStocks, setBackendStocks] = useState<BackendRealtime[]>([]);
  const [wsStocks, setWsStocks] = useState<Map<string, WebSocketRealtime>>(
    new Map()
  );
  const [endDayStocks, setEndDayStocks] = useState<EndDay[]>([]);
  const [isMarketOpen, setIsMarketOpen] = useState(true);

  const [page, setPage] = useState(1);
  const size = 21; // 페이지당 21개
  const [totalPages, setTotalPages] = useState(1);

  const [params] = useSearchParams();
  const query = params.get("query")?.trim() ?? "";

  // 0️⃣ 장 시간 확인
  useEffect(() => {
    const checkMarketOpen = () => {
      const now = new Date();
      const marketOpen =
        (now.getHours() > 9 ||
          (now.getHours() === 9 && now.getMinutes() >= 0)) &&
        (now.getHours() < 15 ||
          (now.getHours() === 15 && now.getMinutes() < 30));
      setIsMarketOpen(marketOpen);
    };

    checkMarketOpen();
    const interval = setInterval(checkMarketOpen, 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // 1️⃣ 전체 데이터 fetch (200개만)
  useEffect(() => {
    const fetchData = async () => {
      try {
        if (isMarketOpen) {
          const response = await getStockRealtimeWithPage(1, 200);
          setBackendStocks(response.dtoList);
          setTotalPages(Math.ceil(response.dtoList.length / size));
        } else {
          const response = await getEndDayWithPage(1, 200);
          setEndDayStocks(response.dtoList);
          setTotalPages(Math.ceil(response.dtoList.length / size));
        }
      } catch (err) {
        console.error("❌ API 에러:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60 * 1000);
    return () => clearInterval(interval);
  }, [isMarketOpen]);

  // 2️⃣ WebSocket
  useEffect(() => {
    if (!isMarketOpen) return;

    const ws = new WebSocket(
      import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8765"
    );
    ws.onmessage = (event) => {
      const data: WebSocketRealtime[] = JSON.parse(event.data);
      setWsStocks((prev) => {
        const updated = new Map(prev);
        data.forEach((d) => updated.set(d.ticker, { ...d }));
        return updated;
      });
    };
    ws.onclose = () => console.log("WS 연결 종료");
    ws.onerror = (err) => console.error("WS 에러", err);

    return () => ws.close();
  }, [isMarketOpen]);

  // 3️⃣ 화면에 보여줄 데이터 결정
  const displayStocks = useMemo(() => {
    const baseData = isMarketOpen
      ? backendStocks.map((b) => {
          const wsItem = wsStocks.get(b.ticker);
          return {
            ...b,
            endPrice: Number(wsItem?.price ?? 0),
            rate: Number(wsItem?.rate ?? 0),
          };
        })
      : endDayStocks.length > 0
      ? endDayStocks.map((b) => ({
          ...b,
          endPrice: Number(b.endPrice ?? 0),
          rate: Number(b.rate ?? 0),
        }))
      : backendStocks.map((b) => ({ ...b, endPrice: 0, rate: 0 }));

    // 검색어 있으면 필터링
    const filtered = query
      ? baseData.filter(
          (s) =>
            s.ticker.includes(query) ||
            s.companyName.toLowerCase().includes(query.toLowerCase())
        )
      : baseData;

    // 검색어 없으면 페이지네이션 적용
    if (!query) {
      const startIdx = (page - 1) * size;
      const endIdx = startIdx + size;
      return filtered.slice(startIdx, endIdx);
    }

    return filtered;
  }, [backendStocks, endDayStocks, wsStocks, isMarketOpen, page, size, query]);

  return (
    <div>
      {query && (
        <h1 className="text-xl font-bold p-4 text-white">
          검색 결과: {query} ({displayStocks.length}건)
        </h1>
      )}

      <div className="grid grid-cols-3 gap-4 p-4">
        {displayStocks.map((stock) => (
          <Link key={stock.ticker} to={`/stock/${stock.ticker}`}>
            <HomeCard
              ticker={stock.ticker}
              companyName={stock.companyName}
              price={stock.endPrice ?? 0}
              rate={stock.rate ?? 0}
              volume={stock.volume}
              marketCap={stock.marketCap}
              categoryName={stock.categoryName}
            />
          </Link>
        ))}
      </div>

      {/* 검색어 없을 때만 페이지네이션 표시 */}
      {!query && (
        <div className="pagination flex justify-center gap-2 mt-4 flex-wrap">
          <button
            disabled={page === 1}
            className="px-3 py-1 border rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
            onClick={() => setPage((p) => Math.max(p - 1, 1))}
          >
            Prev
          </button>
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              className={`px-3 py-1 border rounded ${
                p === page
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 hover:bg-gray-300"
              }`}
              onClick={() => setPage(p)}
            >
              {p}
            </button>
          ))}
          <button
            disabled={page === totalPages}
            className="px-3 py-1 border rounded bg-gray-200 hover:bg-gray-300 disabled:opacity-50"
            onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
