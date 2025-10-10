import { useState, type ChangeEvent } from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../stores/auth";
import LoginRequiredModal from "../components/TendencyGame/LoginRequiredModal";
import logoImg from "../assets/logo.webp";

function getInitials(name: string) {
  const t = (name || "").trim();
  if (!t) return "?";
  const parts = t.split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return t.slice(0, 2).toUpperCase();
}

export default function Header() {
  const [search, setSearch] = useState("");
  const [openAll, setOpenAll] = useState(false); // xs: 전체 패널
  const [openNav, setOpenNav] = useState(false); // sm~lg: 세 친구 패널
  const [loginRequiredModal, setLoginRequiredModal] = useState(false);
  const navigate = useNavigate();

  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);

  //로그아웃 확인 후 실행
  const confirmLogout = async () => {
    const ok = window.confirm("로그아웃하시겠습니까?");
    if (ok) {
      await logout();
      setOpenAll(false);
      setOpenNav(false);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) =>
    setSearch(e.target.value);

  const handleSearch = () => {
    const trimmed = search.trim();
    if (!trimmed) {
      navigate("/");
    } else {
      navigate(`/search?query=${encodeURIComponent(trimmed)}`);
    }
    setOpenAll(false);
    setOpenNav(false);
  };

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") handleSearch();
  };

  const goLogin = () => {
    navigate("/login");
    setOpenAll(false);
    setOpenNav(false);
  };
  const goMy = () => {
    navigate("/mypage");
    setOpenAll(false);
    setOpenNav(false);
  };

  const handleGoHome = () => {
    navigate("/");
  };

  const handleCloseLoginModal = () => {
    setLoginRequiredModal(false);
  };

  const handleTradeClick = (e: React.MouseEvent) => {
    if (!user) {
      e.preventDefault();
      setLoginRequiredModal(true);
      // 2초 후 홈으로 이동
      setTimeout(() => {
        navigate("/");
      }, 2000);
      return;
    }
    setOpenAll(false);
    setOpenNav(false);
  };

  const NavLinks = ({ onClick }: { onClick: () => void }) => (
    <>
      <Link
        to="/game"
        className="px-2 py-2 text-slate-300 hover:text-white font-bold flex-none shrink-0 whitespace-nowrap"
        onClick={onClick}
      >
        투자 성향 파악 게임
      </Link>
      <Link
        to="/trade"
        className="px-2 py-2 text-slate-300 hover:text-white font-bold flex-none shrink-0 whitespace-nowrap"
        onClick={handleTradeClick}
      >
        모의 투자
      </Link>
      <Link
        to="/influence"
        className="px-2 py-2 text-slate-300 hover:text-white font-bold flex-none shrink-0 whitespace-nowrap"
        onClick={onClick}
      >
        기업 영향력
      </Link>
    </>
  );

  const AuthArea = () =>
    !user ? (
      <button
        onClick={goLogin}
        className="flex-none shrink-0 h-10 px-4 border border-slate-600 text-slate-300 rounded-xl hover:border-slate-500 hover:text-white font-bold whitespace-nowrap"
      >
        로그인
      </button>
    ) : (
      <div className="flex items-center gap-3">
        {user.avatarUrl ? (
          <img
            onClick={goMy}
            src={user.avatarUrl}
            alt="프로필"
            className="h-10 w-10 rounded-full object-cover border border-slate-600 cursor-pointer flex-none shrink-0"
            referrerPolicy="no-referrer"
          />
        ) : (
          <div
            onClick={goMy}
            className="h-10 w-10 rounded-full bg-amber-500/90 text-slate-900 flex items-center justify-center font-extrabold cursor-pointer flex-none shrink-0"
            title="마이페이지"
          >
            {getInitials(user.nickname)}
          </div>
        )}
        <button
          onClick={confirmLogout}
          className="flex-none shrink-0 h-10 px-3 text-sm rounded-lg border border-slate-600 hover:bg-slate-700/60 whitespace-nowrap"
        >
          로그아웃
        </button>
      </div>
    );

  return (
    <header className="bg-slate-800 text-white">
      {/* Top bar */}
      <nav className="relative mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-3">
        {/* 좌측: 로고 + 네비게이션(반응형) */}
        <div className="relative flex items-center gap-3 min-w-0">
          <Link
            to="/"
            onClick={() => {
              setOpenAll(false);
              setOpenNav(false);
            }}
          >
            <img src={logoImg} alt="로고이미지" className="h-8 w-auto" />
          </Link>

          <div className="hidden lg:flex items-center gap-4 min-w-0 flex-nowrap">
            <NavLinks onClick={() => {}} />
          </div>

          <div className="hidden sm:block lg:hidden">
            <button
              onClick={() => setOpenNav((v) => !v)}
              className="inline-flex items-center gap-2 rounded-lg px-3 py-2 hover:bg-slate-700/50"
              aria-label="메뉴"
            >
              <svg
                width="22"
                height="22"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                {openNav ? (
                  <path d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path d="M3 6h18M3 12h18M3 18h18" />
                )}
              </svg>
              <span className="text-sm text-slate-300">메뉴</span>
            </button>

            <div
              className={`absolute z-40 mt-2 left-0 w-60 overflow-hidden rounded-xl bg-slate-900/95 ring-1 ring-white/10 shadow-xl transition-[max-height,opacity] duration-300 ${
                openNav
                  ? "max-h-80 opacity-100"
                  : "max-h-0 opacity-0 pointer-events-none"
              }`}
            >
              <div className="flex flex-col px-3 py-2">
                <NavLinks onClick={() => setOpenNav(false)} />
              </div>
            </div>
          </div>
        </div>

        <div className="hidden sm:flex items-center gap-3 min-w-0 flex-nowrap">
          <input
            className="min-w-[9rem] md:min-w-[14rem] w-[14rem] md:w-[18rem] flex-auto px-4 h-10 bg-slate-700 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
            placeholder="기업명 또는 종목코드로 검색"
            value={search}
            onChange={handleChange}
            onKeyDown={handleKey}
          />
          <button
            onClick={handleSearch}
            className="flex-none shrink-0 h-10 px-4 md:px-5 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 rounded-xl hover:from-amber-600 hover:to-amber-700 font-bold whitespace-nowrap"
          >
            검색
          </button>
          <AuthArea />
        </div>

        <button
          aria-label="전체 메뉴"
          className="sm:hidden inline-flex items-center justify-center rounded-lg p-2 hover:bg-slate-700/50"
          onClick={() => setOpenAll((v) => !v)}
        >
          <svg
            width="24"
            height="24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            {openAll ? (
              <path d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path d="M3 6h18M3 12h18M3 18h18" />
            )}
          </svg>
        </button>
      </nav>

      <div
        className={`sm:hidden overflow-hidden transition-[max-height] duration-300 ${
          openAll ? "max-h-[520px]" : "max-h-0"
        }`}
      >
        <div className="px-4 pb-4 space-y-4">
          <div className="flex flex-col gap-1">
            <NavLinks onClick={() => setOpenAll(false)} />
          </div>
          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                className="flex-1 px-4 h-10 bg-slate-700 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                placeholder="기업명 또는 종목코드로 검색"
                value={search}
                onChange={handleChange}
                onKeyDown={handleKey}
              />
              <button
                onClick={handleSearch}
                className="flex-none h-10 px-4 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 rounded-xl hover:from-amber-600 hover:to-amber-700 font-bold"
              >
                검색
              </button>
            </div>
            <AuthArea />
          </div>
        </div>
      </div>

      <LoginRequiredModal
        isOpen={loginRequiredModal}
        onClose={handleCloseLoginModal}
        onGoHome={handleGoHome}
      />
    </header>
  );
}
