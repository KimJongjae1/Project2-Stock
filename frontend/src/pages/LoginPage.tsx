import * as React from 'react';
import { Navigate } from 'react-router';
import { useAuth } from '../stores/auth';
import { url } from '../api/config';

export default function LoginPage() {
  const { user, loading, bootstrap } = useAuth();

  // 새로고침/첫 진입 시 refresh → me 시도
  React.useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  // 이미 로그인된 경우 메인으로 이동
  if (!loading && user) {
    return <Navigate to="/" replace />;
  }

  const loginGoogle = () => {
    window.location.href = url('/api/users/auth/google');
  };

  const loginKakao = () => {
    window.location.href = url('/api/users/auth/kakao');
  };

  return (
    <div className="min-h-dvh flex items-center justify-center bg-slate-800">
      <div className="w-full max-w-md rounded-2xl bg-slate-700 p-8 shadow-2xl border border-slate-600 relative">
        {/* 로고/아이콘 영역 */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-amber-500 to-amber-600 flex items-center justify-center">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" className="text-white">
              <path
                d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">로그인</h1>
          <p className="text-slate-400">계정을 선택해주세요</p>
        </div>

        <div className="space-y-4">
          <button
            onClick={loginGoogle}
            disabled={loading}
            className="w-full rounded-lg bg-white px-4 py-3 text-gray-900 font-medium hover:bg-gray-50 disabled:opacity-60 transition-all flex items-center justify-center gap-3 border border-gray-200"
          >
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Google로 로그인
          </button>

          <button
            onClick={loginKakao}
            disabled={loading}
            className="w-full rounded-lg bg-yellow-400 px-4 py-3 text-gray-900 font-medium hover:bg-yellow-300 disabled:opacity-60 transition-all flex items-center justify-center gap-3"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 3c5.799 0 10.5 3.664 10.5 8.185 0 4.52-4.701 8.184-10.5 8.184a13.5 13.5 0 0 1-1.727-.11l-4.408 2.883c-.501.265-.678.236-.472-.413l.892-3.678c-2.88-1.46-4.785-3.99-4.785-6.866C1.5 6.665 6.201 3 12 3Z" />
            </svg>
            Kakao로 로그인
          </button>
        </div>

        {/* 로딩 상태 */}
        {loading && (
          <div className="mt-4 flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-amber-500"></div>
            <span className="ml-2 text-slate-400 text-sm">로그인 확인 중...</span>
          </div>
        )}
      </div>
    </div>
  );
}
