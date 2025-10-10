import type { Term } from "../../types/StockInfos";

interface TimeTermProps {
  terms: Term[];
  selectedTerm: Term; // 현재 선택된 기간
  onSelect: (term: Term) => void;
}

export default function TimeTerm({
  terms,
  selectedTerm,
  onSelect,
}: TimeTermProps) {
  return (
    <div className="flex flex-wrap gap-3 justify-center lg:justify-start">
      {terms.map((term, index) => {
        const isSelected = selectedTerm.text === term.text;
        return (
          <button
            key={index}
            onClick={() => onSelect(term)}
            className={`px-4 py-2 min-w-[70px] rounded-xl font-semibold transition-all duration-200
              ${
                isSelected
                  ? "bg-gradient-to-r from-amber-500 to-amber-600 text-white shadow-lg scale-105"
                  : "bg-slate-700/80 text-slate-300 hover:bg-slate-600 hover:text-white hover:shadow-md"
              }`}
          >
            {term.text}
          </button>
        );
      })}
    </div>
  );
}
