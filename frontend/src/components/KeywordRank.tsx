import type { Keyword } from "../types/StockInfos";

interface KeywordRankProps {
  keywords: Record<string, number> | (Keyword | string)[];
}

function KeywordRank({ keywords }: KeywordRankProps) {
  // 객체 형태면 배열로 변환
  const formattedKeywords: Keyword[] = Array.isArray(keywords)
    ? keywords.map((kw) =>
        typeof kw === "string" ? { keyword: kw, count: 1 } : kw
      )
    : Object.entries(keywords).map(([keyword, count]) => ({ keyword, count }));

  const topKeywords = [...formattedKeywords]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  const rankColor = (index: number): string => {
    switch (index) {
      case 0:
        return "text-amber-400 font-bold";
      case 1:
        return "text-slate-300 font-bold";
      case 2:
        return "text-amber-700 font-bold";
      default:
        return "text-slate-400";
    }
  };
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
    <div className="flex flex-col divide-y divide-slate-700">
      <div className="flex justify-between pb-2 font-semibold text-slate-400 text-sm uppercase tracking-wide">
        <div className="w-12">순위</div>
        <div className="flex-1 text-center">키워드</div>
        <div className="w-12 text-right">횟수</div>
      </div>

      {topKeywords.map((kw, index) => (
        <div
          key={index}
          className="flex items-center justify-between py-2 text-sm hover:bg-slate-700/60 rounded-lg px-2 transition"
        >
          <span className={`w-12 ${rankColor(index)}`}>{index + 1}위</span>
          <span className={`flex-1 text-center ${rankStyle(index)}`}>
            {kw.keyword}
          </span>
          <span className={`text-right w-12 ${rankStyle(index)}`}>
            {kw.count}
          </span>
        </div>
      ))}
    </div>
  );
}

export default KeywordRank;
