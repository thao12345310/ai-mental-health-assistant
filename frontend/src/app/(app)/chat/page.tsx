'use client';
import { useEffect, useRef, useState, useCallback } from 'react';
import { chatApi } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { useSearchParams } from 'next/navigation';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  emotion?: { primary_emotion: string; confidence: number };
  crisis?: boolean;
}

interface Session { id: number; title?: string; created_at: string; }

const EMOTION_COLORS: Record<string, string> = {
  joy: '#4caf92', sadness: '#7c6ff7', anger: '#e95c7b',
  fear: '#f5a623', surprise: '#5bc8af', neutral: '#9ba3bf',
};

export default function ChatPage() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load sessions
  useEffect(() => {
    chatApi.sessions().then(r => setSessions(r.data)).catch(() => {});
  }, []);

  // Load from URL param
  useEffect(() => {
    const sid = searchParams.get('session');
    if (sid) loadSession(parseInt(sid));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  async function loadSession(id: number) {
    setActiveSessionId(id);
    setLoadingHistory(true);
    try {
      const { data } = await chatApi.history(id);
      setMessages(data.messages.map((m: Message) => m));
    } catch {
      toast.error('Could not load session');
    } finally {
      setLoadingHistory(false);
    }
  }

  async function newSession() {
    setActiveSessionId(null);
    setMessages([]);
  }

  async function sendMessage() {
    if (!input.trim() || sending) return;
    const text = input.trim();
    setInput('');
    setSending(true);

    // Optimistic user bubble
    const tmpId = Date.now();
    setMessages(prev => [...prev, {
      id: tmpId, role: 'user', content: text,
      created_at: new Date().toISOString()
    }]);

    try {
      const { data } = await chatApi.send(text, activeSessionId ?? undefined);

      // Update session id & refresh sidebar
      if (!activeSessionId) {
        setActiveSessionId(data.session_id);
        chatApi.sessions().then(r => setSessions(r.data)).catch(() => {});
      }

      // Replace optimistic + add AI reply
      setMessages(prev => [
        ...prev.filter(m => m.id !== tmpId),
        { ...data.user_message },
        {
          ...data.ai_response,
          emotion: data.emotion,
          crisis: data.crisis_detected,
        }
      ]);

      if (data.crisis_detected) {
        toast('🆘 Crisis resources displayed below', { icon: '⚠️', duration: 6000 });
      }
    } catch (err: unknown) {
      setMessages(prev => prev.filter(m => m.id !== tmpId));
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to send message';
      toast.error(msg);
    } finally {
      setSending(false);
      textareaRef.current?.focus();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  const initials = (user?.full_name || user?.username || 'U').slice(0, 2).toUpperCase();

  return (
    <div className="chat-layout" style={{ height: '100vh' }}>
      {/* Sessions panel */}
      <div className="chat-sessions-panel">
        <div className="chat-sessions-header">
          <span className="section-title">Sessions</span>
          <button id="new-chat-btn" className="btn btn-sm btn-primary" onClick={newSession}>+ New</button>
        </div>
        <div className="sessions-list">
          {sessions.length === 0 && (
            <div style={{ padding: 16, color: 'var(--text-muted)', fontSize: 13, textAlign: 'center' }}>
              No sessions yet.<br/>Start a new chat!
            </div>
          )}
          {sessions.map(s => (
            <div
              key={s.id}
              className={`session-item ${activeSessionId === s.id ? 'active' : ''}`}
              onClick={() => loadSession(s.id)}
              id={`session-${s.id}`}
            >
              <div className="session-title">{s.title || `Session #${s.id}`}</div>
              <div className="session-date">{format(new Date(s.created_at), 'MMM d, yyyy')}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat main */}
      <div className="chat-main">
        <div className="chat-header">
          <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg,#7c6ff7,#a78bfa)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>🧠</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 15 }}>MindCare AI</div>
            <div style={{ fontSize: 12, color: 'var(--accent-success)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-success)', display: 'inline-block' }} />
              Online · here to listen
            </div>
          </div>
          {activeSessionId && (
            <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--text-muted)' }}>Session #{activeSessionId}</span>
          )}
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {!activeSessionId && messages.length === 0 && (
            <div className="empty-state">
              <div style={{ fontSize: 64, marginBottom: 12 }}>🧠</div>
              <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>Hi, I&apos;m MindCare AI</h3>
              <p style={{ color: 'var(--text-secondary)', maxWidth: 320, lineHeight: 1.6 }}>
                I&apos;m here to listen and support your mental wellness. Share what&apos;s on your mind — everything is private and safe.
              </p>
              <div style={{ display: 'flex', gap: 8, marginTop: 16, flexWrap: 'wrap', justifyContent: 'center' }}>
                {["I'm feeling anxious today", "Help me practice mindfulness", "I need someone to talk to"].map(p => (
                  <button key={p} className="btn btn-secondary btn-sm" onClick={() => { setInput(p); textareaRef.current?.focus(); }}>{p}</button>
                ))}
              </div>
            </div>
          )}

          {loadingHistory && (
            <div style={{ display: 'flex', justifyContent: 'center', padding: 24 }}>
              <div className="spinner" style={{ borderTopColor: 'var(--accent-primary)' }} />
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={`${msg.id}-${i}`}>
              {msg.crisis && (
                <div className="crisis-alert" style={{ marginBottom: 8 }}>
                  <span style={{ fontSize: 20 }}>🆘</span>
                  <div>
                    <strong style={{ color: 'var(--accent-danger)' }}>Crisis Support Resources</strong>
                    <br />Call <strong>988</strong> (Suicide &amp; Crisis Lifeline) · Text HOME to <strong>741741</strong> · Emergency: <strong>911</strong>
                  </div>
                </div>
              )}
              <div className={`message-bubble ${msg.role}`}>
                <div className={`message-avatar ${msg.role === 'assistant' ? 'ai' : 'user'}`}>
                  {msg.role === 'assistant' ? '🧠' : initials}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <div className={`message-content ${msg.crisis ? 'crisis' : msg.role === 'assistant' ? 'ai' : 'user'}`}>
                    {msg.content}
                  </div>
                  <div className="message-meta" style={msg.role === 'user' ? { textAlign: 'right' } : {}}>
                    {format(new Date(msg.created_at), 'h:mm a')}
                  </div>
                  {msg.emotion && (
                    <div className="emotion-tag" style={{ color: EMOTION_COLORS[msg.emotion.primary_emotion] || 'var(--accent-primary)' }}>
                      ✨ {msg.emotion.primary_emotion} · {(msg.emotion.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {sending && (
            <div className="message-bubble">
              <div className="message-avatar ai">🧠</div>
              <div className="typing-indicator">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="chat-input-area">
          <textarea
            ref={textareaRef}
            id="chat-input"
            className="chat-textarea"
            placeholder="Share what's on your mind… (Enter to send, Shift+Enter for newline)"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={2}
            disabled={sending}
          />
          <button
            id="chat-send-btn"
            className="chat-send-btn"
            onClick={sendMessage}
            disabled={!input.trim() || sending}
            title="Send message"
          >
            {sending ? <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> : '↑'}
          </button>
        </div>
      </div>
    </div>
  );
}
