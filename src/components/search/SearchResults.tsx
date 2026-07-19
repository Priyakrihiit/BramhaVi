import React from 'react';
import { SearchDocument } from '../../services/searchApi';
import {
  GraduationCap, BookOpen, FileText, Sparkles, Layers,
  FileCode, Briefcase, Image, ExternalLink
} from 'lucide-react';

interface SearchResultsProps {
  results: SearchDocument[];
  onResultClick: (doc: SearchDocument, idx: number) => void;
}

const getIcon = (indexName: string) => {
  switch (indexName.toLowerCase()) {
    case 'courses':
      return <GraduationCap className="h-4 w-4 text-indigo-600" />;
    case 'articles':
      return <BookOpen className="h-4 w-4 text-blue-600" />;
    case 'blogs':
      return <FileText className="h-4 w-4 text-emerald-600" />;
    case 'tutorials':
      return <Sparkles className="h-4 w-4 text-purple-600" />;
    case 'marketplace':
      return <Layers className="h-4 w-4 text-amber-600" />;
    case 'resumes':
      return <FileCode className="h-4 w-4 text-cyan-600" />;
    case 'jobs':
      return <Briefcase className="h-4 w-4 text-rose-600" />;
    case 'media':
      return <Image className="h-4 w-4 text-violet-600" />;
    default:
      return <Layers className="h-4 w-4 text-slate-600" />;
  }
};

export const SearchResults: React.FC<SearchResultsProps> = ({ results, onResultClick }) => {
  const handleItemClick = (doc: SearchDocument, idx: number) => {
    onResultClick(doc, idx + 1);
    // Redirect trigger
    if (doc.url_path) {
      // Direct routing action matching PortalLayout path dispatcher
      window.location.hash = doc.url_path;
    }
  };

  return (
    <div className="space-y-4 font-sans">
      {results.map((doc, idx) => (
        <div
          key={doc.id}
          className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:border-indigo-300 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
        >
          <div className="space-y-2 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="flex items-center gap-1.5 text-[10px] font-bold font-mono uppercase bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full">
                {getIcon(doc.index_name)} {doc.index_name}
              </span>
              {doc.categories && (
                <span className="text-[10px] bg-slate-50 text-slate-500 font-mono px-2 py-0.5 rounded-full">
                  {doc.categories}
                </span>
              )}
              {doc.relevance_score > 0 && (
                <span className="text-[10px] bg-indigo-50 text-indigo-700 font-mono px-2 py-0.5 rounded-full font-bold">
                  Score: {doc.relevance_score.toFixed(1)}
                </span>
              )}
            </div>
            <h3 className="text-sm font-bold text-slate-800 leading-snug">
              {doc.title}
            </h3>
            {doc.excerpt && (
              <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                {doc.excerpt}
              </p>
            )}
            {doc.tags && (
              <div className="flex flex-wrap gap-1.5 mt-2">
                {doc.tags.split(' ').map((tag, tIdx) => (
                  <span key={tIdx} className="text-[9px] text-slate-400 font-mono">
                    #{tag}
                  </span>
                ))}
              </div>
            )}
          </div>
          <div className="flex items-center justify-between md:justify-end gap-3 border-t md:border-t-0 pt-2 md:pt-0 border-slate-100">
            <div className="text-left md:text-right">
              {doc.author_name && (
                <div className="text-[10px] text-slate-400">
                  By <strong className="text-slate-600">{doc.author_name}</strong>
                </div>
              )}
              <div className="text-[9px] text-slate-400 font-mono">
                {new Date(doc.published_at).toLocaleDateString()}
              </div>
            </div>
            <button
              onClick={() => handleItemClick(doc, idx)}
              className="flex items-center gap-1 bg-slate-50 text-slate-700 hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 hover:border-indigo-200 text-xs font-bold px-3 py-2 rounded-xl transition cursor-pointer"
            >
              View <ExternalLink className="h-3 w-3" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
