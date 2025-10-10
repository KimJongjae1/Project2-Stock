import { useEffect, useState } from "react";
import { Navigate } from "react-router";
import { useAuth } from "../stores/auth";
import ProfileCard from "../components/mypage/ProfileCard";
import GameResult from "../components/mypage/GameResult";
import Watchlist from "../components/mypage/Watchlist";
import TradeHistory from "../components/mypage/TradeHistory";
import type { MyPageData } from "../types/MyPageData";
import useAuthGuard from "../hooks/useAuthGuard";
import { api } from "../api/client";

export default function MyPage() {
  const { authed, ready } = useAuthGuard("/");
  const loading = useAuth((s) => s.loading);
  const authUser = useAuth((s) => s.user);

  const [data, setData] = useState<MyPageData | null>(null);
  const [pending, setPending] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready || !authed) return;
    (async () => {
      setPending(true);
      setError(null);
      try {
        const res = await api.get<MyPageData>("/api/mypage/me");
        setData(res);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "불러오기 실패");
      } finally {
        setPending(false);
      }
    })();
  }, [ready, authed]);

  if (loading || pending)
    return (
      <div className="min-h-dvh bg-slate-800 grid place-items-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500 mb-4"></div>
          <div className="text-amber-100 font-medium">
            {loading ? "확인 중…" : "불러오는 중…"}
          </div>
        </div>
      </div>
    );

  if (!authUser) return <Navigate to="/" replace />;

  return (
    <div className="min-h-dvh bg-slate-800">
      <div className="py-8">
        <div className="mx-auto w-full max-w-[1400px] px-4 sm:px-5 space-y-6">
          {error && (
            <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 text-amber-200 px-4 py-2">
              {error}
            </div>
          )}

          {/* 상단 2열 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <ProfileCard />
            <GameResult data={data?.gameResult ?? null} />
          </div>

          {/* 하단 섹션들 */}
          <div className="space-y-6">
            <Watchlist items={data?.favorites ?? []} />
            <TradeHistory
              items={data?.tradeHistory ?? []}
              account={data?.account}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
