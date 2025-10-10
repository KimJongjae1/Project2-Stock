export type AppRuntimeConfig = {
  API_BASE_URL?: string;
};

// 전역 window에 타입 선언
declare global {
  interface Window {
    __APP_CONFIG__?: AppRuntimeConfig;
  }
}

export const API_BASE: string =
  (typeof window !== 'undefined' ? window.__APP_CONFIG__?.API_BASE_URL : undefined) ??
  import.meta.env.VITE_API_BASE_URL ??
  'http://localhost:8080';

// URL 구성 헬퍼 함수 - 중복 슬래시 및 경로 문제 해결
export const url = (path: string): string => {
  // 절대 URL인 경우 그대로 반환
  if (path.startsWith('http')) return path;
  
  // API_BASE가 이미 슬래시로 끝나는지 확인
  const base = API_BASE.endsWith('/') ? API_BASE.slice(0, -1) : API_BASE;
  
  // path가 슬래시로 시작하는지 확인하고 적절히 구성
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  
  return `${base}${normalizedPath}`;
};
