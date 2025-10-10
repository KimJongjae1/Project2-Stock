import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import type { ChartOptions } from "chart.js";
import type { ChartLineData } from "../../types/tendency";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

const formatNumber = (n: number) => new Intl.NumberFormat("ko-KR").format(Math.round(n));
const formatCurrency = (n: number) => `${formatNumber(n)}원`;
const formatDiff = (change: number, rate: number) => {
  const positive = change >= 0;
  return `${positive ? "+" : ""}${formatNumber(change)}원 (${positive ? "+" : ""}${rate.toFixed(2)}%)`;
};

type Props = {
  companyName: string;
  ticker?: string;
  currentWeek: string;
  nextWeek: string;
  price: number;
  change: number;
  rate: number;
  chartData: ChartLineData;
  chartOptions?: ChartOptions<'line'>;
  rangeFrom?: string;
};

export default function StockOverview({
  companyName,
  ticker,
  currentWeek,
  nextWeek,
  price,
  change,
  rate,
  chartData,
  chartOptions,
  rangeFrom,
}: Props) {
  const diffText = formatDiff(change, rate);
  const positive = change >= 0;

  // 💡 ChartMain.tsx의 디자인을 적용한 Chart.js options
  const defaultChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgb(30 41 59)', // slate-800
        titleColor: '#cbd5e1', // slate-300
        bodyColor: '#fcd34d', // amber-300
        titleFont: {
          size: 14,
        },
        bodyFont: {
          size: 16,
          weight: 'bold' as 'bold',
        },
        borderColor: 'rgb(71 85 105)', // slate-600
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#cbd5e1', // slate-300
          font: { size: 12 },
        },
        grid: {
          color: 'rgba(203, 213, 225, 0.1)',
          borderColor: '#475569', // slate-600
        },
      },
      y: {
        ticks: {
          color: '#cbd5e1', // slate-300
        },
        grid: {
          color: 'rgba(203, 213, 225, 0.1)',
          borderColor: '#475569',
        },
      },
    },
    elements: {
      point: {
        backgroundColor: '#fbbf24', // amber-400
        borderColor: '#f59e0b', // amber-500
        borderWidth: 2,
        radius: 4,
      },
      line: {
        borderColor: '#fbbf24', // amber-400
        borderWidth: 2,
      },
    },
  };

  return (
    // 💡 배경색과 텍스트 색상을 변경하여 어두운 테마에 맞춤
    <div className="space-y-4 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-700 text-white p-5 shadow-xl border border-slate-600">
      <header className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          {/* 💡 텍스트 색상 변경 */}
          <h2 className="text-2xl font-bold text-white">{companyName}</h2>
          {ticker ? (
            <span className="rounded-full bg-slate-600 px-2 py-0.5 text-xs font-semibold text-slate-300">
              {ticker}
            </span>
          ) : null}
        </div>
        {/* 💡 텍스트 색상 변경 */}
        <div className="mt-1 text-sm text-slate-400">{currentWeek}</div>
      </header>

      <section>
        {/* 💡 텍스트 색상 변경 */}
        <div className="text-3xl font-extrabold text-white">{formatCurrency(price)}</div>
        {/* 이 부분은 기존 로직 유지 */}
        <div className={`mt-1 text-sm font-semibold ${positive ? "text-emerald-400" : "text-rose-400"}`}>
          {diffText}
        </div>
      </section>

      {/* 💡 차트 컨테이너의 배경색과 테두리 색상 변경 */}
      <div className="rounded-xl border border-slate-600 bg-slate-900 p-2">
        <Line
          data={{ labels: chartData.labels, datasets: chartData.datasets as any }}
          options={{ ...defaultChartOptions, ...chartOptions }}
          height={220}
        />
      </div>

      <footer className="flex items-center justify-between text-xs text-slate-400">
        <span>
          {rangeFrom ? `범위: ${rangeFrom} ~ ${currentWeek}` : `현재: ${currentWeek}`}
        </span>
        <span>다음: {nextWeek}</span>
      </footer>
    </div>
  );
}