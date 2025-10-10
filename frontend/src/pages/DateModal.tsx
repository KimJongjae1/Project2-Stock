import { useState } from "react";

interface CustomDateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (start: Date, end: Date) => void;
}

function DateModal({ isOpen, onClose, onConfirm }: CustomDateModalProps) {
  const today = new Date();
  const fiveYearsAgo = new Date();
  fiveYearsAgo.setFullYear(today.getFullYear() - 5);

  const [start, setStart] = useState(today.toISOString().slice(0, 10));
  const [end, setEnd] = useState(today.toISOString().slice(0, 10));

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-300">
      <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl p-6 w-80 space-y-5 transform transition-transform duration-300 scale-100">
        <h2 className="font-bold text-lg text-black dark:text-white text-center">
          사용자 지정 기간 선택
        </h2>
        <div className="flex flex-col gap-4 text-black dark:text-white">
          <label className="flex flex-col gap-1 text-sm font-medium">
            시작일:
            <input
              type="date"
              max={today.toISOString().slice(0, 10)}
              min={fiveYearsAgo.toISOString().slice(0, 10)}
              value={start}
              onChange={(e) => setStart(e.target.value)}
              className="border border-gray-300 dark:border-gray-600 p-2 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-amber-400 dark:bg-slate-700 dark:text-white"
            />
          </label>
          <label className="flex flex-col gap-1 text-sm font-medium">
            종료일:
            <input
              type="date"
              max={today.toISOString().slice(0, 10)}
              min={start}
              value={end}
              onChange={(e) => setEnd(e.target.value)}
              className="border border-gray-300 dark:border-gray-600 p-2 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-amber-400 dark:bg-slate-700 dark:text-white"
            />
          </label>
        </div>
        <div className="flex justify-end gap-3 mt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500 text-black dark:text-white font-semibold transition-all duration-200 shadow-sm hover:shadow-md"
          >
            취소
          </button>
          <button
            onClick={() => {
              onConfirm(new Date(start), new Date(end));
              onClose();
            }}
            className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-semibold transition-all duration-200 shadow-sm hover:shadow-md active:scale-95"
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
}

export default DateModal;
