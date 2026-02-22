'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.replace(isAuthenticated() ? '/dashboard' : '/login');
  }, [router]);

  return (
    <div className="page-loader">
      <div className="sidebar-logo-icon" style={{ width: 52, height: 52, fontSize: 24 }}>🧠</div>
      <div className="spinner" />
    </div>
  );
}
