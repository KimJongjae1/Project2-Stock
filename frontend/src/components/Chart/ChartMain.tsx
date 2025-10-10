// src/components/Chart/ChartMain.tsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { Payload } from "recharts/types/component/DefaultTooltipContent";
import type { StockInfos } from "../../types/StockInfos";

interface ChartProps {
  data: StockInfos[];
  term: string;
  dailyNewsCount: Record<string, number>;
}

function ChartMain({ data, term, dailyNewsCount }: ChartProps) {
  // 숫자 포맷
  function numberFormat(num: number) {
    return num.toLocaleString();
  }

  // chart용 데이터: dateString 추가 + dailyNewsCount 반영
  const chartData = data.map((d) => {
    const key = d.date.replace(/-/g, ""); // "2025-09-26" → "20250926"
    return {
      ...d,
      dateString: d.date,
      newsCount: dailyNewsCount[key] ?? 0,
    };
  });

  // Custom Tooltip
  const CustomTooltip = ({
    active,
    payload,
    label,
  }: {
    active?: boolean;
    payload?: Payload<number, string>[];
    label?: string;
  }) => {
    if (active && payload && payload.length > 0) {
      const pricePoint = payload.find((p) => p.dataKey === "endPrice");
      const newsPoint = payload.find((p) => p.dataKey === "newsCount");

      return (
        <div className="bg-slate-800 text-white p-3 rounded-lg shadow-lg border border-slate-600">
          <p className="text-base">
            날짜: <span className="font-bold text-amber-300">{label}</span>
          </p>
          {pricePoint && (
            <p className="text-base">
              종가:{" "}
              <span className="font-bold text-amber-300">
                {numberFormat(pricePoint.value ?? 0)}
              </span>
            </p>
          )}
          {newsPoint && (
            <p className="text-base">
              뉴스 수:{" "}
              <span className="font-bold text-emerald-400">
                {numberFormat(newsPoint.value ?? 0)}
              </span>
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  if (!chartData || chartData.length === 0) return null;

  // 최신 데이터 찾기
  const latestData = chartData.reduce((prev, curr) =>
    curr.dateString > prev.dateString ? curr : prev
  );
  const latestDateString = latestData.dateString;

  // 날짜 순 정렬
  const filteredData = chartData
    .sort((a, b) => (a.dateString > b.dateString ? 1 : -1))
    .filter((d) => d.dateString <= latestDateString);

  // X축 interval 계산
  let xInterval: number | "preserveStartEnd" = 0;
  if (term === "사용자 지정") {
    const len = filteredData.length;
    if (len <= 7) xInterval = 0;
    else if (len <= 30) xInterval = 6;
    else if (len <= 180) xInterval = 29;
    else if (len <= 365) xInterval = 89;
    else if (len <= 365 * 3) xInterval = 179;
    else if (len <= 365 * 5) xInterval = 364;
    else xInterval = Math.floor(len / 4);
  } else {
    switch (term) {
      case "1주":
        xInterval = 0;
        break;
      case "1개월":
        xInterval = 6;
        break;
      case "6개월":
        xInterval = 29;
        break;
      case "1 년":
        xInterval = 89;
        break;
      case "3 년":
        xInterval = 179;
        break;
      case "5 년":
        xInterval = 364;
        break;
      default:
        xInterval = 0;
    }
  }

  return (
    <div className="w-full h-96">
      <div className="w-full h-96 bg-slate-900 rounded-xl p-2">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={filteredData}>
            <XAxis
              dataKey="dateString"
              stroke="#cbd5e1"
              interval={xInterval}
              tick={{ fontSize: 12 }}
            />
            <YAxis yAxisId="left" stroke="#cbd5e1" width={60} />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#10b981"
              width={60}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="endPrice"
              stroke="#fbbf24"
              strokeWidth={2}
              dot={{ r: 4, stroke: "#fbbf24", fill: "#fbbf24" }}
              activeDot={{ r: 6, stroke: "#f59e0b", fill: "#fbbf24" }}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="newsCount"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 3, stroke: "#10b981", fill: "#10b981" }}
              activeDot={{ r: 5, stroke: "#059669", fill: "#10b981" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default ChartMain;
