import { useAuth } from '../stores/auth';
import { getAccessToken, setAccessToken } from './tokenCache';
import { url } from './config';

// 서버 엔드포인트
const REFRESH_PATH = '/api/users/auth/refresh';
const LOGOUT_PATH = '/api/users/logout';

// 공통 응답 처리: 204/빈 바디 안전 처리 (any 없이)
async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const msg = await res.text().catch(() => '');
    console.error(`[API ${res.status}] ${res.url} -> ${msg}`);
    throw new Error(msg || String(res.status));
  }

  // 204 또는 빈 응답 처리
  const isNoContent = res.status === 204 || res.headers.get('content-length') === '0';
  if (isNoContent) {
    // T가 void/undefined일 때만 의미가 있지만, 호출부 제네릭으로 통제
    return undefined as unknown as T;
  }

  // JSON 응답으로 가정(서버가 JSON만 내려준다는 계약)
  return (await res.json()) as T;
}

// Authorization 헤더 빌드 (refresh엔 금지)
function buildHeaders(path: string): HeadersInit {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const isRefresh = path.startsWith(REFRESH_PATH);
  const t = getAccessToken();
  if (t && !isRefresh) headers.Authorization = `Bearer ${t}`;
  return headers;
}

// 동시 401 폭주 방지
let inflightRefresh: Promise<boolean> | null = null;

async function refreshOnce(): Promise<boolean> {
  if (!inflightRefresh) {
    inflightRefresh = (async () => {
      try {
        const res = await fetch(url(REFRESH_PATH), {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!res.ok) {
          setAccessToken(null);
          useAuth.getState().setUser(null);
          return false;
        }

        type RefreshResp = { accessToken?: string };
        const data = (await res.json()) as RefreshResp;

        if (data.accessToken) {
          setAccessToken(data.accessToken);
          return true;
        }

        setAccessToken(null);
        useAuth.getState().setUser(null);
        return false;
      } catch {
        setAccessToken(null);
        useAuth.getState().setUser(null);
        return false;
      } finally {
        setTimeout(() => {
          inflightRefresh = null;
        }, 0);
      }
    })();
  }
  return inflightRefresh;
}

// 요청 래퍼
async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const fullUrl = url(path);
  const res = await fetch(fullUrl, {
    credentials: 'include',
    ...init,
    headers: { ...buildHeaders(path), ...(init.headers ?? {}) },
  });

  if (res.status === 401 && retry && !path.startsWith(REFRESH_PATH)) {
    const ok = await refreshOnce();
    if (ok) {
      const res2 = await fetch(fullUrl, {
        credentials: 'include',
        ...init,
        headers: { ...buildHeaders(path), ...(init.headers ?? {}) },
      });
      return handle<T>(res2);
    }
  }
  return handle<T>(res);
}

// 공개 API
export const api = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body != null ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PUT', body: body != null ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PATCH', body: body != null ? JSON.stringify(body) : undefined }),
  del: <T>(path: string) => request<T>(path, { method: 'DELETE' }),

  // 로그아웃(반환값 없음)
  logout: async (): Promise<void> => {
    try {
      await fetch(url(LOGOUT_PATH), {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      });
    } finally {
      setAccessToken(null);
      useAuth.getState().setUser(null);
    }
  },
};
