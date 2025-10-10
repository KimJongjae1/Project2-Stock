import type { FinishResultResponse } from "../../api/tendencyGame";

interface GameFinishModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGoHome: () => void;
  result: FinishResultResponse | null;
}

export default function GameFinishModal({ isOpen, onClose, onGoHome, result }: GameFinishModalProps) {
  if (!isOpen || !result) return null;

  const formatCurrency = (value: number) => new Intl.NumberFormat("ko-KR").format(Math.round(value));
  const formatPercentage = (value: number) => `${value > 0 ? "+" : ""}${value.toFixed(2)}%`;

  const handleGoHome = () => {
    onClose();
    onGoHome();
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-300">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-6 w-96 space-y-5 transform transition-transform duration-300 scale-100">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
            <svg className="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="font-bold text-xl text-black dark:text-white mb-2">
            게임 종료!
          </h2>
          <p className="text-slate-600 dark:text-slate-300 text-sm">
            투자 성향 분석이 완료되었습니다.
          </p>
        </div>

        <div className="bg-slate-50 dark:bg-slate-700 rounded-xl p-4 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-slate-600 dark:text-slate-300 text-sm">총 자산</span>
            <span className="font-bold text-lg text-black dark:text-white">{formatCurrency(result.totalAsset)}원</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-600 dark:text-slate-300 text-sm">실현 손익</span>
            <span className={`font-semibold ${result.realizedProfit >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
              {formatCurrency(result.realizedProfit)}원
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-600 dark:text-slate-300 text-sm">수익률</span>
            <span className={`font-semibold ${result.totalYield >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
              {formatPercentage(result.totalYield)}
            </span>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-slate-200 hover:bg-slate-300 dark:bg-slate-600 dark:hover:bg-slate-500 text-slate-800 dark:text-slate-200 font-semibold py-3 px-4 rounded-xl transition-colors duration-200"
          >
            다시 보기
          </button>
          <button
            onClick={handleGoHome}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl transition-colors duration-200"
          >
            홈으로
          </button>
        </div>
      </div>
    </div>
  );
}
