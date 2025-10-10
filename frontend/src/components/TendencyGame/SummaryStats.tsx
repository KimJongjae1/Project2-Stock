import type { ReactNode } from "react";

export type SummaryStatItem = {
  id: string;
  label: string;
  value: string;
  helper?: string;
  tone?: "default" | "positive" | "negative";
  icon?: ReactNode;
};

const toneClass = (tone: SummaryStatItem["tone"]) => {
  switch (tone) {
    case "positive":
      // 💡 어두운 배경에서 대비를 위해 더 밝은 에메랄드 색상으로 조정했습니다.
      return "text-emerald-400";
    case "negative":
      // 💡 어두운 배경에서 대비를 위해 더 밝은 로즈 색상으로 조정했습니다.
      return "text-rose-400";
    default:
      // 💡 어두운 배경에서 미묘하고 읽기 쉬운 색상으로 조정했습니다.
      return "text-slate-400";
  }
};

export default function SummaryStats({ items }: { items: SummaryStatItem[] }) {
  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
      {items.map((item) => (
        <article
          key={item.id}
          // 💡 어두운 테마 배경, 그림자, 링 스타일을 적용했습니다.
          className="rounded-2xl bg-slate-800/80 px-4 py-3 shadow-xl backdrop-blur-sm ring-1 ring-slate-600"
        >
          {/* 💡 가독성을 위해 텍스트 색상을 조정했습니다. */}
          <p className="text-[13px] font-medium text-slate-400">{item.label}</p>
          {/* 💡 가독성을 위해 텍스트 색상을 조정했습니다. */}
          <p className="mt-2 text-lg font-semibold text-white">{item.value}</p>
          {item.helper ? (
            <p className={`mt-1 text-xs font-medium ${toneClass(item.tone)}`}>{item.helper}</p>
          ) : null}
        </article>
      ))}
    </section>
  );
}