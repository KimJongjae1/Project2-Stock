import {
  ResponsiveContainer,
  ComposedChart,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Bar,
  Customized,
  Line,
  Brush,
  Cell,
} from "recharts";
import { useMemo, useState } from "react";

type Candle = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export default function CandleChart({ data }: { data: Candle[] }) {
  // moving averages
  const withMA = useMemo(() => {
    const calcMA = (period: number) => {
      const out = new Array<number | null>(data.length).fill(null);
      let sum = 0;
      for (let i = 0; i < data.length; i++) {
        sum += data[i].close;
        if (i >= period) sum -= data[i - period].close;
        if (i >= period - 1) out[i] = Math.round(sum / period);
      }
      return out;
    };
    const ma5 = calcMA(5);
    const ma20 = calcMA(20);
    const ma60 = calcMA(60);
    return data.map((d, i) => ({
      ...d,
      ma5: ma5[i],
      ma20: ma20[i],
      ma60: ma60[i],
    }));
  }, [data]);

  // brush range (indices)
  const [range, setRange] = useState<{
    startIndex: number;
    endIndex: number;
  } | null>(null);
  const view = useMemo(() => {
    const start = range?.startIndex ?? 0; // 기본 전체 구간 표시
    const end = range?.endIndex ?? withMA.length - 1;
    return withMA.slice(start, end + 1);
  }, [withMA, range]);
  const priceMin = view.length
    ? Math.min(...view.map((d) => Math.min(d.open, d.high, d.low, d.close)))
    : 0;
  const priceMax = view.length
    ? Math.max(...view.map((d) => Math.max(d.open, d.high, d.low, d.close)))
    : 1;
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const d = payload[0].payload as Candle;
      return (
        <div className="bg-slate-800 text-white p-3 rounded-lg border border-slate-600">
          <div>{label}</div>
          <div>시가: {d.open.toLocaleString()}</div>
          <div>고가: {d.high.toLocaleString()}</div>
          <div>저가: {d.low.toLocaleString()}</div>
          <div>종가: {d.close.toLocaleString()}</div>
          <div>거래량: {d.volume.toLocaleString()}</div>
        </div>
      );
    }
    return null;
  };

  const CandleLayer = (props: any) => {
    const { xAxisMap, yAxisMap, data: chartData } = props ?? {};
    if (!xAxisMap || !yAxisMap) return null;
    const xKeys = Object.keys(xAxisMap);
    const yKeys = Object.keys(yAxisMap);
    if (xKeys.length === 0 || yKeys.length === 0) return null;
    const xAxis: any = (xAxisMap as any)[xKeys[0]];
    const yAxis: any = (yAxisMap as any)[yKeys[0]];
    const xScale = xAxis?.scale;
    const yScale = yAxis?.scale;
    if (!xScale || !yScale) return null;
    const band = (xAxis.bandSize ||
      (xScale.bandwidth ? xScale.bandwidth() : 8)) as number;
    const cw = Math.max(3, band * 0.6); // 최소 폭 강화
    // const left = offset?.left ?? 0;
    const data: Candle[] = Array.isArray(chartData) ? chartData : [];
    return (
      <g>
        {data.map((d: Candle, idx: number) => {
          const xv = xScale(d.date);
          if (xv == null) return null;
          const x = (xv as number) + band / 2;
          const yOpen = yScale(d.open) as number;
          const yClose = yScale(d.close) as number;
          const yHigh = yScale(d.high) as number;
          const yLow = yScale(d.low) as number;
          const top = Math.min(yOpen, yClose);
          const bottom = Math.max(yOpen, yClose);
          const color = d.close >= d.open ? "#ef4444" : "#3b82f6";
          return (
            <g key={idx}>
              <line
                x1={x}
                x2={x}
                y1={yHigh}
                y2={yLow}
                stroke={color}
                strokeWidth={1}
              />
              <rect
                x={x - cw / 2}
                y={top}
                width={cw}
                height={Math.max(1, bottom - top)}
                fill={color}
                stroke={color}
              />
            </g>
          );
        })}
      </g>
    );
  };

  return (
    <div className="w-full h-[480px]">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={view}
          margin={{ top: 10, right: 20, bottom: 10, left: 0 }}
          barCategoryGap={"70%"}
        >
          <CartesianGrid stroke="#334155" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="#cbd5e1"
            tick={{ fontSize: 12 }}
            interval={Math.max(0, Math.floor(view.length / 10))}
          />
          <YAxis
            yAxisId="price"
            stroke="#cbd5e1"
            domain={[priceMin * 0.98, priceMax * 1.02]}
          />
          <YAxis
            yAxisId="vol"
            orientation="right"
            stroke="#94a3b8"
            allowDecimals={false}
            tickFormatter={(v) => (v as number).toLocaleString()}
          />
          <Tooltip content={<CustomTooltip />} />
          {/* Hidden line to bind price axis domain (safety) */}
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="close"
            stroke="transparent"
            dot={false}
            isAnimationActive={false}
          />
          {/* Volume bars */}
          <Bar yAxisId="vol" dataKey="volume" opacity={0.5} barSize={4}>
            {view.map((d, i) => (
              <Cell
                key={`v-${i}`}
                fill={d.close >= d.open ? "#ef4444" : "#3b82f6"}
              />
            ))}
          </Bar>
          {/* Candle layer */}
          <Customized yAxisId="price" component={<CandleLayer />} />
          {/* Range selector (zoom) */}
          <Brush
            dataKey="date"
            height={28}
            travellerWidth={10}
            onChange={(x: any) =>
              setRange(
                x?.startIndex != null && x?.endIndex != null
                  ? { startIndex: x.startIndex, endIndex: x.endIndex }
                  : null
              )
            }
            stroke="#94a3b8"
            fill="#0f172a"
            tickFormatter={(d: any) => String(d)}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
