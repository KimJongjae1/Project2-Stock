import {
  ResponsiveContainer,
  ComposedChart,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Customized,
  Line,
} from "recharts";

type Candle = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
  ma5?: number | null;
  ma20?: number | null;
  ma60?: number | null;
};

type CandleLayerProps = {
  xAxisMap?: any;
  yAxisMap?: any;
  data?: Candle[];
  upColor: string;
  downColor: string;
};

function CandleLayerComp(props: CandleLayerProps) {
  const {
    xAxisMap,
    yAxisMap,
    data: chartData,
    upColor,
    downColor,
  } = (props || {}) as CandleLayerProps;
  if (!xAxisMap || !yAxisMap) return null;
  const xKeys = Object.keys(xAxisMap);
  const yKeys = Object.keys(yAxisMap);
  if (xKeys.length === 0 || yKeys.length === 0) return null;
  const xAxis: any = (xAxisMap as any)[xKeys[0]];
  // 명시적으로 가격축 선택(yAxisId='price'), 없으면 첫번째 축 사용
  const yAxis: any = (yAxisMap as any)["price"] ?? (yAxisMap as any)[yKeys[0]];
  const xScale = xAxis?.scale;
  const yScale = yAxis?.scale;
  if (!xScale || !yScale) return null;
  const band = (xAxis.bandSize ||
    (xScale.bandwidth ? xScale.bandwidth() : 8)) as number;
  const cw = Math.max(3, band * 0.6);
  const dataArr: Candle[] = Array.isArray(chartData) ? chartData : [];
  return (
    <g>
      {dataArr.map((d: Candle, idx: number) => {
        const xv = xScale(d.date);
        if (xv == null) return null;
        const x = (xv as number) + band / 2;
        const yOpen = yScale(d.open) as number;
        const yClose = yScale(d.close) as number;
        const yHigh = yScale(d.high) as number;
        const yLow = yScale(d.low) as number;
        const top = Math.min(yOpen, yClose);
        const bottom = Math.max(yOpen, yClose);
        const color = d.close >= d.open ? upColor : downColor;
        return (
          <g key={idx}>
            <line
              x1={x}
              x2={x}
              y1={yHigh}
              y2={yLow}
              stroke={color}
              strokeWidth={1.4}
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
}

type Props = {
  data: Candle[];
  height?: number;
  showMA?: boolean;
  upColor?: string;
  downColor?: string;
  showGrid?: boolean;
};

export default function CandlePriceChart({
  data,
  height = 360,
  showMA = true,
  upColor = "#ef4444",
  downColor = "#3b82f6",
  showGrid = true,
}: Props) {
  const priceMin = data.length
    ? Math.min(...data.map((d) => Math.min(d.open, d.high, d.low, d.close)))
    : 0;
  const priceMax = data.length
    ? Math.max(...data.map((d) => Math.max(d.open, d.high, d.low, d.close)))
    : 1;

  // -- end CandleLayerComp --

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 10, right: 20, bottom: 10, left: 0 }}
        >
          {showGrid && <CartesianGrid stroke="#334155" vertical={false} />}
          <XAxis
            dataKey="date"
            stroke="#cbd5e1"
            tick={{ fontSize: 12 }}
            interval={Math.max(0, Math.floor(data.length / 10))}
          />
          <YAxis
            yAxisId="price"
            stroke="#cbd5e1"
            domain={[priceMin * 0.98, priceMax * 1.02]}
          />
          <Tooltip
            content={({ active, payload, label }: any) => {
              if (active && payload && payload.length) {
                const d = payload[0].payload as Candle;
                return (
                  <div className="bg-slate-800 text-white p-3 rounded-lg border border-slate-600">
                    <div>{label}</div>
                    <div>시가: {d.open.toLocaleString()}</div>
                    <div>고가: {d.high.toLocaleString()}</div>
                    <div>저가: {d.low.toLocaleString()}</div>
                    <div>종가: {d.close.toLocaleString()}</div>
                  </div>
                );
              }
              return null;
            }}
          />
          {/* 보조: 축 도메인 안정화를 위한 투명 라인 */}
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="close"
            stroke="transparent"
            dot={false}
            isAnimationActive={false}
          />
          {/* 이동평균선 */}
          {showMA && (
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="ma5"
              stroke="#22c55e"
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
          )}
          {showMA && (
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="ma20"
              stroke="#f59e0b"
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
          )}
          {showMA && (
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="ma60"
              stroke="#8b5cf6"
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
          )}
          <Customized
            yAxisId="price"
            component={(p: any) => (
              <CandleLayerComp {...p} upColor={upColor} downColor={downColor} />
            )}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
