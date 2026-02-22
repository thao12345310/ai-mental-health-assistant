'use client';
import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';
import toast from 'react-hot-toast';

export default function RegisterPage() {
  const { register } = useAuth();
  const [form, setForm] = useState({ email: '', username: '', password: '', full_name: '' });
  const [loading, setLoading] = useState(false);

  function set(field: string) {
    return (e: React.ChangeEvent<HTMLInputElement>) => setForm(f => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (form.password.length < 8) { toast.error('Password must be at least 8 characters'); return; }
    if (!/[A-Z]/.test(form.password)) { toast.error('Password must contain an uppercase letter'); return; }
    if (!/\d/.test(form.password)) { toast.error('Password must contain a digit'); return; }
    setLoading(true);
    try {
      await register(form.email, form.username, form.password, form.full_name || undefined);
      toast.success('Account created! Welcome 🎉');
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Registration failed');
    } finally {
      setLoading(false);
    }
  }

  const strengthColor = () => {
    const p = form.password;
    if (p.length === 0) return 'transparent';
    if (p.length < 6) return 'var(--accent-danger)';
    if (p.length < 10 || !/[A-Z]/.test(p) || !/\d/.test(p)) return 'var(--accent-warning)';
    return 'var(--accent-success)';
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">🧠</div>
        <h1 className="auth-title">Create account</h1>
        <p className="auth-subtitle">Start your mental wellness journey today</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="reg-name">Full name (optional)</label>
            <input id="reg-name" type="text" className="form-input" placeholder="Jane Doe" value={form.full_name} onChange={set('full_name')} />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-username">Username</label>
            <input id="reg-username" type="text" className="form-input" placeholder="jane_doe" value={form.username} onChange={set('username')} required pattern="^[a-zA-Z0-9_]+" minLength={3} />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-email">Email address</label>
            <input id="reg-email" type="email" className="form-input" placeholder="you@example.com" value={form.email} onChange={set('email')} required />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="reg-password">Password</label>
            <input id="reg-password" type="password" className="form-input" placeholder="Min 8 chars, 1 uppercase, 1 digit" value={form.password} onChange={set('password')} required minLength={8} />
            {form.password && (
              <div style={{ height: 3, borderRadius: 99, background: 'var(--bg-muted)', overflow: 'hidden', marginTop: 4 }}>
                <div style={{ height: '100%', background: strengthColor(), width: Math.min(100, form.password.length * 8) + '%', transition: 'all 0.3s' }} />
              </div>
            )}
          </div>

          <button type="submit" className="btn btn-primary btn-lg btn-full" disabled={loading} id="register-submit">
            {loading ? <span className="spinner" /> : null}
            {loading ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{' '}
          <Link href="/login" className="auth-link">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
