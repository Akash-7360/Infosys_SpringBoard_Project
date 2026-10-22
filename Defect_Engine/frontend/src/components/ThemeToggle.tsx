'use client';

import React, { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';

export const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Avoid hydration mismatch by waiting for mount
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-16 h-8 rounded-full bg-surface border border-surface-border animate-pulse" />
    );
  }

  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={`Switch to ${isDark ? 'Light' : 'Dark'} theme`}
      className="group relative flex items-center justify-between w-16 h-8 px-1 rounded-full bg-surface/90 hover:bg-surface border border-surface-border shadow-sm transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
      title={`Current: ${isDark ? 'Dark Mode' : 'Light Mode'} (Click to switch)`}
    >
      {/* Background track icons */}
      <span className="flex items-center justify-center w-6 h-6 text-amber-500/80 transition-opacity duration-200">
        <Sun className="w-3.5 h-3.5" />
      </span>
      <span className="flex items-center justify-center w-6 h-6 text-indigo-400/80 transition-opacity duration-200">
        <Moon className="w-3.5 h-3.5" />
      </span>

      {/* Floating sliding thumb knob */}
      <div
        className={`absolute top-1 left-1 w-6 h-6 rounded-full flex items-center justify-center shadow-md transform transition-all duration-300 ease-spring ${
          isDark
            ? 'translate-x-8 bg-indigo-600 text-white shadow-indigo-600/40 ring-1 ring-white/20'
            : 'translate-x-0 bg-amber-400 text-amber-950 shadow-amber-500/40 ring-1 ring-amber-300'
        }`}
      >
        {isDark ? (
          <Moon className="w-3 h-3 text-white transition-transform duration-300 rotate-0" />
        ) : (
          <Sun className="w-3.5 h-3.5 text-amber-950 transition-transform duration-300 rotate-90" />
        )}
      </div>
    </button>
  );
};
