import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import HomeCard from "../components/HomeCard";
import type {
  WebSocketRealtime,
  BackendRealtime,
  EndDay,
  PageResponseDto,
} from "../types/StockRealtime";
import {
  getStockRealtimeWithPage,
  getEndDayWithPage,
} from "../api/StockRealtimeApi";

export default function HomePage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // URL에서 페이지 읽기
  const pageParam = searchParams.get("page");
  const [page, setPage] = useState<number>(pageParam ? Number(pageParam) : 1);

  const [size] = useState(21);
  const [totalPages, setTotalPages] = useState(1);

  const [backendStocks, setBackendStocks] = useState<BackendRealtime[]>([]);
  const [endDayStocks, setEndDayStocks] = useState<EndDay[]>([]);
  const [isMarketOpen, setIsMarketOpen] = useState(true);
  const [wsStocks, setWsStocks] = useState<Map<string, WebSocketRealtime>>(
    new Map()
  );

  // URL 쿼리와 상태 동기화
  useEffect(() => {
    const pageParam = searchParams.get("page");
    if (pageParam && Number(pageParam) !== page) {
      setPage(Number(pageParam));
    }
  }, [searchParams]);

  useEffect(() => {
    setSearchParams({ page: String(page) });
  }, [page, setSearchParams]);

  const handleStockClick = (ticker: string) => {
    navigate(`/stock/${ticker}?fromPage=${page}`);
  };

  // 시장 시간 확인 (09:00 ~ 15:30)
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

  // 데이터 fetch
  useEffect(() => {
    const fetchData = async () => {
      try {
        if (isMarketOpen) {
          const response: PageResponseDto<BackendRealtime> =
            await getStockRealtimeWithPage(1, 200);
          setBackendStocks(response.dtoList);
          setTotalPages(Math.ceil(response.dtoList.length / size));
        } else {
          const response: PageResponseDto<EndDay> = await getEndDayWithPage(
            page,
            size
          );
          setEndDayStocks(response.dtoList);
          setTotalPages(response.totalPage || 1);
        }
      } catch (err) {
        console.error("❌ API 에러:", err);
      }
    };
    fetchData();
  }, [isMarketOpen, page, size]);

  // WebSocket (시장 열렸을 때만)
  useEffect(() => {
    if (!isMarketOpen) return;

    const ws = new WebSocket(
      import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8765"
    );

    ws.onopen = () => console.log("✅ WS 연결 성공");

    ws.onmessage = (event) => {
      try {
        const data: WebSocketRealtime[] = JSON.parse(event.data);
        setWsStocks((prev) => {
          const updated = new Map(prev);
          data.forEach((d) => updated.set(d.ticker, d));
          return updated;
        });
      } catch (err) {
        console.error("❌ WS 데이터 파싱 오류:", err, event.data);
      }
    };

    return () => ws.close();
  }, [isMarketOpen]);

  const displayStocks = isMarketOpen
    ? backendStocks.slice((page - 1) * size, page * size).map((b) => {
        const wsItem = wsStocks.get(b.ticker);
        return {
          ticker: b.ticker,
          companyName: b.companyName,
          volume: b.volume,
          marketCap: b.marketCap,
          categoryName: b.categoryName,
          price: wsItem ? Number(wsItem.price) : 0,
          rate: wsItem ? wsItem.rate : 0,
        };
      })
    : endDayStocks.map((e) => ({
        ticker: e.ticker,
        companyName: e.companyName,
        volume: e.volume,
        marketCap: e.marketCap,
        categoryName: e.categoryName,
        price: e.endPrice,
        rate: e.rate,
      }));

  // 페이지네이션 버튼 계산
  const getPageNumbers = () => {
    const maxVisible = 10; // 한 번에 보여줄 페이지 수
    let start = Math.max(1, page - Math.floor(maxVisible / 2));
    const end = Math.min(totalPages, start + maxVisible - 1);

    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }

    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  };

  return (
    <div className="w-full min-h-screen">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 p-3">
        {displayStocks.map((stock) => (
          <HomeCard
            key={stock.ticker}
            ticker={stock.ticker}
            companyName={stock.companyName}
            price={stock.price}
            rate={stock.rate}
            volume={stock.volume}
            marketCap={stock.marketCap}
            categoryName={stock.categoryName}
            onCardClick={() => handleStockClick(stock.ticker)}
          />
        ))}
      </div>

      {/* 페이지네이션 */}
      <div className="flex justify-center gap-2 mt-4 flex-wrap">
        <button
          className="px-3 py-1 rounded border bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={page === 1}
          onClick={() => setPage(page - 1)}
        >
          Prev
        </button>

        {getPageNumbers().map((p) => (
          <button
            key={p}
            className={`px-3 py-1 rounded border transition ${
              p === page
                ? "bg-blue-500 text-white border-blue-500"
                : "bg-gray-200 hover:bg-gray-300 border-gray-300"
            }`}
            onClick={() => setPage(p)}
          >
            {p}
          </button>
        ))}

        <button
          className="px-3 py-1 rounded border bg-gray-200 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={page === totalPages}
          onClick={() => setPage(page + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}
