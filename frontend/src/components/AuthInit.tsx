import { useEffect } from 'react';
import { useAuth } from '../stores/auth';

export default function AuthInit() {
  const { bootstrap } = useAuth();
  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);
  return null;
}
