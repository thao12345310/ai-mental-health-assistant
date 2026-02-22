'use client';
import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, clearTokens, getUser, isAuthenticated, saveTokens, saveUser } from '@/lib/auth';
import { authApi } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface AuthCtx {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, full_name?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthCtx>({} as AuthCtx);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated()) {
      const cached = getUser();
      if (cached) {
        setUser(cached);
        setLoading(false);
      } else {
        authApi.me()
          .then(({ data }) => { setUser(data); saveUser(data); })
          .catch(() => { clearTokens(); })
          .finally(() => setLoading(false));
      }
    } else {
      setLoading(false);
    }
  }, []);

  async function login(email: string, password: string) {
    const { data } = await authApi.login({ email, password });
    saveTokens(data.tokens.access_token, data.tokens.refresh_token);
    saveUser(data.user);
    setUser(data.user);
    router.push('/dashboard');
  }

  async function register(email: string, username: string, password: string, full_name?: string) {
    await authApi.register({ email, username, password, full_name });
    await login(email, password);
  }

  function logout() {
    clearTokens();
    setUser(null);
    router.push('/login');
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
