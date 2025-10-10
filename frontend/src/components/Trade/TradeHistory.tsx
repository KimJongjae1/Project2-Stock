import type { UserTradeHistory } from "../../types/Trade";

interface HistoryCardProps {
  tradeHistory: UserTradeHistory[];
}

function TradeHistory({ tradeHistory }: HistoryCardProps) {
  const formatDateTime = (dateStr: string | Date): string => {
    const date = new Date(dateStr);
    const YYYY = date.getFullYear();
    const MM = (date.getMonth() + 1).toString().padStart(2, "0");
    const DD = date.getDate().toString().padStart(2, "0");
    const hh = date.getHours().toString().padStart(2, "0");
    const mm = date.getMinutes().toString().padStart(2, "0");
    const ss = date.getSeconds().toString().padStart(2, "0");
    return `${YYYY}-${MM}-${DD} ${hh}:${mm}:${ss}`;
  };

  return (
    <>
      {tradeHistory.slice(0, 10).map((h, idx) => (
        <div key={idx} className="pb-1">
          <div className="bg-slate-800 text-white rounded-2xl shadow-lg p-4 border border-slate-700 flex flex-col gap-1">
            <div
              className={
                h.tradeType === "BUY" ? "text-green-400" : "text-red-400"
              }
            >
              {(h.price * h.volume).toLocaleString()} 원 ({" "}
              {h.price.toLocaleString()} 원 * {h.volume} 주 )
            </div>
            <div className="text-slate-300 text-sm">
              {formatDateTime(h.createdAt)}
            </div>
          </div>
        </div>
      ))}
    </>
  );
}

export default TradeHistory;
