const formatNumber = (n: number) => new Intl.NumberFormat('ko-KR').format(Math.max(0, Math.round(n)));
const formatCurrency = (n: number) => `${formatNumber(n)}원`;
const formatPercent = (n: number) => {
    const value = Number.isFinite(n) ? n : 0;
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
};

type TradePanelProps = {
    stockCount: number;
    totalValue: number;
    averageCost: number;
    evaluationProfit: number;
    evaluationRate: number;
    tradeAmount: number;
    onTradeAmountChange(n: number): void;
    onBuy(): void;
    onSell(): void;
    onNextWeek(): void;
    onEndGame(): void;
    term: string;
    onTermChange(term: string): void;
    maxAffordable: number;
    maxSellable: number;
    currentWeek?: number;
    maxWeek?: number;
};

export default function TradePanel({
    stockCount,
    totalValue,
    averageCost,
    evaluationProfit,
    evaluationRate,
    tradeAmount,
    onTradeAmountChange,
    onBuy,
    onSell,
    onNextWeek,
    onEndGame,
    term,
    onTermChange,
    maxAffordable,
    maxSellable,
    currentWeek = 1,
    maxWeek = 10,
}: TradePanelProps) {
    const infoItems = [
        { label: '보유 주식', value: `${formatNumber(stockCount)}주` },
        { label: '평가 금액', value: formatCurrency(totalValue) },
        { label: '평균 단가', value: formatCurrency(averageCost) },
        {
            label: '평가 손익',
            value: formatCurrency(evaluationProfit),
            helper: formatPercent(evaluationRate),
            tone: evaluationProfit >= 0 ? 'text-emerald-400' : 'text-rose-400',
        },
    ];

    const canBuy = tradeAmount > 0 && tradeAmount <= Math.max(0, Math.floor(maxAffordable));
    const canSell = tradeAmount > 0 && tradeAmount <= Math.max(0, Math.floor(maxSellable));
    
    // 주차에 따른 버튼 활성화 조건
    const canGoToNextWeek = currentWeek < maxWeek; // 10주가 되기 전까지는 '다음주로' 활성화
    const canEndGame = currentWeek >= maxWeek; // 10주차가 되면 종료 버튼 활성화

    const quickSet = (amount: number) => {
        onTradeAmountChange(Math.max(0, Math.floor(amount)));
    };

    return (
        <aside className="space-y-4">
            {/* 💡 배경 및 폰트 색상 변경 */}
            <section className="space-y-4 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-700 p-5 shadow-xl border border-slate-600">
                <div className="grid grid-cols-2 gap-3 text-sm">
                    {infoItems.map((item) => (
                        <div key={item.label}>
                            <p className="text-xs text-slate-400">{item.label}</p>
                            <p className="mt-1 font-semibold text-white">{item.value}</p>
                            {item.helper ? (
                                <p className={`text-xs font-semibold ${item.tone ?? 'text-slate-400'}`}>{item.helper}</p>
                            ) : null}
                        </div>
                    ))}
                </div>

                <div className="flex items-center justify-between">
                    <label className="text-sm text-slate-400">투자 금액</label>
                </div>

                <div className="flex items-end gap-3">
                    <div className="flex-1">
                        <label className="mb-1 block text-sm text-slate-400">수량</label>
                        <input
                            type="number"
                            min={0}
                            className="w-full rounded-lg border border-slate-600 px-3 py-2 bg-slate-900 text-white"
                            value={tradeAmount}
                            onChange={(e) => quickSet(Number(e.target.value) || 0)}
                        />
                    </div>
                    <div className="flex flex-col gap-2 text-xs">
                        {[1, 5, 10].map((preset) => (
                            <button
                                key={preset}
                                type="button"
                                onClick={() => quickSet(preset)}
                                className="rounded-lg border border-slate-600 px-3 py-2 text-slate-300 hover:bg-slate-700"
                            >
                                {preset}주
                            </button>
                        ))}
                        <button
                            type="button"
                            onClick={() => quickSet(maxAffordable)}
                            className="rounded-lg border border-slate-600 px-3 py-2 text-slate-300 hover:bg-slate-700"
                        >
                            전액 매수
                        </button>
                        <button
                            type="button"
                            onClick={() => quickSet(maxSellable)}
                            className="rounded-lg border border-slate-600 px-3 py-2 text-slate-300 hover:bg-slate-700"
                        >
                            전량 매도
                        </button>
                    </div>
                </div>

                <div className="flex gap-2">
                    <button
                        type="button"
                        onClick={onBuy}
                        disabled={!canBuy}
                        className="flex-1 rounded-lg bg-emerald-500 px-4 py-2 font-semibold text-white transition hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                        매수
                    </button>
                    <button
                        type="button"
                        onClick={onSell}
                        disabled={!canSell}
                        className="flex-1 rounded-lg bg-rose-500 px-4 py-2 font-semibold text-white transition hover:bg-rose-600 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                        매도
                    </button>
                </div>

                <div className="flex gap-2">
                    <button
                        type="button"
                        onClick={onNextWeek}
                        disabled={!canGoToNextWeek}
                        className={`flex-1 rounded-lg border border-slate-600 px-4 py-2 font-semibold text-white transition hover:bg-slate-700 ${
                            canGoToNextWeek 
                                ? 'bg-yellow-500 hover:bg-yellow-600' 
                                : 'bg-gray-500 cursor-not-allowed opacity-50'
                        }`}
                    >
                        {canGoToNextWeek ? '다음 주로' : '최대 주차'}
                    </button>
                    <button
                        type="button"
                        onClick={onEndGame}
                        disabled={!canEndGame}
                        className={`flex-1 rounded-lg border border-indigo-400 px-4 py-2 font-semibold text-white transition hover:bg-indigo-900 ${
                            canEndGame 
                                ? 'bg-indigo-500 hover:bg-indigo-600' 
                                : 'bg-gray-500 cursor-not-allowed opacity-50'
                        }`}
                    >
                        종료
                    </button>
                </div>
            </section>
        </aside>
    );
}