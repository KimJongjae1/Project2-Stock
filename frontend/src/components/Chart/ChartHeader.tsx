// src/components/Chart/ChartHeader.tsx
import { CalendarDays } from "lucide-react";
import type { StockInfos } from "../../types/StockInfos";
import { useNavigate } from "react-router";
import StarYellowSvg from "../../svg/StarYellowSvg";
import StarGraySvg from "../../svg/StarGraySvg";
import { toggleFavorite } from "../../api/StockInfosApi";

interface ChartHeaderProps extends StockInfos {
  termText: string;
  pastPrice: number;
  rate: number;
  date: string;
  isLoggedIn: boolean;
  isFavorite: boolean | null;
  setIsFavorite: (fav: boolean) => void;
}

function ChartHeader({
  ticker,
  companyName,
  endPrice,
  rate,
  termText,
  pastPrice,
  date,
  isLoggedIn,
  isFavorite,
  setIsFavorite,
}: ChartHeaderProps) {
  const stockDate = typeof date === "string" ? new Date(date) : date;
  const navigate = useNavigate();
  const formattedDate = `${stockDate.getFullYear()}년 ${
    stockDate.getMonth() + 1
  }월 ${stockDate.getDate()}일`;

  const priceColor =
    rate > 0 ? "text-green-400" : rate < 0 ? "text-red-400" : "text-slate-300";
  const arrow = rate > 0 ? "▲" : rate < 0 ? "▼" : "-";

  const handleFavoriteClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isLoggedIn) {
      navigate("/login");
      return;
    }

    if (isFavorite === null) return; // 로딩 중이면 클릭 막기

    try {
      const newStatus = await toggleFavorite(ticker);
      setIsFavorite(newStatus);
    } catch (err) {
      console.error(err);
      alert("즐겨찾기 저장 중 오류가 발생했습니다.");
    }
  };

  return (
    <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white px-6 py-5 rounded-2xl shadow-lg border border-slate-700">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-extrabold tracking-tight text-white">
            {companyName}
          </h1>
          <span className="px-3 py-1 text-sm font-semibold text-amber-400 bg-slate-700 rounded-full border border-amber-500 shadow-md">
            {ticker}
          </span>
          <button
            className="cursor-pointer hover:bg-black/10 rounded-lg transition-colors"
            onClick={handleFavoriteClick}
          >
            {isFavorite === null ? null : isFavorite ? (
              <StarYellowSvg />
            ) : (
              <StarGraySvg />
            )}
          </button>
        </div>

        <div className="flex items-center gap-2 text-sm text-slate-400">
          <CalendarDays className="w-4 h-4 text-slate-500" />
          <span>{formattedDate}</span>
        </div>
      </div>

      <div className="mt-4 flex items-baseline gap-3">
        <span
          className={`text-3xl font-extrabold tracking-tight drop-shadow-md ${priceColor}`}
        >
          {endPrice.toLocaleString()} 원
        </span>
        <span className={`text-sm font-semibold ${priceColor}`}>
          {arrow} {Math.abs(rate).toFixed(2)} %
        </span>
        <span className="text-sm text-slate-400">
          ({termText} 전 가격: {pastPrice.toLocaleString()} 원)
        </span>
      </div>
    </div>
  );
}

export default ChartHeader;
