interface TradeSuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  tradeType: "BUY" | "SELL";
  quantity: number;
  price: number;
}

export default function TradeSuccessModal({ isOpen, onClose, tradeType, quantity, price }: TradeSuccessModalProps) {
  if (!isOpen) return null;

  const formatCurrency = (value: number) => new Intl.NumberFormat("ko-KR").format(Math.round(value));
  const totalAmount = price * quantity;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-300">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-6 w-80 space-y-5 transform transition-transform duration-300 scale-100">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
            <svg className="w-8 h-8 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="font-bold text-xl text-black dark:text-white mb-2">
            거래 성공!
          </h2>
          <p className="text-slate-600 dark:text-slate-300 text-sm">
            {tradeType === "BUY" ? "매수" : "매도"} 주문이 성공적으로 체결되었습니다.
          </p>
        </div>

        <div className="bg-slate-50 dark:bg-slate-700 rounded-xl p-4 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-slate-600 dark:text-slate-300 text-sm">거래 유형</span>
            <span className={`font-semibold ${tradeType === "BUY" ? "text-emerald-600" : "text-rose-600"}`}>
              {tradeType === "BUY" ? "매수" : "매도"}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-600 dark:text-slate-300 text-sm">수량</span>
            <span className="font-semibold text-black dark:text-white">{quantity}주</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-600 dark:text-slate-300 text-sm">체결가</span>
            <span className="font-semibold text-black dark:text-white">{formatCurrency(price)}원</span>
          </div>
          <div className="border-t border-slate-200 dark:border-slate-600 pt-3">
            <div className="flex justify-between items-center">
              <span className="text-slate-600 dark:text-slate-300 text-sm font-medium">총 거래금액</span>
              <span className="font-bold text-lg text-black dark:text-white">{formatCurrency(totalAmount)}원</span>
            </div>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-3 px-4 rounded-xl transition-colors duration-200"
        >
          확인
        </button>
      </div>
    </div>
  );
}
