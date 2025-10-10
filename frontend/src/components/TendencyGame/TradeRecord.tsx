type Item = { gameTradeType: "BUY" | "SELL"; gameTradePrice: number; gameTradeDate: string; qty?: number };
type Props = { items: Item[] };

const formatCurrency = (v: number) => `${new Intl.NumberFormat("ko-KR").format(Math.round(v))}원`;

export default function TradeRecord({ items }: Props) {
  return (
    // 💡 배경, 그림자, 테두리 스타일을 어두운 테마에 맞게 변경
    <div className="rounded-2xl bg-gradient-to-br from-slate-800 to-slate-700 p-5 shadow-xl border border-slate-600 text-white">
      <div className="mb-3 flex items-center justify-between">
        {/* 💡 텍스트 색상 변경 */}
        <div className="font-bold text-white">최근 매수/매도 내역</div>
      </div>
      <div className="max-h-96 overflow-auto">
        <table className="w-full text-sm">
          <thead>
            {/* 💡 텍스트 색상 변경 */}
            <tr className="text-slate-400">
              <th className="py-2 text-left font-medium">구분</th>
              <th className="py-2 text-right font-medium">가격</th>
              <th className="py-2 text-right font-medium">수량</th>
              <th className="py-2 text-right font-medium">일자</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={4} className="py-6 text-center text-slate-400">
                  거래 내역이 없습니다.
                </td>
              </tr>
            ) : (
              items.map((t, idx) => (
                // 💡 테두리 색상과 텍스트 색상 변경
                <tr key={`${t.gameTradeDate}-${idx}`} className="border-t border-slate-600 text-slate-300">
                  {/* 💡 매수/매도 색상 변경 */}
                  <td className={`py-2 font-semibold ${t.gameTradeType === "BUY" ? "text-emerald-400" : "text-rose-400"}`}>
                    {t.gameTradeType === "BUY" ? "매수" : "매도"}
                  </td>
                  <td className="py-2 text-right">{formatCurrency(t.gameTradePrice)}</td>
                  <td className="py-2 text-right">{t.qty ?? "-"}</td>
                  <td className="py-2 text-right">{t.gameTradeDate.slice(0, 10)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}