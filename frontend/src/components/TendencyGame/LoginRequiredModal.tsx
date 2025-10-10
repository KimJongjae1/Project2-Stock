interface LoginRequiredModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGoHome: () => void;
}

export default function LoginRequiredModal({ isOpen, onClose, onGoHome }: LoginRequiredModalProps) {
  if (!isOpen) return null;

  const handleGoHome = () => {
    onClose();
    onGoHome();
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-300">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-6 w-80 space-y-5 transform transition-transform duration-300 scale-100">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
            <svg className="w-8 h-8 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 className="font-bold text-xl text-black dark:text-white mb-2">
            로그인이 필요합니다
          </h2>
          <p className="text-slate-600 dark:text-slate-300 text-sm">
            투자 성향 게임을 이용하려면 로그인해주세요.
          </p>
        </div>

        <div className="bg-slate-50 dark:bg-slate-700 rounded-xl p-4">
          <div className="text-center">
            <p className="text-slate-600 dark:text-slate-300 text-sm">
              로그인 후 다양한 투자 게임과<br />
              개인화된 투자 정보를 이용하실 수 있습니다.
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 bg-slate-200 hover:bg-slate-300 dark:bg-slate-600 dark:hover:bg-slate-500 text-slate-800 dark:text-slate-200 font-semibold py-3 px-4 rounded-xl transition-colors duration-200"
          >
            취소
          </button>
          <button
            onClick={handleGoHome}
            className="flex-1 bg-amber-600 hover:bg-amber-700 text-white font-semibold py-3 px-4 rounded-xl transition-colors duration-200"
          >
            홈으로
          </button>
        </div>
      </div>
    </div>
  );
}
