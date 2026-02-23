'use client';
import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import ThemeToggle from '@/components/ThemeToggle';
import Link from 'next/link';

const NAV = [
  { href: '/dashboard', icon: '📊', label: 'Dashboard' },
  { href: '/chat',      icon: '💬', label: 'AI Chat'   },
  { href: '/mood',      icon: '🌡️', label: 'Mood Log'  },
  { href: '/history',   icon: '📈', label: 'History'   },
];

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.replace('/login');
  }, [user, loading, router]);

  if (loading || !user) {
    return (
      <div className="page-loader">
        <div style={{ width:52,height:52,background:'linear-gradient(135deg,#7c6ff7,#a78bfa)',borderRadius:14,display:'flex',alignItems:'center',justifyContent:'center',fontSize:24 }}>🧠</div>
        <div className="spinner" />
      </div>
    );
  }

  const initials = (user.full_name || user.username || 'U').slice(0, 2).toUpperCase();

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">🧠</div>
          <div>
            <div className="sidebar-logo-text">MindCare AI</div>
            <div className="sidebar-logo-sub">Mental Health Assistant</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {NAV.map(item => (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${pathname.startsWith(item.href) ? 'active' : ''}`}
            >
              <span className="nav-item-icon">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Theme Toggle */}
        <div style={{ padding: '8px 0' }}>
          <ThemeToggle />
        </div>

        <div className="sidebar-user">
          <div className="sidebar-user-info">
            <div className="user-avatar">{initials}</div>
            <div className="user-meta">
              <div className="user-name">{user.full_name || user.username}</div>
              <div className="user-email">{user.email}</div>
            </div>
            <button className="logout-btn" onClick={logout} title="Sign out" id="sidebar-logout">
              ⏻
            </button>
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
