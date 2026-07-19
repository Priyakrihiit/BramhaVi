/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

export type AppTheme = 'dark' | 'light' | 'gold';

interface ThemeContextType {
  theme: AppTheme;
  setTheme: (theme: AppTheme) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<AppTheme>(() => {
    const saved = localStorage.getItem('bvg_theme') as AppTheme;
    return saved || 'dark'; // Dark theme is default for deep космический feel
  });

  const setTheme = (newTheme: AppTheme) => {
    setThemeState(newTheme);
    localStorage.setItem('bvg_theme', newTheme);
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : theme === 'light' ? 'gold' : 'dark');
  };

  useEffect(() => {
    const root = document.documentElement;
    // Remove existing theme classes
    root.classList.remove('theme-dark', 'theme-light', 'theme-gold');
    // Add current theme class
    root.classList.add(`theme-${theme}`);

    // Set dark/light class on body/html for Tailwind CSS compatibility
    if (theme === 'dark' || theme === 'gold') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  return (
    <React.Fragment>
      <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
        {children}
      </ThemeContext.Provider>
    </React.Fragment>
  );
};

export const useThemeStore = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeStore must be used within a ThemeProvider');
  }
  return context;
};
