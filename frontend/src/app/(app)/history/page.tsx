'use client';
import { useEffect, useState } from 'react';
import { moodApi } from '@/lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { format } from 'date-fns';

interface MoodEntry {
  id: number;
  score: number;
  note?: string;
  logged_at: string;
}

interface MoodHistory {
  entries: MoodEntry[];
  average_score: number | null;
  total_entries: number;
}

const EMOJI: Record<number, string> = {1:'😰',2:'😢',3:'😟',4:'😔',5:'😐',6:'🙂',7:'😊',8:'😄',9:'😁',10:'🤩'};

function getColor(s: number) {
  if (s <= 3) return '#e95c7b';
  if (s <= 5) return '#f5a623';
  if (s <= 7) return '#5bc8af';
  return '#4caf92';
}

const CustomDot = (props: { cx?: number; cy?: number; payload?: MoodEntry }) => {
  const { cx, cy, payload } = props;
  if (!cx || !cy || !payload) return null;
  return (
    <circle cx={cx} cy={cy} r={5} fill={getColor(payload.score)} stroke="#1a1e2a" strokeWidth={2} />
  );
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload as MoodEntry;
  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 10, padding: '10px 14px', fontSize: 13 }}>
      <div style={{ fontWeight: 700, color: getColor(d.score), marginBottom: 4 }}>
        {EMOJI[d.score]} {d.score}/10
      </div>
      <div style={{ color: 'var(--text-muted)' }}>{format(new Date(d.logged_at), 'MMM d, yyyy · h:mm a')}</div>
      {d.note && <div style={{ color: 'var(--text-secondary)', marginTop: 4, maxWidth: 200, fontStyle: 'italic' }}>&ldquo;{d.note}&rdquo;</div>}
    </div>
  );
};

export default function HistoryPage() {
  const [data, setData] = useState<MoodHistory | null>(null);
  const [limit, setLimit] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    moodApi.history(limit)
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [limit]);

  const chartData = data?.entries.slice().reverse() ?? [];

  function getMoodTrend() {
    if (!chartData.length || chartData.length < 2) return null;
    const first = chartData.slice(0, 3).reduce((a, b) => a + b.score, 0) / 3;
    const last = chartData.slice(-3).reduce((a, b) => a + b.score, 0) / 3;
    if (last > first + 0.5) return { dir: 'up', label: 'Improving ↑', color: 'var(--accent-success)' };
    if (last < first - 0.5) return { dir: 'down', label: 'Declining ↓', color: 'var(--accent-danger)' };
    return { dir: 'flat', label: 'Stable →', color: 'var(--accent-warning)' };
  }

  const trend = getMoodTrend();

  return (
    <div className="page-wrapper">
      <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <h1 className="page-title">Mood History</h1>
          <p className="page-subtitle">Track your emotional wellbeing over time</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {[7, 14, 30].map(n => (
            <button
              key={n}
              id={`history-limit-${n}`}
              className={`btn btn-sm ${limit === n ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setLimit(n)}
            >
              {n}d
            </button>
          ))}
        </div>
      </div>

      {/* Stats row */}
      <div className="dashboard-grid" style={{ marginBottom: 24 }}>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(124,111,247,0.15)' }}>📊</div>
          <div className="stat-value">{data?.total_entries ?? '—'}</div>
          <div className="stat-label">Total Entries</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(75,175,146,0.15)' }}>⭐</div>
          <div className="stat-value" style={{ color: data?.average_score ? getColor(Math.round(data.average_score)) : undefined }}>
            {data?.average_score?.toFixed(1) ?? '—'}
          </div>
          <div className="stat-label">Average Score</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(91,200,175,0.15)' }}>📈</div>
          <div className="stat-value" style={{ fontSize: 20, color: trend?.color }}>{trend?.label ?? '—'}</div>
          <div className="stat-label">Trend</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245,166,35,0.15)' }}>🌡️</div>
          <div className="stat-value">
            {data?.entries[0] ? (
              <span style={{ color: getColor(data.entries[0].score) }}>
                {EMOJI[data.entries[0].score]} {data.entries[0].score}
              </span>
            ) : '—'}
          </div>
          <div className="stat-label">Latest Mood</div>
        </div>
      </div>

      {/* Chart */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 className="section-title" style={{ marginBottom: 20 }}>Mood Over Time</h2>
        {loading ? (
          <div style={{ height: 240, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="spinner" style={{ borderTopColor: 'var(--accent-primary)', width: 32, height: 32, borderWidth: 3 }} />
          </div>
        ) : chartData.length < 2 ? (
          <div className="empty-state" style={{ height: 200 }}>
            <div className="empty-state-icon">📉</div>
            <p>Log at least 2 entries to see the chart</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="logged_at" tickFormatter={d => format(new Date(d), 'MMM d')} tick={{ fill: '#626880', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 10]} ticks={[2, 4, 6, 8, 10]} tick={{ fill: '#626880', fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              {data?.average_score && (
                <ReferenceLine y={data.average_score} stroke="rgba(124,111,247,0.4)" strokeDasharray="4 4" label={{ value: 'avg', fill: '#7c6ff7', fontSize: 11 }} />
              )}
              <Line type="monotone" dataKey="score" stroke="#7c6ff7" strokeWidth={2.5} dot={<CustomDot />} activeDot={{ r: 7, fill: '#7c6ff7' }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Entry list */}
      <div className="card">
        <h2 className="section-title" style={{ marginBottom: 16 }}>All Entries</h2>
        {!data?.entries.length ? (
          <div className="empty-state">
            <div className="empty-state-icon">🌡️</div>
            <p>No mood entries yet</p>
            <a href="/mood" className="btn btn-primary btn-sm" style={{ marginTop: 12 }}>Log Your First Mood</a>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {data.entries.map(entry => (
              <div key={entry.id} style={{ display: 'flex', alignItems: 'flex-start', gap: 14, padding: '12px 0', borderBottom: '1px solid var(--border)' }}>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: `${getColor(entry.score)}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, flexShrink: 0 }}>
                  {EMOJI[entry.score]}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontWeight: 700, fontSize: 16, color: getColor(entry.score) }}>{entry.score}/10</span>
                    <span style={{ padding: '2px 8px', borderRadius: 99, fontSize: 11, fontWeight: 600, background: `${getColor(entry.score)}18`, color: getColor(entry.score) }}>
                      {entry.score <= 3 ? 'Low' : entry.score <= 5 ? 'Fair' : entry.score <= 7 ? 'Good' : 'Great'}
                    </span>
                    <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 'auto' }}>
                      {format(new Date(entry.logged_at), 'MMM d, yyyy · h:mm a')}
                    </span>
                  </div>
                  {entry.note && (
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4, lineHeight: 1.5 }}>
                      {entry.note}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
