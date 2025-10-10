export type TokenListener = (token: string | null) => void;

let accessToken: string | null = null;
const listeners = new Set<TokenListener>();

export function setAccessToken(token: string | null) {
  if (accessToken === token) return;
  accessToken = token;
  // 변경 알림
  for (const l of listeners) {
    try {
      l(accessToken);
    } catch {
      // ignore
    }
  }
}

export function getAccessToken() {
  return accessToken;
}

/** 토큰 변경 구독. 반환된 함수를 호출하면 구독 해제됩니다. */
export function subscribe(listener: TokenListener): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}
