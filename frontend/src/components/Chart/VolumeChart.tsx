import { ResponsiveContainer, ComposedChart, XAxis, YAxis, Tooltip, CartesianGrid, Bar, Brush, Cell } from 'recharts';

type Candle = { date: string; open: number; close: number; volume: number };

export default function VolumeChart({ data, onRangeChange, height = 160 }: { data: Candle[]; onRangeChange?: (r: {startIndex:number; endIndex:number} | null)=>void; height?: number }) {
  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 4, right: 20, bottom: 10, left: 0 }}>
          <CartesianGrid stroke="#334155" vertical={false} />
          <XAxis dataKey="date" stroke="#cbd5e1" tick={{ fontSize: 12 }} interval={Math.max(0, Math.floor(data.length / 10))} />
          <YAxis orientation="right" stroke="#94a3b8" allowDecimals={false} tickFormatter={(v) => (v as number).toLocaleString()} />
          <Tooltip content={({ active, payload, label }: any) => {
            if (active && payload && payload.length) {
              const d = payload[0].payload as Candle;
              return (
                <div className="bg-slate-800 text-white p-2 rounded-lg border border-slate-600">
                  <div>{label}</div>
                  <div>거래량: {d.volume.toLocaleString()}</div>
                </div>
              );
            }
            return null;
          }} />
          <Bar dataKey="volume" opacity={0.7} barSize={5}>
            {data.map((d, i) => (
              <Cell key={`v-${i}`} fill={d.close >= d.open ? '#ef4444' : '#3b82f6'} />
            ))}
          </Bar>
          <Brush dataKey="date" height={28} travellerWidth={10} stroke="#94a3b8" fill="#0f172a" tickFormatter={(d:any)=>String(d)}
                 onChange={(x:any)=> onRangeChange?.(x?.startIndex!=null && x?.endIndex!=null ? {startIndex:x.startIndex, endIndex:x.endIndex} : null)} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

