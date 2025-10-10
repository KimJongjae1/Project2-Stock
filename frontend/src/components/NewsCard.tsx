// NewsCard.tsx
import { Link } from "react-router";
import type { News } from "../types/StockInfos";

interface NewsCardProps {
  news: News[];
}

function NewsCard({ news }: NewsCardProps) {
  function formatDate(dateStr: string): string {
    if (dateStr.length !== 8) return dateStr; // 예외 처리
    const year = dateStr.slice(0, 4);
    const month = dateStr.slice(4, 6);
    const day = dateStr.slice(6, 8);
    return `${year}-${month}-${day}`;
  }
  return (
    <>
      {news.map((n, idx) => (
        <div key={idx} className="pb-1">
          <div className=" bg-slate-800 text-white rounded-2xl shadow-lg p-4 border border-slate-700 hover:bg-slate-700 transition">
            <Link to={n.url} target="_blank" rel="noopener noreferrer">
              <div className="flex justify-between gap-2">
                <div className="font-semibold hover:underline">{n.title}</div>
                <div className="text-slate-300 whitespace-nowrap">
                  {formatDate(n.date)}
                </div>
              </div>
            </Link>
          </div>
        </div>
      ))}
    </>
  );
}

export default NewsCard;
