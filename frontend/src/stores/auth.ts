import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User } from '../types/user';
import { url } from '../api/config';
import { getAccessToken, setAccessToken } from '../api/tokenCache';

type State = {
  user: User | null;
  loading: boolean;
};

type Actions = {
  setUser: (u: User | null) => void;
  bootstrap: () => Promise<void>;
  logout: () => Promise<void>;
};

let __booting = false;

export const useAuth = create<State & Actions>()(
  persist(
    (set) => ({
      user: null,
      loading: false,

      setUser: (u) => set({ user: u }),

      bootstrap: async () => {
        if (__booting) return;
        __booting = true;
        set({ loading: true });
        try {
          // 1) refresh로 accessToken 확보(메모리)
          const res = await fetch(url('/api/users/auth/refresh'), {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          });

          if (res.ok) {
            type RefreshResp = { accessToken?: string };
            const data = (await res.json()) as RefreshResp;
            if (data.accessToken) setAccessToken(data.accessToken);
            else setAccessToken(null);
          } else {
            setAccessToken(null);
            set({ user: null });
          }

          // 2) 토큰 있으면 me 조회
          const token = getAccessToken();
          if (token) {
            const meRes = await fetch(url('/api/users/login-user'), {
              method: 'GET',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
              },
            });
            if (meRes.ok) {
              const me = (await meRes.json()) as User;
              set({ user: me });
            } else {
              setAccessToken(null);
              set({ user: null });
            }
          }
        } finally {
          set({ loading: false });
          __booting = false;
        }
      },

      logout: async () => {
        set({ loading: true });
        try {
          await fetch(url('/api/users/logout'), {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
          });
        } catch {
          // ignore
        } finally {
          setAccessToken(null);
          set({ user: null, loading: false });
        }
      },
    }),
    {
      name: 'auth-store',
      storage: createJSONStorage(() => sessionStorage),
      // user만 저장 (토큰은 메모리)
      partialize: (s) => ({ user: s.user }),
    },
  ),
);

//탭 간 user 동기화
if (typeof window !== 'undefined') {
  window.addEventListener('storage', (e: StorageEvent) => {
    if (e.key === 'auth-store') {
      const raw = e.newValue;
      if (!raw) {
        useAuth.getState().setUser(null);
        return;
      }
      try {
        const parsed = JSON.parse(raw) as { state?: { user?: User | null } };
        if (parsed.state && 'user' in parsed.state) {
          useAuth.getState().setUser(parsed.state.user ?? null);
        }
      } catch {
        // ignore JSON parse errors
      }
    }
  });
}
