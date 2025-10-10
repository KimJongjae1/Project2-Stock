import { useEffect, useMemo, useState } from "react";
import axios from "axios";

export const API_SERVER_HOST =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8080";
  
type InfluenceItem = {
  rank: number;
  company: string;
  score: number;
  relative: number;
  score_type: string;
};

export default function InfluencePage() {
  const [data, setData] = useState<InfluenceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const url =
          API_SERVER_HOST + "/api/influence?path=s3%3A%2F%2Fcheesecrust-spark-data-bucket%2Foutputs%2Fpagerank%2Fpagerank%2F&top=20";
        const res = await axios.get<InfluenceItem[]>(url, { timeout: 15000 });
        setData(res.data ?? []);
      } catch (e: any) {
        setError(e?.message ?? "데이터를 불러오지 못했습니다.");
        setData([]);
      } finally {
        setLoading(false);
      }
    };
    void fetchData();
  }, []);

  const top20 = useMemo(() => data.slice(0, 20), [data]);
  const maxScore = useMemo(() => (top20.length ? Math.max(...top20.map((d) => d.score)) : 1), [top20]);

  return (
    <div className="min-h-screen p-5">
      <h1 className="text-2xl font-extrabold text-white mb-5">기업 영향력</h1>

      {loading && (
        <div className="grid place-items-center py-20">
          <div className="w-8 h-8 animate-spin rounded-full border-2 border-slate-300 border-t-amber-500" />
        </div>
      )}
      {error && (
        <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 text-rose-200 px-4 py-2 mb-4">
          {error}
        </div>
      )}

      {!loading && !error && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 좌: 버블 차트 */}
          <section className="lg:col-span-2 rounded-2xl bg-slate-900 p-6 border border-slate-700">
            <h2 className="text-white font-bold mb-4">상위 20개 영향력 (버블 · score %)</h2>
            <div className="overflow-x-auto">
              <svg width="100%" viewBox="0 0 800 520">
                {(() => {
                  const cols = 5; // 5 x 4 = 20
                  const cellW = 150; // 각 셀 가로 간격
                  const cellH = 130; // 각 셀 세로 간격 (버블 확대에 맞춰 약간 증가)
                  const startX = 80; // 좌측 여백
                  const startY = 70; // 상단 여백
                  const minR = 20;
                  const maxR = 64;
                  return top20.map((d, idx) => {
                    const col = idx % cols;
                    const row = Math.floor(idx / cols);
                    const cx = startX + col * cellW;
                    const cy = startY + row * cellH;
                    const r = minR + ((d.score / maxScore) || 0) * (maxR - minR);
                    return (
                      <g key={d.rank} transform={`translate(${cx}, ${cy})`}>
                        <circle r={r} fill="#f59e0b" fillOpacity={0.9} />
                        <text y={4} textAnchor="middle" fill="#0f172a" fontSize={12} fontWeight={700}>
                          {(d.score * 100).toFixed(1)}%
                        </text>
                        <text y={r + 16} textAnchor="middle" fill="#cbd5e1" fontSize={12} className="pointer-events-none">
                          {d.company}
                        </text>
                      </g>
                    );
                  });
                })()}
              </svg>
            </div>
          </section>

          {/* 우: 표 */}
          <section className="rounded-2xl bg-slate-900 p-6 border border-slate-700">
            <h2 className="text-white font-bold mb-4">랭킹 테이블</h2>
            <div className="max-h-[600px] overflow-auto scroll-dark">
              <table className="w-full text-base table-fixed">
                <colgroup>
                  <col className="w-10" />
                  <col />
                  <col className="w-28" />
                </colgroup>
                <thead>
                  <tr className="text-slate-400 text-base">
                    <th className="py-1 text-left">순위</th>
                    <th className="py-1 text-left">기업</th>
                    <th className="py-1 text-right">Score (%)</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((d) => (
                    <tr key={d.rank} className="border-t border-slate-700 text-slate-200 text-base">
                      <td className="py-1">{d.rank}</td>
                      <td className="py-1 truncate" title={d.company}>{d.company}</td>
                      <td className="py-1 text-right whitespace-nowrap">{(d.score * 100).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}


