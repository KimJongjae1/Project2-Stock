import { memo } from "react";

type DisplayStock = {
  ticker: string;
  companyName: string;
  price: number;
  rate: number;
  volume: number;
  categoryName: string;
  marketCap: number;
};

function numberFormat(num: number) {
  return num.toLocaleString();
}

function formatMarketCap(marketCap: number) {
  const inManWon = Math.floor(marketCap / 10000);
  return inManWon.toLocaleString();
}

interface HomeCardProps extends DisplayStock {
  onCardClick: () => void;
}

const HomeCard = memo(function HomeCard({
  ticker,
  companyName,
  price,
  rate,
  volume,
  categoryName,
  marketCap,
  onCardClick,
}: HomeCardProps) {
  return (
    <div
      className="cursor-pointer bg-white/20 border-white/30 backdrop-blur-sm rounded-2xl p-4 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 border"
      onClick={onCardClick}
    >
      {/* 헤더 */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1">
          <div className="text-white font-semibold text-lg truncate">
            {companyName}
          </div>
          <div className="text-white/70 text-sm font-mono">{ticker}</div>
        </div>
      </div>

      {/* 산업 분류와 시총 */}
      <div className="flex justify-between items-center mb-3">
        <div className="bg-gradient-to-r from-amber-500 to-amber-600 text-white px-2 py-1 rounded-full text-xs font-medium">
          {categoryName}
        </div>
        <div className="text-white/90 text-sm">
          시총{" "}
          <span className="text-white font-medium">
            {formatMarketCap(marketCap)}
          </span>{" "}
          조
        </div>
      </div>

      {/* 주가 정보 */}
      <div className="flex justify-between items-end">
        <div>
          <div className="text-white text-xl font-bold">
            {numberFormat(price)}원
          </div>
          <div
            className={`text-sm font-medium ${
              rate >= 0 ? "text-green-400" : "text-red-400"
            }`}
          >
            {rate >= 0 ? "+" : ""}
            {rate.toFixed(2)}%
          </div>
        </div>
        <div className="text-right">
          <div className="text-white/70 text-xs">거래량</div>
          <div className="text-white/90 text-sm font-medium">
            {numberFormat(volume)}
          </div>
        </div>
      </div>
    </div>
  );
});

export default HomeCard;
