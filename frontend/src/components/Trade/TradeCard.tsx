import { useState } from "react";
import { useTrade } from "../../hooks/useTrade";
import type { UserAsset, UserStockHoldingDto } from "../../types/Trade";
import type { TradeHistoryDto } from "../../types/Trade";

interface TradeCardProps {
  ticker: string;
  stockPrice: number;
  userTrade: UserAsset;
  userHolding?: UserStockHoldingDto | null;
  onTrade?: (type: "BUY" | "SELL", amount: number) => void; // 로컬 상태 업데이트용
  onTradeSuccess?: () => void; // 거래 성공 시 추가 처리
  setUserHolding?: (holding: UserStockHoldingDto) => void; // 즉시 보유 수량 업데이트용
  marketOpen: boolean; // 장 마감 체크
}

function TradeCard({
  ticker,
  stockPrice,
  userTrade,
  userHolding,
  onTrade,
  onTradeSuccess,
  setUserHolding,
  marketOpen,
}: TradeCardProps) {
  const [amount, setAmount] = useState<number>(0);
  const { loading, error, buyStock, sellStock, clearError } = useTrade();

  const profitRate =
    userHolding && userHolding.avgBuyPrice
      ? ((stockPrice - userHolding.avgBuyPrice) / userHolding.avgBuyPrice) * 100
      : 0;

  const handleBuy = async () => {
    if (!marketOpen) {
      alert("장이 마감되었습니다. 거래할 수 없습니다.");
      return;
    }

    if (amount <= 0) {
      alert("수량을 입력해주세요.");
      return;
    }

    const totalCost = amount * stockPrice;
    if (totalCost > userTrade.cash) {
      alert("보유 현금이 부족합니다.");
      return;
    }

    try {
      clearError();
      const result: TradeHistoryDto | null = await buyStock({
        ticker,
        price: stockPrice,
        volume: amount,
      });

      if (result) {
        alert(
          `매수 완료!\n종목: ${ticker}\n수량: ${amount}주\n총 금액: ${result.totalPrice.toLocaleString()}원`
        );

        if (setUserHolding) {
          const newQuantity = (userHolding?.quantity ?? 0) + amount;
          const newAvgPrice =
            userHolding && userHolding.avgBuyPrice
              ? (userHolding.avgBuyPrice * (userHolding.quantity ?? 0) +
                  stockPrice * amount) /
                newQuantity
              : stockPrice;

          setUserHolding({
            ticker,
            quantity: newQuantity,
            avgBuyPrice: newAvgPrice,
          });
        }

        if (onTrade) onTrade("BUY", amount);
        if (onTradeSuccess) onTradeSuccess();
        setAmount(0);
      }
    } catch (err) {
      console.error("매수 실패:", err);
      alert("매수 주문 처리 중 오류가 발생했습니다.");
    }
  };

  const handleSell = async () => {
    if (!marketOpen) {
      alert("장이 마감되었습니다. 거래할 수 없습니다.");
      return;
    }

    if (amount <= 0) {
      alert("수량을 입력해주세요.");
      return;
    }

    if ((userHolding?.quantity ?? 0) < amount) {
      alert("보유 주식이 부족합니다.");
      return;
    }

    try {
      clearError();
      const result: TradeHistoryDto | null = await sellStock({
        ticker,
        price: stockPrice,
        volume: amount,
      });

      if (result) {
        alert(
          `매도 완료!\n종목: ${ticker}\n수량: ${amount}주\n총 금액: ${result.totalPrice.toLocaleString()}원`
        );

        if (setUserHolding) {
          setUserHolding({
            ticker,
            quantity: (userHolding?.quantity ?? 0) - amount,
            avgBuyPrice: userHolding?.avgBuyPrice ?? 0,
          });
        }

        if (onTrade) onTrade("SELL", amount);
        if (onTradeSuccess) onTradeSuccess();
        setAmount(0);
      }
    } catch (err) {
      console.error("매도 실패:", err);
      alert("매도 주문 처리 중 오류가 발생했습니다.");
    }
  };

  const increase = () => setAmount((prev) => prev + 1);
  const decrease = () => setAmount((prev) => (prev > 0 ? prev - 1 : 0));
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (/^\d*$/.test(value)) {
      setAmount(Number(value));
    }
  };

  const inputColor = amount === 0 ? "text-slate-400" : "text-white";

  return (
    <div className="bg-slate-800 text-white rounded-2xl shadow-lg p-6 space-y-6">
      {/* 장 마감 안내 */}
      {!marketOpen && (
        <div className="bg-yellow-500/20 border border-yellow-400 rounded-lg p-3 text-red-500 text-center font-semibold mb-3">
          장이 마감되었습니다.
        </div>
      )}

      {error && (
        <div className="bg-red-500/20 border border-red-500 rounded-lg p-3 text-red-300 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-3">
        <div className="flex justify-between border-b border-slate-700 pb-2">
          <span>총 자산</span>
          <span className="font-semibold">
            {userTrade.originalMoney.toLocaleString()} 원
          </span>
        </div>
        <div className="flex justify-between border-b border-slate-700 pb-2">
          <span>현재 보유 현금</span>
          <span className="font-semibold">
            {userTrade.cash.toLocaleString()} 원
          </span>
        </div>
        <div className="flex justify-between border-b border-slate-700 pb-2">
          <span>총 보유 주식 금액</span>
          <span className="font-semibold">
            {userTrade.haveStock.toLocaleString()} 원
          </span>
        </div>
        <div className="flex justify-between border-b border-slate-700 pb-2">
          <span>현재 보유 주식 수</span>
          <span className="font-semibold">{userHolding?.quantity ?? 0} 주</span>
        </div>
        <div className="flex justify-between">
          <span>종목별 손익률</span>
          <span
            className={`font-semibold ${
              profitRate >= 0 ? "text-green-400" : "text-red-400"
            }`}
          >
            {profitRate >= 0 ? "+" : ""}
            {profitRate.toFixed(2)}%
          </span>
        </div>
      </div>

      <div className="space-y-3">
        <label className="block text-sm text-slate-300">투자 수량</label>
        <div className="flex items-center gap-2">
          <input
            type="text"
            className={`text-center ${inputColor} bg-slate-700 rounded py-1 px-5 border border-slate-600 focus:border-blue-500 focus:outline-none`}
            value={amount}
            onChange={handleChange}
            disabled={loading || !marketOpen}
            placeholder="0"
          />
          <button
            className="w-10 bg-green-500 px-3 py-1 rounded text-white font-semibold hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={increase}
            disabled={loading || !marketOpen}
          >
            +
          </button>
          <button
            className="w-10 bg-red-500 px-3 py-1 rounded text-white font-semibold hover:bg-red-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={decrease}
            disabled={loading || !marketOpen}
          >
            -
          </button>
        </div>

        <div className="text-sm text-slate-300 text-center bg-slate-700 rounded py-2">
          거래금액: {(amount * stockPrice).toLocaleString()}원
        </div>

        <div className="flex gap-3">
          <button
            className="flex-1 bg-green-500 px-4 py-2 rounded-lg text-white font-semibold hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleBuy}
            disabled={loading || amount <= 0 || !marketOpen}
          >
            {loading ? "처리중..." : "매수"}
          </button>
          <button
            className="flex-1 bg-red-500 px-4 py-2 rounded-lg text-white font-semibold hover:bg-red-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={handleSell}
            disabled={loading || amount <= 0 || !marketOpen}
          >
            {loading ? "처리중..." : "매도"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default TradeCard;
