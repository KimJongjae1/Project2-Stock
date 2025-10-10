import * as React from "react";
import type { MyPageData, TradeHistoryEntry } from "../../types/MyPageData";
import { Link } from "react-router";

type Props = {
  items?: MyPageData["tradeHistory"];
  account?: MyPageData["account"];
  step?: number;
};

export default function TradeHistory({
  items = [],
  account,
  step = 10,
}: Props) {
  const empty = !items || items.length === 0;

  const originalMoney = account?.originalMoney ?? 0;
  const cash = account?.cash ?? 0;
  const haveStock = account?.haveStock ?? 0;
  const totalAsset = account?.totalAsset ?? cash + haveStock;
  const returnPct =
    account?.returnPct ??
    (originalMoney > 0
      ? ((totalAsset - originalMoney) * 100) / originalMoney
      : null);

  // ---- 포맷터 ----
  const won = (n: number) => n.toLocaleString("ko-KR");
  const ts = (iso: string) => new Date(iso).toLocaleString();

  // ---- 색상 헬퍼 ----
  const colors = (t: TradeHistoryEntry["tradeType"]) =>
    t === "BUY"
      ? {
          badge: "bg-red-500/20 text-red-300 border-red-400/40",
          sign: "-",
          delta: "text-red-300",
        }
      : {
          badge: "bg-emerald-500/20 text-emerald-300 border-emerald-400/40",
          sign: "+",
          delta: "text-emerald-300",
        };

  const INITIAL = React.useMemo(
    () => Math.min(step, items.length),
    [items.length, step]
  );
  const [visibleCount, setVisibleCount] = React.useState(INITIAL);

  React.useEffect(() => {
    setVisibleCount(Math.min(step, items.length));
  }, [items, step]);

  const visibleItems = items.slice(0, visibleCount);
  const remain = Math.max(items.length - visibleCount, 0);
  const canMore = remain > 0;

  const handleMore = () => {
    setVisibleCount((v) => Math.min(v + step, items.length));
  };

  return (
    <section className="w-full bg-slate-700 backdrop-blur-xl rounded-2xl shadow-lg p-6 border border-slate-600 relative">
      <div className="flex items-center gap-2 mb-5">
        <h3 className="text-xl sm:text-2xl font-extrabold text-white">
          모의 투자 히스토리
        </h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <KpiCard label="총 자산" value={`${won(totalAsset)}원`} />
        <KpiCard label="총 현금" value={`${won(cash)}원`} />
        <KpiCard label="총 투자 금액" value={`${won(haveStock)}원`} />
        <KpiCard
          label="수익률"
          value={
            returnPct == null
              ? "-"
              : `${(Math.round(returnPct * 100) / 100).toFixed(2)}%`
          }
        />
      </div>

      {/* 리스트 */}
      {empty ? (
        <div className="text-center py-8">
          <div className="text-slate-400 mb-4">투자 내역이 없습니다.</div>
          <Link
            to="/trade"
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-amber-600 text-white rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all"
          >
            모의투자 시작하기
          </Link>
        </div>
      ) : (
        <>
          <div className="flex flex-col gap-3.5">
            {visibleItems.map((it, idx) => {
              const { badge, sign, delta } = colors(it.tradeType);
              const totalPrice = it.price * it.volume;
              const signed = it.tradeType === "SELL" ? totalPrice : -totalPrice;

              return (
                <div
                  key={`${it.itemNo}-${it.createdAt}-${idx}`}
                  className="p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-slate-600 border border-slate-500 hover:bg-slate-500 hover:border-amber-400 transition-all"
                >
                  {/* 좌: 시간 + 회사명 */}
                  <div className="min-w-0">
                    <div className="text-slate-400 text-xs sm:text-sm">
                      {ts(it.createdAt)}
                    </div>
                    <div className="text-white font-semibold truncate">
                      {it.companyName}
                    </div>
                  </div>

                  {/* 우: 거래 요약 */}
                  <div className="flex items-center gap-3 sm:gap-4 flex-wrap">
                    {/* BUY/SELL 뱃지 */}
                    <span
                      className={`px-3 py-1 rounded-[10px] text-xs font-bold border ${badge}`}
                    >
                      {it.tradeType === "BUY" ? "매수" : "매도"}
                    </span>

                    {/* 체결가/수량 */}
                    <div className="px-3 py-1 rounded-[10px] text-sm font-bold text-amber-200 bg-slate-500/70 border border-slate-400">
                      {it.volume.toLocaleString()}주 · {won(it.price)}원
                    </div>

                    {/* 총금액(+/-) */}
                    <div
                      className={`px-3 py-1 rounded-[10px] text-sm font-bold bg-slate-500/70 border border-slate-400 ${delta}`}
                    >
                      {sign}
                      {won(Math.abs(signed))}원
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* 더보기 */}
          {canMore && (
            <div className="flex justify-center mt-5">
              <button
                type="button"
                onClick={handleMore}
                className="px-4 py-2 rounded-lg border border-slate-500 bg-slate-600 text-slate-200 hover:bg-slate-500 hover:border-amber-400 transition-all text-sm font-medium"
                aria-label="더보기"
              >
                + 더보기 {remain > step ? `(${step}/${remain})` : `(${remain})`}
              </button>
            </div>
          )}
        </>
      )}
    </section>
  );
}

function KpiCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl p-5 text-center bg-slate-600 border border-slate-500 hover:border-amber-400 transition-all">
      <div className="text-amber-400 text-xl sm:text-2xl font-bold">
        {value}
      </div>
      <div className="text-slate-300 text-xs">{label}</div>
    </div>
  );
}
