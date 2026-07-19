/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { createContext, useContext, useState, useCallback } from 'react';

// Multilingual Dictionaries
export type LocaleCode = 'en' | 'hi';

const translations = {
  en: {
    welcome: "Welcome to BrahmaVidya Galaxy",
    explore: "Explore Galaxy",
    pricing: "Pricing",
    courses: "Courses",
    tutorials: "Tutorials",
    bookstore: "Bookstore",
    portfolio: "Portfolio",
    resume: "Resume Builder",
    services: "Marketplace",
    community: "Community Forums",
    signIn: "Sign In",
    signOut: "Sign Out",
    searchPlaceholder: "Search across courses, books, services...",
    capabilities: "Active Capabilities",
  },
  hi: {
    welcome: "ब्रह्मविद्या गैलेक्सी में आपका स्वागत है",
    explore: "गैलेक्सी का अन्वेषण करें",
    pricing: "मूल्य निर्धारण",
    courses: "पाठ्यक्रम",
    tutorials: "ट्यूटोरियल",
    bookstore: "किताबों की दुकान",
    portfolio: "पोर्टफोलियो",
    resume: "रिज्यूमे बिल्डर",
    services: "मार्केटप्लेस",
    community: "सामुदायिक मंच",
    signIn: "लॉग इन करें",
    signOut: "लॉग आउट करें",
    searchPlaceholder: "पाठ्यक्रमों, पुस्तकों, सेवाओं में खोजें...",
    capabilities: "सक्रिय क्षमताएं",
  }
};

// Toast Notifications types
export type ToastType = 'success' | 'error' | 'info' | 'warning' | 'loading';

export interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
}

// Global Dialog types
export interface DialogConfig {
  isOpen: boolean;
  type: 'delete' | 'confirm' | 'warning' | 'error' | 'success' | 'payment' | 'login' | 'capability';
  title: string;
  message: string;
  onConfirm?: () => void;
}

interface GlobalContextType {
  locale: LocaleCode;
  setLocale: (code: LocaleCode) => void;
  translate: (key: keyof typeof translations['en']) => string;
  toasts: ToastItem[];
  showToast: (type: ToastType, message: string) => void;
  dismissToast: (id: string) => void;
  dialog: DialogConfig;
  showDialog: (config: Omit<DialogConfig, 'isOpen'>) => void;
  closeDialog: () => void;
}

const GlobalContext = createContext<GlobalContextType | undefined>(undefined);

export const GlobalSystemProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [locale, setLocaleState] = useState<LocaleCode>('en');
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const [dialog, setDialog] = useState<DialogConfig>({
    isOpen: false,
    type: 'success',
    title: '',
    message: '',
  });

  const setLocale = useCallback((code: LocaleCode) => {
    setLocaleState(code);
  }, []);

  const translate = useCallback((key: keyof typeof translations['en']) => {
    return translations[locale][key] || translations['en'][key] || '';
  }, [locale]);

  const showToast = useCallback((type: ToastType, message: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts(prev => [...prev, { id, type, message }]);
    
    // Auto dismiss toasts after 3.5 seconds
    if (type !== 'loading') {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id));
      }, 3500);
    }
  }, []);

  const dismissToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const showDialog = useCallback((config: Omit<DialogConfig, 'isOpen'>) => {
    setDialog({ ...config, isOpen: true });
  }, []);

  const closeDialog = useCallback(() => {
    setDialog(prev => ({ ...prev, isOpen: false }));
  }, []);

  return (
    <React.Fragment>
      <GlobalContext.Provider
        value={{
          locale,
          setLocale,
          translate,
          toasts,
          showToast,
          dismissToast,
          dialog,
          showDialog,
          closeDialog,
        }}
      >
        {children}
        
        {/* Render Global Toasts List Portal */}
        <div id="bvg-toasts-portal" className="fixed bottom-5 right-5 z-55 flex flex-col gap-2 max-w-sm w-full pointer-events-none">
          {toasts.map(t => (
            <div
              key={t.id}
              onClick={() => dismissToast(t.id)}
              className={`p-4 rounded-xl shadow-2xl border text-xs font-semibold cursor-pointer pointer-events-auto flex items-center justify-between transition-all duration-200 animate-slide-in ${
                t.type === 'success' ? 'bg-emerald-950 border-emerald-800 text-emerald-350' :
                t.type === 'error' ? 'bg-rose-950 border-rose-800 text-rose-350' :
                t.type === 'warning' ? 'bg-amber-950 border-amber-800 text-amber-350' :
                t.type === 'loading' ? 'bg-slate-900 border-indigo-950 text-slate-300' :
                'bg-slate-900 border-indigo-950 text-indigo-400'
              }`}
            >
              <div className="flex items-center gap-2">
                {t.type === 'loading' && (
                  <span className="h-3 w-3 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
                )}
                <span>{t.message}</span>
              </div>
              <span className="text-slate-500 hover:text-white pl-4">&times;</span>
            </div>
          ))}
        </div>
      </GlobalContext.Provider>
    </React.Fragment>
  );
};

export const useGlobalSystem = () => {
  const context = useContext(GlobalContext);
  if (!context) {
    throw new Error('useGlobalSystem must be used within a GlobalSystemProvider');
  }
  return context;
};
