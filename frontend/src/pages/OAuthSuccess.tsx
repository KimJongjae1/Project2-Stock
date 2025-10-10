import { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router';
import { useAuth } from '../stores/auth';

const GUARD_KEY = 'oauth_refresh_guard_ts';

export default function OAuthSuccess() {
  const nav = useNavigate();
  const [sp] = useSearchParams();
  const ran = useRef(false);
  const { bootstrap } = useAuth();

  useEffect(() => {
    if (ran.current) return;
    ran.current = true;

    // 중복 진입/빠른 더블 클릭 가드 (옵션)
    const now = Date.now();
    const last = Number(sessionStorage.getItem(GUARD_KEY) || '0');
    if (now - last < 8000) return;
    sessionStorage.setItem(GUARD_KEY, String(now));

    (async () => {
      try {
        // bootstrap()이 refresh → accessToken → me 조회까지 수행
        await bootstrap();

        // 성공 시 리다이렉트 목적지 (없으면 '/')
        const redirect = sp.get('redirect') || '/';
        nav(redirect, { replace: true });
      } catch {
        nav('/oauth/fail?reason=refresh_failed', { replace: true });
      }
    })();
  }, [bootstrap, nav, sp]);

  return <div className="min-h-dvh grid place-items-center text-gray-600">로그인 처리중…</div>;
}
