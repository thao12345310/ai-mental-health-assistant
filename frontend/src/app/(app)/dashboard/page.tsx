'use client';
import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { moodApi, chatApi } from '@/lib/api';
import Link from 'next/link';
import { format } from 'date-fns';

interface MoodHistory {
  entries: { id: number; score: number; note?: string; logged_at: string }[];
  average_score: number | null;
  total_entries: number;
}

interface Session {
  id: number;
  title?: string;
  created_at: string;
}

const MOOD_EMOJI: Record<number, string> = {
  1:'😰',2:'😢',3:'😟',4:'😔',5:'😐',6:'🙂',7:'😊',8:'😄',9:'😁',10:'🤩'
};

function getMoodColor(score: number) {
  if (score <= 3) return 'var(--accent-danger)';
  if (score <= 5) return 'var(--accent-warning)';
  if (score <= 7) return 'var(--accent-secondary)';
  return 'var(--accent-success)';
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [mood, setMood] = useState<MoodHistory | null>(null);
  const [sessions, setSessions] = useState<Session[]>([]);

  useEffect(() => {
    moodApi.history(7).then(r => setMood(r.data)).catch(() => {});
    chatApi.sessions().then(r => setSessions(r.data)).catch(() => {});
  }, []);

  const latest = mood?.entries[0];
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <div className="page-wrapper">
      {/* Header */}
      <div className="page-header">
        <h1 className="page-title">{greeting}, {user?.full_name?.split(' ')[0] || user?.username} 👋</h1>
        <p className="page-subtitle">Here&apos;s your mental wellness overview</p>
      </div>

      {/* Stats row */}
      <div className="dashboard-grid" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(124,111,247,0.15)' }}>💬</div>
          <div className="stat-value">{sessions.length}</div>
          <div className="stat-label">Chat Sessions</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(75,175,146,0.15)' }}>📅</div>
          <div className="stat-value">{mood?.total_entries ?? '—'}</div>
          <div className="stat-label">Mood Entries (7d)</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245,166,35,0.15)' }}>⭐</div>
          <div className="stat-value">
            {mood?.average_score ? mood.average_score.toFixed(1) : '—'}
          </div>
          <div className="stat-label">Avg Mood Score</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(233,92,123,0.15)' }}>🌡️</div>
          <div className="stat-value">
            {latest ? (
              <span style={{ color: getMoodColor(latest.score) }}>{MOOD_EMOJI[latest.score]} {latest.score}</span>
            ) : '—'}
          </div>
          <div className="stat-label">Latest Mood</div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="dashboard-2col" style={{ marginBottom: 24 }}>
        <div className="card">
          <h2 className="section-title" style={{ marginBottom: 12 }}>Quick Actions</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <Link href="/chat" id="dash-start-chat" className="btn btn-primary btn-full btn-lg">
              💬 Start a Conversation
            </Link>
            <Link href="/mood" id="dash-log-mood" className="btn btn-secondary btn-full">
              🌡️ Log Today&apos;s Mood
            </Link>
            <Link href="/history" id="dash-view-history" className="btn btn-ghost btn-full">
              📈 View Mood History
            </Link>
          </div>
        </div>

        {/* Recent mood */}
        <div className="card">
          <h2 className="section-title" style={{ marginBottom: 12 }}>Recent Mood Entries</h2>
          {mood?.entries.length ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {mood.entries.slice(0, 5).map(entry => (
                <div key={entry.id} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ fontSize: 20 }}>{MOOD_EMOJI[entry.score]}</span>
                  <div style={{ flex: 1 }}>
                    <span style={{ fontWeight: 600, color: getMoodColor(entry.score) }}>{entry.score}/10</span>
                    {entry.note && <span style={{ color: 'var(--text-muted)', fontSize: 12, marginLeft: 8 }}>{entry.note.slice(0, 30)}{entry.note.length > 30 ? '…' : ''}</span>}
                  </div>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    {format(new Date(entry.logged_at), 'MMM d')}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: '24px 0' }}>
              <div className="empty-state-icon">🌡️</div>
              <p>No mood entries yet</p>
              <Link href="/mood" className="btn btn-sm btn-secondary" style={{ marginTop: 8 }}>Log Now</Link>
            </div>
          )}
        </div>
      </div>

      {/* Recent sessions */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <h2 className="section-title">Recent Chat Sessions</h2>
          <Link href="/chat" className="btn btn-sm btn-ghost" id="dash-new-session">+ New Chat</Link>
        </div>

        {sessions.length ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {sessions.slice(0, 6).map(s => (
              <Link key={s.id} href={`/chat?session=${s.id}`} style={{ textDecoration: 'none' }}>
                <div className="card-sm" style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer', transition: 'all 0.2s' }}
                  onMouseEnter={e => (e.currentTarget.style.borderColor = 'rgba(124,111,247,0.3)')}
                  onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
                >
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(124,111,247,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16 }}>💬</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
                      {s.title || `Session #${s.id}`}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      {format(new Date(s.created_at), 'MMM d, yyyy · h:mm a')}
                    </div>
                  </div>
                  <span style={{ color: 'var(--text-muted)', fontSize: 16 }}>›</span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="empty-state" style={{ padding: '24px 0' }}>
            <div className="empty-state-icon">💬</div>
            <p>No conversations yet</p>
            <Link href="/chat" className="btn btn-sm btn-primary" style={{ marginTop: 8 }}>Start Chatting</Link>
          </div>
        )}
      </div>

      {/* Crisis note */}
      <div style={{ marginTop: 20, padding: '14px 18px', background: 'rgba(233,92,123,0.07)', border: '1px solid rgba(233,92,123,0.2)', borderRadius: 12, display: 'flex', gap: 10, alignItems: 'center' }}>
        <span style={{ fontSize: 20 }}>🆘</span>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          If you&apos;re in crisis, call <strong style={{ color: 'var(--accent-danger)' }}>988</strong> (Suicide &amp; Crisis Lifeline) or <strong style={{ color: 'var(--accent-danger)' }}>911</strong>. Our AI chat also detects crisis signals and will provide immediate resources.
        </p>
      </div>
    </div>
  );
}
