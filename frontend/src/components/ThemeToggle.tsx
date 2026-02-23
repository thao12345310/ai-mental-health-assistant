'use client';
import { useTheme } from '@/contexts/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      className="theme-toggle"
      title={isDark ? 'Chuyển sang Light mode' : 'Chuyển sang Dark mode'}
      aria-label="Toggle theme"
    >
      <span className="theme-toggle-track">
        <span className="theme-toggle-thumb">
          {isDark ? '🌙' : '☀️'}
        </span>
      </span>
      <span className="theme-toggle-label">
        {isDark ? 'Dark' : 'Light'}
      </span>
    </button>
  );
}
