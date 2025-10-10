import * as React from "react";
import { useAuth } from "../../stores/auth";
import NicknameDialog from "./NicknameDialog";
import { api } from "../../api/client";

function getInitials(name: string) {
  const trimmed = (name || "").trim();
  if (!trimmed) return "?";
  const parts = trimmed.split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return trimmed.slice(0, 2).toUpperCase();
}

export default function ProfileCard() {
  const user = useAuth((s) => s.user);
  const setUser = useAuth((s) => s.setUser);
  const logout = useAuth((s) => s.logout);

  const [openNick, setOpenNick] = React.useState(false);

  const onSavedNickname = (newNickname: string) => {
    if (!user) return;
    setUser({ ...user, nickname: newNickname });
  };

  const onDeleteAccount = async () => {
    const ok = window.confirm(
      "정말로 회원탈퇴 하시겠어요? 이 작업은 되돌릴 수 없습니다."
    );
    if (!ok) return;
    try {
      await api.del<void>("/api/users/me");
    } finally {
      await logout();
    }
  };

  if (!user) return null;

  return (
    <section
      className="w-full bg-slate-700 backdrop-blur-xl rounded-2xl shadow-lg border border-slate-600 p-6 relative overflow-visible
                 flex items-center justify-center min-h-[28rem]"
    >
      {/* 중앙 컨텐츠 */}
      <div className="w-full">
        {/* 아바타 */}
        <div className="flex justify-center">
          {user.avatarUrl ? (
            <img
              src={user.avatarUrl}
              alt="프로필"
              className="w-24 h-24 rounded-full object-cover shadow-lg ring-4 ring-amber-500/30"
              referrerPolicy="no-referrer"
            />
          ) : (
            <div className="w-24 h-24 rounded-full bg-gradient-to-r from-amber-500 to-amber-600 text-white flex items-center justify-center font-extrabold text-3xl shadow-lg ring-4 ring-amber-400/30 select-none">
              {getInitials(user.nickname)}
            </div>
          )}
        </div>

        {/* 닉네임 + 변경 */}
        <div className="mt-5 flex items-center justify-center gap-2 flex-wrap">
          <h2 className="text-2xl font-extrabold text-white tracking-tight">
            {user.nickname}
          </h2>
          <button
            onClick={() => setOpenNick(true)}
            className="inline-flex items-center gap-1 px-2 py-1 rounded-md border border-slate-500 bg-slate-600 text-sm text-slate-200 hover:bg-slate-500 hover:border-amber-400 transition-all"
            title="닉네임 변경"
            aria-label="닉네임 변경"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              aria-hidden
            >
              <path
                d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25Z"
                stroke="currentColor"
                strokeWidth="1.5"
              />
              <path
                d="M14.06 6.19l3.75 3.75L20.5 7.25l-3.75-3.75-2.69 2.69Z"
                stroke="currentColor"
                strokeWidth="1.5"
              />
            </svg>
            <span>변경</span>
          </button>
        </div>

        {/* 가입일 */}
        <p className="mt-1 text-center text-slate-400 text-sm">
          • 가입일: {new Date(user.createdAt).toLocaleDateString()}
        </p>
      </div>

      {/* 우측 하단 고정: 회원탈퇴 */}
      <div className="absolute bottom-6 right-6">
        <button
          onClick={onDeleteAccount}
          className="px-4 py-2 rounded-lg bg-red-600/80 text-white hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400/50 transition-all"
        >
          회원탈퇴
        </button>
      </div>

      {/* 닉네임 모달 */}
      <NicknameDialog
        open={openNick}
        initialNickname={user.nickname}
        onClose={() => setOpenNick(false)}
        onSaved={onSavedNickname}
      />
    </section>
  );
}
