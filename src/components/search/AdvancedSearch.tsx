import React from 'react';
import { Settings } from 'lucide-react';

interface AdvancedSearchProps {
  selectedScope: string;
  setSelectedScope: (scope: string) => void;
  selectedType: string;
  setSelectedType: (type: string) => void;
  facetsParam: string;
  setFacetsParam: (facets: string) => void;
}

export const AdvancedSearch: React.FC<AdvancedSearchProps> = ({
  selectedScope,
  setSelectedScope,
  selectedType,
  setSelectedType,
  facetsParam,
  setFacetsParam
}) => {
  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4 font-sans text-xs">
      <h3 className="font-bold text-slate-800 text-xs uppercase tracking-wider flex items-center gap-1.5 font-mono border-b border-slate-100 pb-2.5">
        <Settings className="h-4 w-4 text-indigo-600" /> Advanced Options
      </h3>

      <div className="space-y-4">
        {/* Scope Index */}
        <div className="space-y-1.5">
          <label className="font-bold text-slate-500 uppercase font-mono text-[9px] tracking-wider block">
            Target Index
          </label>
          <select
            value={selectedScope}
            onChange={(e) => setSelectedScope(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none cursor-pointer"
          >
            <option value="">All Indexes (Global Search)</option>
            <option value="courses">LMS Courses</option>
            <option value="articles">CMS Articles</option>
            <option value="blogs">CMS Blogs</option>
            <option value="tutorials">Developer Tutorials</option>
            <option value="faqs">CMS FAQs</option>
            <option value="media">DAM Media Library</option>
            <option value="marketplace">Marketplace Books</option>
            <option value="portfolios">Portfolios</option>
            <option value="resumes">Resumes</option>
            <option value="jobs">Jobs</option>
          </select>
        </div>

        {/* Entity Model Class Type */}
        <div className="space-y-1.5">
          <label className="font-bold text-slate-500 uppercase font-mono text-[9px] tracking-wider block">
            Entity Type Class
          </label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none cursor-pointer"
          >
            <option value="">Any Type</option>
            <option value="CourseStructure">CourseStructure</option>
            <option value="Article">Article</option>
            <option value="Blog">Blog</option>
            <option value="Page">Page</option>
            <option value="Tutorial">Tutorial</option>
            <option value="FAQ">FAQ</option>
            <option value="MediaFile">MediaFile</option>
            <option value="Book">Book</option>
            <option value="Website">Website</option>
            <option value="Resume">Resume</option>
            <option value="Job">Job</option>
          </select>
        </div>

        {/* Aggregated Facets Config */}
        <div className="space-y-1.5">
          <label className="font-bold text-slate-500 uppercase font-mono text-[9px] tracking-wider block">
            Requested Facets (comma separated)
          </label>
          <input
            type="text"
            placeholder="e.g. Level, Format, price"
            value={facetsParam}
            onChange={(e) => setFacetsParam(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          />
        </div>
      </div>
    </div>
  );
};
