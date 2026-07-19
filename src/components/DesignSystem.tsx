/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { AlertCircle, CheckCircle2, Inbox, ChevronRight, ChevronDown, Search, Plus, MoreHorizontal, HelpCircle } from 'lucide-react';

// ==========================================
// BUTTON COMPONENT
// ==========================================
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyle = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98] cursor-pointer';
  
  const variants = {
    primary: 'bg-gradient-to-r from-indigo-600 via-indigo-500 to-indigo-600 text-white hover:from-indigo-500 hover:to-indigo-400 focus:ring-indigo-500 shadow-md shadow-indigo-600/10 hover:shadow-lg hover:shadow-indigo-600/20 border border-indigo-400/20',
    secondary: 'bg-slate-900 hover:bg-slate-850 text-slate-200 border border-slate-800 hover:border-slate-700 focus:ring-slate-700',
    outline: 'bg-transparent border border-indigo-950 text-indigo-400 hover:bg-indigo-950/20 hover:border-indigo-900 focus:ring-indigo-950',
    ghost: 'bg-transparent text-slate-400 hover:text-white hover:bg-slate-900/60 focus:ring-slate-900',
    danger: 'bg-gradient-to-r from-rose-600 to-rose-700 text-white hover:from-rose-500 hover:to-rose-600 focus:ring-rose-500 shadow-md shadow-rose-950/20',
    warning: 'bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 hover:from-amber-400 hover:to-amber-500 focus:ring-amber-500 shadow-md shadow-amber-950/20',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs gap-1.5',
    md: 'px-4.5 py-2.5 text-sm gap-2',
    lg: 'px-6 py-3.5 text-base gap-2.5',
  };

  return (
    <button
      disabled={disabled || isLoading}
      className={`${baseStyle} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <span className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin"></span>
      ) : null}
      {children}
    </button>
  );
};

// ==========================================
// INPUT FIELD COMPONENT
// ==========================================
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  icon,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || React.useId();
  return (
    <div className="flex flex-col gap-1.5 text-left w-full">
      {label && (
        <label htmlFor={inputId} className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          {label}
        </label>
      )}
      <div className="relative flex items-center">
        {icon && (
          <div className="absolute left-3.5 text-slate-500 pointer-events-none">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          className={`w-full bg-slate-900 border ${error ? 'border-rose-500/50 focus:border-rose-500' : 'border-indigo-950/80 focus:border-indigo-500/80'} rounded-xl py-2.5 ${icon ? 'pl-10' : 'px-3.5'} pr-3.5 text-sm focus:outline-none focus:ring-1 ${error ? 'focus:ring-rose-500' : 'focus:ring-indigo-500'} text-slate-200 placeholder:text-slate-650 transition-all duration-200 ${className}`}
          {...props}
        />
      </div>
      {error && (
        <span className="text-[11px] text-rose-400 font-medium flex items-center gap-1">
          <AlertCircle size={12} /> {error}
        </span>
      )}
      {!error && helperText && (
        <span className="text-[10px] text-slate-500 font-medium">{helperText}</span>
      )}
    </div>
  );
};

// ==========================================
// TEXTAREA COMPONENT
// ==========================================
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || React.useId();
  return (
    <div className="flex flex-col gap-1.5 text-left w-full">
      {label && (
        <label htmlFor={inputId} className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          {label}
        </label>
      )}
      <textarea
        id={inputId}
        className={`w-full bg-slate-900 border ${error ? 'border-rose-500/50 focus:border-rose-500' : 'border-indigo-950/80 focus:border-indigo-500/80'} rounded-xl p-3 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200 placeholder:text-slate-650 transition-all duration-200 min-h-[90px] ${className}`}
        {...props}
      />
      {error && (
        <span className="text-[11px] text-rose-400 font-medium flex items-center gap-1 mt-1">
          <AlertCircle size={12} /> {error}
        </span>
      )}
    </div>
  );
};

// ==========================================
// SELECT DROPDOWN COMPONENT
// ==========================================
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

export const Select: React.FC<SelectProps> = ({
  label,
  error,
  children,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || React.useId();
  return (
    <div className="flex flex-col gap-1.5 text-left w-full">
      {label && (
        <label htmlFor={inputId} className="text-xs font-bold text-slate-400 uppercase tracking-wider">
          {label}
        </label>
      )}
      <select
        id={inputId}
        className={`w-full bg-slate-900 border ${error ? 'border-rose-500/50' : 'border-indigo-950/80 focus:border-indigo-500/80'} rounded-xl py-2.5 px-3.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200 ${className}`}
        {...props}
      >
        {children}
      </select>
    </div>
  );
};

// ==========================================
// CHECKBOX COMPONENT
// ==========================================
interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  label,
  error,
  className = '',
  id,
  ...props
}) => {
  const checkboxId = id || React.useId();
  return (
    <div className="flex flex-col gap-1 w-full text-left">
      <label htmlFor={checkboxId} className="inline-flex items-start gap-2.5 cursor-pointer text-xs text-slate-400 select-none">
        <input
          id={checkboxId}
          type="checkbox"
          className="mt-0.5 rounded border-indigo-950 bg-slate-900 text-indigo-650 focus:ring-indigo-500 h-4 w-4 transition duration-200"
          {...props}
        />
        <span>{label}</span>
      </label>
      {error && (
        <span className="text-[11px] text-rose-400 font-medium flex items-center gap-1 mt-0.5">
          <AlertCircle size={12} /> {error}
        </span>
      )}
    </div>
  );
};

// ==========================================
// RADIO BUTTON COMPONENT
// ==========================================
interface RadioProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export const Radio: React.FC<RadioProps> = ({
  label,
  className = '',
  id,
  ...props
}) => {
  const radioId = id || React.useId();
  return (
    <label htmlFor={radioId} className="inline-flex items-center gap-2 cursor-pointer text-xs text-slate-400 select-none text-left">
      <input
        id={radioId}
        type="radio"
        className="border-indigo-950 bg-slate-900 text-indigo-655 focus:ring-indigo-500 h-4 w-4 transition duration-200"
        {...props}
      />
      <span>{label}</span>
    </label>
  );
};

// ==========================================
// BADGE COMPONENT
// ==========================================
interface BadgeProps {
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'error' | 'info';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'primary',
  className = '',
}) => {
  const colors = {
    primary: 'bg-indigo-950 text-indigo-400 border border-indigo-900/60',
    success: 'bg-emerald-950/40 text-emerald-450 border border-emerald-900/40',
    warning: 'bg-amber-950/40 text-amber-450 border border-amber-900/40',
    error: 'bg-rose-950/40 text-rose-450 border border-rose-900/40',
    info: 'bg-sky-950/40 text-sky-455 border border-sky-900/40',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold font-mono uppercase tracking-wider ${colors[variant]} ${className}`}>
      {children}
    </span>
  );
};

// ==========================================
// AVATAR COMPONENT
// ==========================================
interface AvatarProps {
  src?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const Avatar: React.FC<AvatarProps> = ({
  src,
  name,
  size = 'md',
  className = '',
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6 text-[9px]',
    md: 'h-8 w-8 text-xs',
    lg: 'h-12 w-12 text-sm',
  };
  return (
    <div className={`rounded-full border border-indigo-950 bg-slate-900 flex items-center justify-center overflow-hidden shrink-0 font-bold text-slate-350 select-none ${sizeClasses[size]} ${className}`}>
      {src ? (
        <img src={src} alt="Avatar" className="h-full w-full object-cover" />
      ) : (
        <span>{name ? name.substring(0, 2).toUpperCase() : 'BV'}</span>
      )}
    </div>
  );
};

// ==========================================
// TABS NAVIGATION COMPONENT
// ==========================================
interface TabsProps {
  tabs: string[];
  activeTab: string;
  onChange: (tab: string) => void;
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className = '',
}) => {
  return (
    <div className={`flex border-b border-indigo-950/40 gap-6 text-xs font-semibold select-none ${className}`}>
      {tabs.map(t => (
        <button
          key={t}
          onClick={() => onChange(t)}
          className={`py-3 transition relative cursor-pointer ${activeTab === t ? 'text-indigo-400 font-extrabold' : 'text-slate-500 hover:text-slate-300'}`}
        >
          {t}
          {activeTab === t && (
            <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-500 rounded-full animate-fade-in" />
          )}
        </button>
      ))}
    </div>
  );
};

// ==========================================
// ACCORDION COMPONENT
// ==========================================
interface AccordionProps {
  title: string;
  children: React.ReactNode;
}

export const Accordion: React.FC<AccordionProps> = ({ title, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="border border-indigo-950/80 rounded-2xl overflow-hidden bg-slate-900/40">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex justify-between items-center p-5 text-xs font-bold text-white hover:bg-slate-900/60 transition text-left cursor-pointer"
      >
        <span>{title}</span>
        <ChevronDown size={14} className={`text-slate-500 transition duration-200 ${isOpen ? 'rotate-180 text-indigo-400' : ''}`} />
      </button>
      {isOpen && (
        <div className="p-5 border-t border-indigo-950/40 text-xs text-slate-400 leading-relaxed text-left animate-slide-down">
          {children}
        </div>
      )}
    </div>
  );
};

// ==========================================
// DIALOG MODAL BASE CONTAINER
// ==========================================
interface DialogProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export const Dialog: React.FC<DialogProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
}) => {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="fixed inset-0 cursor-pointer" onClick={onClose} />
      <div className={`relative w-full ${sizeClasses[size]} bg-[#0b1329] border border-indigo-950/80 rounded-2xl shadow-2xl p-6 overflow-hidden flex flex-col text-left animate-zoom-in`}>
        {title && (
          <div className="flex justify-between items-center border-b border-indigo-950/40 pb-4 mb-4">
            <h3 className="text-base font-bold text-white tracking-tight">{title}</h3>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white transition p-1 hover:bg-slate-900 rounded-lg text-lg leading-none cursor-pointer"
            >
              &times;
            </button>
          </div>
        )}
        <div className="flex-1 overflow-y-auto max-h-[80vh]">
          {children}
        </div>
      </div>
    </div>
  );
};

// ==========================================
// DRAWER COMPONENT
// ==========================================
interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  position?: 'left' | 'right';
}

export const Drawer: React.FC<DrawerProps> = ({
  isOpen,
  onClose,
  title,
  children,
  position = 'left',
}) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 z-50 flex bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="flex-1 cursor-pointer" onClick={onClose} />
      <div className={`w-80 bg-[#0b1329] border-t border-b border-indigo-950 p-6 flex flex-col text-left animate-slide-in relative ${position === 'left' ? 'border-r' : 'border-l ml-auto'}`}>
        <div className="flex justify-between items-center border-b border-indigo-950/40 pb-4 mb-6">
          <span className="text-sm font-bold text-white uppercase tracking-wider">{title || 'Menu'}</span>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-lg leading-none cursor-pointer">&times;</button>
        </div>
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
};

// ==========================================
// BREADCRUMB COMPONENT
// ==========================================
export const Breadcrumb: React.FC<{ items: string[] }> = ({ items }) => {
  return (
    <nav className="flex items-center gap-1.5 text-[10px] text-slate-500 font-mono select-none uppercase tracking-wider">
      {items.map((item, idx) => (
        <React.Fragment key={idx}>
          <span className={idx === items.length - 1 ? 'text-indigo-400 font-bold' : ''}>{item}</span>
          {idx < items.length - 1 && <ChevronRight size={10} />}
        </React.Fragment>
      ))}
    </nav>
  );
};

// ==========================================
// TOOLTIP COMPONENT
// ==========================================
interface TooltipProps {
  text: string;
  children: React.ReactNode;
}

export const Tooltip: React.FC<TooltipProps> = ({ text, children }) => {
  const [visible, setVisible] = useState(false);
  return (
    <div className="relative inline-block" onMouseEnter={() => setVisible(true)} onMouseLeave={() => setVisible(false)}>
      {children}
      {visible && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1 bg-slate-900 border border-indigo-950 rounded text-[10px] text-slate-200 whitespace-nowrap shadow-xl z-55 animate-fade-in pointer-events-none">
          {text}
        </div>
      )}
    </div>
  );
};

// ==========================================
// SKELETON LOADER CARD
// ==========================================
export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <div className={`p-5 bg-slate-900/60 border border-indigo-950 rounded-2xl space-y-4 animate-pulse ${className}`}>
      <div className="h-4 bg-indigo-950/80 rounded-full w-2/3"></div>
      <div className="space-y-2">
        <div className="h-3 bg-indigo-950/60 rounded-full w-full"></div>
        <div className="h-3 bg-indigo-950/60 rounded-full w-5/6"></div>
      </div>
    </div>
  );
};

// ==========================================
// LOADING SPINNER WIDGET
// ==========================================
export const LoadingSpinner: React.FC<{ text?: string }> = ({ text = 'Compiling system modules...' }) => {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-500 font-mono text-xs select-none">
      <span className="relative flex h-3 w-3">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
        <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
      </span>
      <span>{text}</span>
    </div>
  );
};

// ==========================================
// EMPTY STATE COMPONENT
// ==========================================
interface EmptyStateProps {
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No records found',
  description = 'There are currently no active elements configured for this category.',
  actionText,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 bg-slate-900/20 border border-dashed border-indigo-950 rounded-2xl py-14 max-w-md mx-auto gap-4">
      <div className="p-3.5 bg-indigo-950/40 border border-indigo-900/40 text-indigo-400 rounded-xl">
        <Inbox size={24} />
      </div>
      <div className="space-y-1">
        <h4 className="text-sm font-bold text-white">{title}</h4>
        <p className="text-xs text-slate-400 leading-relaxed">{description}</p>
      </div>
      {actionText && onAction && (
        <Button onClick={onAction} size="sm" variant="outline" className="mt-2">
          {actionText}
        </Button>
      )}
    </div>
  );
};

// ==========================================
// ERROR SPLASH PAGE COMPONENT
// ==========================================
interface ErrorSplashProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export const ErrorSplash: React.FC<ErrorSplashProps> = ({
  title = 'System Configuration Error',
  message = 'An unexpected connection limit was reached. Please verify system logs.',
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 py-16 gap-5 max-w-md mx-auto">
      <div className="p-4 bg-rose-950/50 border border-rose-900/50 text-rose-400 rounded-full animate-bounce">
        <AlertCircle size={32} />
      </div>
      <div className="space-y-2">
        <h3 className="text-lg font-black text-white tracking-tight">{title}</h3>
        <p className="text-xs text-slate-400 leading-relaxed">{message}</p>
      </div>
      {onRetry && (
        <Button onClick={onRetry} variant="secondary">
          Retry System Connection
        </Button>
      )}
    </div>
  );
};

// ==========================================
// PAGINATION COMPONENT
// ==========================================
interface PaginationProps {
  current: number;
  total: number;
  onChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ current, total, onChange }) => {
  return (
    <div className="flex items-center gap-1.5 justify-center mt-6 text-xs font-mono select-none">
      <button disabled={current <= 1} onClick={() => onChange(current - 1)} className="px-2.5 py-1.5 rounded-lg border border-indigo-950 text-slate-400 hover:text-white disabled:opacity-30 cursor-pointer">
        Prev
      </button>
      {Array.from({ length: total }).map((_, idx) => (
        <button key={idx} onClick={() => onChange(idx + 1)} className={`px-3 py-1.5 rounded-lg border transition cursor-pointer ${current === idx + 1 ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'border-indigo-950 text-slate-500 hover:text-slate-300'}`}>
          {idx + 1}
        </button>
      ))}
      <button disabled={current >= total} onClick={() => onChange(current + 1)} className="px-2.5 py-1.5 rounded-lg border border-indigo-950 text-slate-400 hover:text-white disabled:opacity-30 cursor-pointer">
        Next
      </button>
    </div>
  );
};

// ==========================================
// SEARCH BAR WIDGET
// ==========================================
interface SearchBarProps {
  placeholder?: string;
  onSearch: (q: string) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ placeholder = 'Search...', onSearch }) => {
  const [q, setQ] = useState('');
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(q);
  };
  return (
    <form onSubmit={handleSubmit} className="relative w-full text-left">
      <Search className="absolute left-3.5 top-3.5 text-slate-500" size={15} />
      <input
        type="text"
        placeholder={placeholder}
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="w-full bg-slate-900 border border-indigo-950/80 rounded-xl py-3 pl-11 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200"
      />
    </form>
  );
};

// ==========================================
// STATS CARD COMPONENT
// ==========================================
interface StatsCardProps {
  label: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
}

export const StatsCard: React.FC<StatsCardProps> = ({ label, value, change, isPositive = true }) => {
  return (
    <div className="p-5 bg-slate-900/60 border border-indigo-950 rounded-2xl text-left relative overflow-hidden">
      <span className="block text-[10px] text-slate-500 uppercase font-bold tracking-wider">{label}</span>
      <span className="block text-2xl font-black text-white mt-1.5">{value}</span>
      {change && (
        <span className={`block text-[10px] font-mono mt-1 ${isPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
          {isPositive ? '▲' : '▼'} {change}
        </span>
      )}
    </div>
  );
};

// ==========================================
// CHARTS WRAPPER (PREMIUM COMPONENT MOCK)
// ==========================================
interface ChartsProps {
  title: string;
  data: number[];
  labels: string[];
}

export const ChartsWrapper: React.FC<ChartsProps> = ({ title, data, labels }) => {
  const max = Math.max(...data) || 1;
  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl text-left space-y-4">
      <h4 className="text-xs font-bold text-white uppercase tracking-wider">{title}</h4>
      <div className="flex items-end gap-3 h-32 pt-4">
        {data.map((val, idx) => {
          const heightPercent = `${(val / max) * 100}%`;
          return (
            <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end gap-1.5 group">
              <div 
                style={{ height: heightPercent }} 
                className="w-full bg-indigo-650/80 group-hover:bg-indigo-500 rounded-t-lg transition-all duration-300 relative"
              >
                <div className="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition text-[9px] font-mono text-slate-350 bg-slate-950 px-1 py-0.5 rounded border border-indigo-900">
                  {val}
                </div>
              </div>
              <span className="text-[9px] text-slate-500 font-mono truncate w-full text-center">{labels[idx]}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// ==========================================
// DATA TABLE COMPONENT
// ==========================================
interface DataTableProps {
  headers: string[];
  rows: any[][];
}

export const DataTable: React.FC<DataTableProps> = ({ headers, rows }) => {
  return (
    <div className="w-full overflow-x-auto rounded-2xl border border-indigo-950 bg-slate-900/20">
      <table className="w-full border-collapse text-left text-xs">
        <thead>
          <tr className="bg-slate-900 border-b border-indigo-950/80">
            {headers.map((h, idx) => (
              <th key={idx} className="p-4 font-bold text-slate-400 uppercase tracking-wider text-[10px]">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-indigo-950/45 text-slate-300">
          {rows.map((row, rIdx) => (
            <tr key={rIdx} className="hover:bg-slate-900/40 transition">
              {row.map((cell, cIdx) => (
                <td key={cIdx} className="p-4">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ==========================================
// NOTIFICATION BADGE COMPONENT
// ==========================================
export const NotificationBadge: React.FC<{ count: number }> = ({ count }) => {
  if (count <= 0) return null;
  return (
    <span className="inline-flex h-4 min-w-[16px] px-1 items-center justify-center rounded-full bg-rose-600 text-white font-mono text-[9px] font-bold select-none border border-slate-950">
      {count > 99 ? '99+' : count}
    </span>
  );
};

// ==========================================
// FLOATING ACTION BUTTON COMPONENT
// ==========================================
export const FloatingButton: React.FC<{ onClick: () => void; icon?: React.ReactNode }> = ({ onClick, icon }) => {
  return (
    <button 
      onClick={onClick}
      className="fixed bottom-6 right-6 p-4 rounded-full bg-indigo-650 hover:bg-indigo-500 text-white shadow-2xl transition duration-150 active:scale-95 cursor-pointer z-40 border border-indigo-500/20 hover:scale-105"
    >
      {icon || <Plus size={20} />}
    </button>
  );
};
