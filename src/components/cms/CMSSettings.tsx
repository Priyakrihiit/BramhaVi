import React, { useState } from 'react';
import { Settings, Save } from 'lucide-react';

export const CMSSettings: React.FC = () => {
  const [siteName, setSiteName] = useState('BrahmaVidya Academy');
  const [enableCache, setEnableCache] = useState(true);
  const [enableMediaCleanup, setEnableMediaCleanup] = useState(true);

  return (
    <div className="p-5 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
      <div>
        <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">CMS Global Config</h3>
        <p className="text-xs text-slate-500">Configure global caching policies, media library cleaners, and metadata targets</p>
      </div>

      <div className="space-y-4 max-w-lg">
        <div>
          <label className="block text-[10px] uppercase font-bold text-slate-400 font-mono mb-1">Site Title Namespace</label>
          <input
            type="text"
            value={siteName}
            onChange={e => setSiteName(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center justify-between p-3 bg-slate-950 border border-slate-800 rounded-xl">
          <div>
            <span className="block font-semibold text-slate-200 text-xs">Enable Query Caching</span>
            <span className="block text-[10px] text-slate-500 font-mono">Invalidates cache automatically on publish signals</span>
          </div>
          <button
            onClick={() => setEnableCache(!enableCache)}
            className={`w-10 h-5 rounded-full transition-colors ${enableCache ? 'bg-indigo-600' : 'bg-slate-800'}`}
          />
        </div>

        <div className="flex items-center justify-between p-3 bg-slate-950 border border-slate-800 rounded-xl">
          <div>
            <span className="block font-semibold text-slate-200 text-xs">Automated Media Cleanup</span>
            <span className="block text-[10px] text-slate-500 font-mono">Deletes local files from storage when models are purged</span>
          </div>
          <button
            onClick={() => setEnableMediaCleanup(!enableMediaCleanup)}
            className={`w-10 h-5 rounded-full transition-colors ${enableMediaCleanup ? 'bg-indigo-600' : 'bg-slate-800'}`}
          />
        </div>

        <button className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg transition flex items-center justify-center gap-1.5">
          <Save size={14} />
          Save Configurations
        </button>
      </div>
    </div>
  );
};
