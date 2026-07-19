import React, { useRef, useEffect } from 'react';

interface AutocompleteProps {
  completions: string[];
  onSelect: (val: string) => void;
  onClose: () => void;
}

export const Autocomplete: React.FC<AutocompleteProps> = ({ completions, onSelect, onClose }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    document.addEventListener('mousedown', handleOutsideClick);
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, [onClose]);

  return (
    <div
      ref={containerRef}
      className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-2xl shadow-lg z-50 overflow-hidden font-sans text-xs"
    >
      <ul className="divide-y divide-slate-100">
        {completions.map((phrase, idx) => (
          <li key={idx}>
            <button
              type="button"
              onClick={() => onSelect(phrase)}
              className="w-full text-left px-4 py-2.5 hover:bg-indigo-50/50 text-slate-800 transition cursor-pointer"
            >
              {phrase}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
