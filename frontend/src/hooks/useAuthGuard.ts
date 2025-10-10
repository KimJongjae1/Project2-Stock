import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '../stores/auth';
import { getAccessToken, subscribe } from '../api/tokenCache';

export default function useAuthGuard(redirectTo: string = '/') {
  const nav = useNavigate();
  const { loading, bootstrap } = useAuth();

  // 토큰을 state로 관리해 변경에 반응
  const [token, setToken] = useState<string | null>(() => getAccessToken());

  useEffect(() => {
    const off = subscribe(setToken); // 반드시 () => void 반환
    return off;
  }, []);

  // 앱 부트스트랩(쿠키→refresh→me)
  useEffect(() => {
    if (loading) void bootstrap();
  }, [loading, bootstrap]);

  const ready = !loading;

  // 가드: 로딩 끝났고 토큰 없으면 리다이렉트
  useEffect(() => {
    if (ready && !token) {
      nav(redirectTo, { replace: true });
    }
  }, [ready, token, nav, redirectTo]);

  return { authed: !!token, ready };
}
