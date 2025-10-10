import type { FC } from "react";

interface ChartNewsProps {
  analysis: string;
}

const ChartNews: FC<ChartNewsProps> = ({ analysis }) => {
  return (
    <div className="font-bold bg-slate-800 text-white rounded-2xl shadow-lg p-4 border border-slate-700 hover:bg-slate-700 transition">
      <div className="whitespace-pre-line">{analysis}</div>
    </div>
  );
};

export default ChartNews;
