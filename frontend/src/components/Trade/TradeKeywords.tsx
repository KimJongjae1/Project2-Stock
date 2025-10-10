import type { Keyword } from "../../types/StockInfos";

interface KeywordRankProps {
  keywords: Record<string, number> | (Keyword | string)[];
}

function TradeKeywords({ keywords }: KeywordRankProps) {
  // 객체 형태면 배열로 변환
  const formattedKeywords: Keyword[] = Array.isArray(keywords)
    ? keywords.map((kw) =>
        typeof kw === "string" ? { keyword: kw, count: 1 } : kw
      )
    : Object.entries(keywords).map(([keyword, count]) => ({ keyword, count }));

  const topKeywords = [...formattedKeywords]
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  const rankStyle = (index: number): string => {
    switch (index) {
      case 0:
      case 1:
      case 2:
        return "text-white font-bold";
      default:
        return "text-slate-400";
    }
  };

  return (
    <div className="flex   divide-slate-700">
      {topKeywords.map((kw, index) => (
        <div
          key={index}
          className="flex items-center justify-between py-2 text-sm rounded-lg px-2 transition"
        >
          <span className={`flex-1 text-center ${rankStyle(index)}`}>
            {kw.keyword}
          </span>
        </div>
      ))}
    </div>
  );
}

export default TradeKeywords;
