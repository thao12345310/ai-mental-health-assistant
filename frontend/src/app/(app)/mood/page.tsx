'use client';
import { useState } from 'react';
import { moodApi } from '@/lib/api';
import toast from 'react-hot-toast';

const MOOD_LABELS: Record<number, { label: string; emoji: string; desc: string }> = {
  1:  { label: 'Terrible',    emoji: '😰', desc: 'Extremely distressed' },
  2:  { label: 'Very Bad',    emoji: '😢', desc: 'Very difficult day'   },
  3:  { label: 'Bad',         emoji: '😟', desc: 'Struggling a bit'     },
  4:  { label: 'Poor',        emoji: '😔', desc: 'Below average'        },
  5:  { label: 'Okay',        emoji: '😐', desc: 'Neutral, getting by'  },
  6:  { label: 'Decent',      emoji: '🙂', desc: 'Slightly positive'    },
  7:  { label: 'Good',        emoji: '😊', desc: 'Feeling good'         },
  8:  { label: 'Great',       emoji: '😄', desc: 'Really positive'      },
  9:  { label: 'Excellent',   emoji: '😁', desc: 'Having a great day'   },
  10: { label: 'Amazing',     emoji: '🤩', desc: 'Exceptional wellbeing' },
};

function getScoreColor(s: number) {
  if (s <= 3) return 'var(--accent-danger)';
  if (s <= 5) return 'var(--accent-warning)';
  if (s <= 7) return 'var(--accent-secondary)';
  return 'var(--accent-success)';
}

export default function MoodPage() {
  const [score, setScore] = useState(5);
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [logged, setLogged] = useState<{ score: number; note?: string } | null>(null);

  const info = MOOD_LABELS[score];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await moodApi.log(score, note || undefined);
      setLogged({ score, note: note || undefined });
      toast.success('Mood logged! 🌟');
      setNote('');
    } catch {
      toast.error('Failed to log mood');
    } finally {
      setLoading(false);
    }
  }

  if (logged) {
    return (
      <div className="page-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80vh' }}>
        <div className="card" style={{ maxWidth: 420, width: '100%', textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 72, marginBottom: 12 }}>{MOOD_LABELS[logged.score].emoji}</div>
          <h2 style={{ fontSize: 22, fontWeight: 800, marginBottom: 6 }}>Mood Logged!</h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 4 }}>
            You logged a <strong style={{ color: getScoreColor(logged.score) }}>{logged.score}/10 — {MOOD_LABELS[logged.score].label}</strong>
          </p>
          {logged.note && <p style={{ color: 'var(--text-muted)', fontSize: 13, fontStyle: 'italic', marginBottom: 20 }}>&ldquo;{logged.note}&rdquo;</p>}
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap', marginTop: 20 }}>
            <button className="btn btn-primary" onClick={() => setLogged(null)} id="log-another-btn">Log Another</button>
            <a href="/history" className="btn btn-secondary">View History</a>
            <a href="/chat" className="btn btn-ghost">Talk to AI</a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-wrapper">
      <div className="page-header">
        <h1 className="page-title">How are you feeling?</h1>
        <p className="page-subtitle">Track your mood daily to understand patterns over time</p>
      </div>

      <div style={{ maxWidth: 560, margin: '0 auto' }}>
        <form onSubmit={handleSubmit}>
          {/* Score display */}
          <div className="card" style={{ textAlign: 'center', marginBottom: 20, padding: 36 }}>
            <div className="mood-score-display" style={{ borderColor: getScoreColor(score), boxShadow: `0 0 24px ${getScoreColor(score)}40` }}>
              {score}
            </div>
            <div style={{ fontSize: 48, marginBottom: 6 }}>{info.emoji}</div>
            <h2 style={{ fontSize: 22, fontWeight: 800, color: getScoreColor(score) }}>{info.label}</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>{info.desc}</p>
          </div>

          {/* Slider */}
          <div className="card" style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
              <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>😰 Terrible</span>
              <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Amazing 🤩</span>
            </div>
            <input
              id="mood-slider"
              type="range"
              className="mood-slider"
              min={1} max={10} step={1}
              value={score}
              onChange={e => setScore(parseInt(e.target.value))}
            />
            {/* Tick marks */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
              {[1,2,3,4,5,6,7,8,9,10].map(n => (
                <button
                  type="button"
                  key={n}
                  onClick={() => setScore(n)}
                  style={{
                    width: 28, height: 28, borderRadius: '50%', border: 'none',
                    background: score === n ? getScoreColor(n) : 'var(--bg-elevated)',
                    color: score === n ? 'white' : 'var(--text-muted)',
                    fontSize: 11, fontWeight: 700, cursor: 'pointer',
                    transition: 'all 0.2s',
                    transform: score === n ? 'scale(1.15)' : 'scale(1)',
                  }}
                  id={`mood-btn-${n}`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>

          {/* Note */}
          <div className="card" style={{ marginBottom: 20 }}>
            <div className="form-group">
              <label className="form-label" htmlFor="mood-note">Add a note (optional)</label>
              <textarea
                id="mood-note"
                className="form-input"
                placeholder="What's contributing to your mood today? Any thoughts or events worth noting…"
                value={note}
                onChange={e => setNote(e.target.value)}
                rows={4}
                maxLength={1000}
              />
              <span style={{ fontSize: 11, color: 'var(--text-muted)', textAlign: 'right', display: 'block' }}>
                {note.length}/1000
              </span>
            </div>
          </div>

          <button
            type="submit"
            id="log-mood-submit"
            className="btn btn-primary btn-lg btn-full"
            disabled={loading}
          >
            {loading ? <span className="spinner" /> : '🌡️'}
            {loading ? 'Saving…' : 'Log My Mood'}
          </button>
        </form>
      </div>
    </div>
  );
}
