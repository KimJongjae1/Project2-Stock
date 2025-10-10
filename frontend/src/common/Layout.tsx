// src/components/Layout.tsx
import { Outlet } from 'react-router';
import { useEffect } from 'react';
import { useAuth } from '../stores/auth';
import Footer from './Footer';
import Header from './Header';

export default function Layout() {
  const bootstrap = useAuth((s) => s.bootstrap);

  // 마운트 시 1회
  useEffect(() => {
    void bootstrap();
    // bootstrap은 zustand 액션이라 보통 안정적인 참조임.
    // 의존성에 bootstrap만 넣는 게 안전.
  }, [bootstrap]);

  // 포커스/가시성 복귀 시만
  useEffect(() => {
    const run = () => {
      void bootstrap();
    };
    const onVis = () => {
      if (document.visibilityState === 'visible') run();
    };
    window.addEventListener('focus', run);
    document.addEventListener('visibilitychange', onVis);
    return () => {
      window.removeEventListener('focus', run);
      document.removeEventListener('visibilitychange', onVis);
    };
  }, [bootstrap]);

  return (
    <div className="min-h-screen bg-gradient-to-br bg-slate-800">
      <div className="mx-auto px-4 sm:px-6 lg:px-8 max-w-[1800px]">
        <Header />
        <div className="pt-5 pb-5">
          <Outlet />
        </div>
        <Footer />
      </div>
    </div>
  );
}
