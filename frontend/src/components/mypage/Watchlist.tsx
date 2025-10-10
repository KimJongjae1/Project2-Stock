import { Link } from 'react-router';

type FavoriteItem = { itemId: number; name: string; ticker: string };

export default function Watchlist({ items = [] }: { items?: FavoriteItem[] }) {
  const empty = !items || items.length === 0;

  return (
    <section className="w-full bg-slate-700 backdrop-blur-xl rounded-2xl shadow-lg p-6 border border-slate-600 relative">
      <div className="flex items-center gap-2 mb-5">
        <div className="text-amber-400">⭐</div>
        <h3 className="text-xl sm:text-2xl font-extrabold text-white">관심 종목</h3>
      </div>

      {empty ? (
        <div className="text-center py-8">
          <div className="text-slate-400 mb-4">관심 종목이 없습니다.</div>
        </div>
      ) : (
        // 1열 → sm:2열 → lg:3열 → xl:4열
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {items.map((it) => (
            <Link
              to={`/stock/${it.ticker}`}
              key={it.itemId}
              className="px-4 py-5 rounded-2xl bg-slate-600 border border-slate-500 shadow-lg text-left hover:bg-slate-500 hover:border-amber-400 transition-all hover:shadow-xl"
              title={it.name}
            >
              <div className="text-white font-bold truncate">{it.name}</div>
              <div className="text-slate-400 text-sm mt-1">{it.ticker}</div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
