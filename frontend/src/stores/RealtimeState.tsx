import { create } from 'zustand';
import type { WebSocketRealtime } from '../types/StockRealtime';

interface RealtimeState {
  data: Record<string, WebSocketRealtime>;
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
}

export const useRealtimeStore = create<RealtimeState>((set) => {
  let ws: WebSocket | null = null;

  const connect = () => {
    if (ws) return; // 이미 연결되어 있으면 무시
    ws = new WebSocket(
      import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8765'
    );

    ws.onopen = () => {
      console.log('✅ WS 연결 성공');
      set({ isConnected: true });
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketRealtime[] = JSON.parse(event.data);
        set((state) => {
          const newData = { ...state.data };
          data.forEach((d) => {
            newData[d.ticker] = d;
          });
          return { data: newData };
        });
      } catch (err) {
        console.error('❌ WS 데이터 파싱 오류:', err, event.data);
      }
    };

    ws.onclose = () => {
      console.log('❌ WS 연결 종료');
      set({ isConnected: false });
      ws = null;
    };

    ws.onerror = (err) => {
      console.error('❌ WS 에러', err);
      ws?.close();
      ws = null;
      set({ isConnected: false });
    };
  };

  const disconnect = () => {
    ws?.close();
    ws = null;
    set({ isConnected: false });
  };

  return {
    data: {},
    isConnected: false,
    connect,
    disconnect,
  };
});
