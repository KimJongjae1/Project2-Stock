import { useEffect, useRef } from 'react';

export type CanvasCandlePoint = {
  date: string; // ISO yyyy-mm-dd
  open: number;
  high: number;
  low: number;
  close: number;
};

type Props = {
  data: CanvasCandlePoint[];
  height?: number;
  upColor?: string;
  downColor?: string;
};

export default function CanvasCandle({ data, height = 360, upColor = '#ff3b30', downColor = '#2f80ed' }: Props) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const wrap = wrapRef.current!;
    const canvas = canvasRef.current!;
    if (!wrap || !canvas) return;

    const dpr = window.devicePixelRatio || 1;
    const padding = { top: 10, right: 50, bottom: 20, left: 50 };

    const draw = () => {
      const width = wrap.clientWidth || 600;
      const cWidth = width * dpr;
      const cHeight = height * dpr;
      canvas.width = cWidth;
      canvas.height = cHeight;
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      // bg
      ctx.clearRect(0, 0, width, height);

      const plotW = width - padding.left - padding.right;
      const plotH = height - padding.top - padding.bottom;
      const x0 = padding.left; const y0 = padding.top;

      if (!data || data.length === 0) return;

      const hi = Math.max(...data.map(d => d.high));
      const lo = Math.min(...data.map(d => d.low));
      const yScale = (v: number) => y0 + (hi - v) / (hi - lo) * plotH;

      const step = plotW / data.length;
      const bodyW = Math.max(3, step * 0.6);

      // grid horizontal
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 1;
      const ticks = 6;
      for (let i = 0; i <= ticks; i++) {
        const y = y0 + (plotH / ticks) * i + 0.5;
        ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x0 + plotW, y); ctx.stroke();
      }

      // candles
      data.forEach((d, i) => {
        const x = x0 + step * i + step / 2;
        const yOpen = yScale(d.open);
        const yClose = yScale(d.close);
        const yHigh = yScale(d.high);
        const yLow = yScale(d.low);
        const top = Math.min(yOpen, yClose);
        const bottom = Math.max(yOpen, yClose);
        const color = d.close >= d.open ? upColor : downColor;
        // wick
        ctx.strokeStyle = color; ctx.lineWidth = 1.2;
        ctx.beginPath(); ctx.moveTo(x, yHigh); ctx.lineTo(x, yLow); ctx.stroke();
        // body
        ctx.fillStyle = color;
        const h = Math.max(1, bottom - top);
        ctx.fillRect(x - bodyW / 2, top, bodyW, h);
      });

      // axes (left price)
      ctx.fillStyle = '#cbd5e1'; ctx.font = '12px sans-serif'; ctx.textAlign = 'right';
      for (let i = 0; i <= ticks; i++) {
        const v = lo + (hi - lo) * (1 - i / ticks);
        const y = y0 + (plotH / ticks) * i + 4;
        ctx.fillText(v.toLocaleString(), x0 - 8, y);
      }
    };

    draw();

    const ro = new ResizeObserver(draw);
    ro.observe(wrap);
    return () => ro.disconnect();
  }, [data, height, upColor, downColor]);

  return (
    <div ref={wrapRef} style={{ width: '100%', height }}>
      <canvas ref={canvasRef} />
    </div>
  );
}

