type Props = {
  keywords: string[];
  news: Array<{ title: string; url: string; date: string }>;
};

export default function StockHighlights({ keywords, news }: Props) {
  return (
    // 💡 bg-slate-900과 rounded-xl를 적용
    <div className="rounded-xl bg-slate-900 p-5">
      <section className="mb-4">
        {/* 💡 텍스트 색상을 배경에 맞게 변경 */}
        <h3 className="mb-2 text-sm font-semibold text-white">주요 키워드</h3>
        {keywords.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {keywords.map((word, idx) => (
              <span
                key={`${word}-${idx}`}
                // 💡 배경에 맞게 색상을 변경
                className="rounded-full bg-slate-700 px-2.5 py-1 text-xs font-semibold text-white"
              >
                {word}
              </span>
            ))}
          </div>
        ) : (
          // 💡 텍스트 색상을 배경에 맞게 변경
          <p className="text-xs text-slate-400">표시할 키워드가 없습니다.</p>
        )}
      </section>

      <section>
        {/* 💡 텍스트 색상을 배경에 맞게 변경 */}
        <h3 className="mb-2 text-sm font-semibold text-white">관련 뉴스</h3>
        {news.length > 0 ? (
          <ul className="space-y-2">
            {news.map((n, idx) => (
              <li key={`${n.url}-${idx}`} className="rounded-xl border border-slate-600 bg-slate-800 px-4 py-3">
                <a href={n.url} target="_blank" rel="noreferrer" className="font-semibold text-white hover:underline">
                  {n.title}
                </a>
                <div className="mt-1 text-xs text-slate-500">{n.date}</div>
              </li>
            ))}
          </ul>
        ) : (
          // 💡 텍스트 색상을 배경에 맞게 변경
          <p className="text-xs text-slate-400">관련 뉴스가 없습니다.</p>
        )}
      </section>
    </div>
  );
}