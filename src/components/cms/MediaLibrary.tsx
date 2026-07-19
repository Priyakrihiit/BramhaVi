import React, { useEffect, useState } from 'react';
import { cmsApi } from '../../services/cmsApi';
import { Image, Upload, Trash2, Link } from 'lucide-react';

export const MediaLibrary: React.FC = () => {
  const [mediaFiles, setMediaFiles] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);

  const loadMedia = async () => {
    const res = await cmsApi.media.list();
    if (res.success && res.data) {
      setMediaFiles(res.data);
    }
  };

  useEffect(() => {
    loadMedia();
  }, []);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    setUploading(true);
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('caption', file.name);
    formData.append('alt_text', file.name);

    try {
      const res = await cmsApi.media.create(formData);
      if (res.success) {
        loadMedia();
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono text-indigo-400">Media Library</h3>
          <p className="text-xs text-slate-500">Store featured images, PDFs, and rich graphics with automatic cleanups</p>
        </div>
        <label className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg cursor-pointer transition flex items-center gap-2">
          <Upload size={14} />
          {uploading ? 'Uploading...' : 'Upload Media Asset'}
          <input type="file" onChange={handleUpload} className="hidden" disabled={uploading} />
        </label>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {mediaFiles.length === 0 ? (
          <div className="col-span-full py-16 text-center text-slate-500 text-xs italic">
            No media files uploaded yet. Upload your first asset above.
          </div>
        ) : (
          mediaFiles.map(file => (
            <div key={file.id} className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-lg flex flex-col justify-between">
              <div className="p-3 aspect-video bg-slate-950 flex items-center justify-center border-b border-slate-800 relative group">
                <Image className="text-slate-700" size={32} />
                <div className="absolute inset-0 bg-slate-950/80 opacity-0 group-hover:opacity-100 flex items-center justify-center gap-2 transition-opacity">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(file.file_url || '');
                      alert('Copied URL to clipboard!');
                    }}
                    className="p-1.5 bg-slate-800 text-slate-300 rounded hover:text-white transition"
                    title="Copy URL"
                  >
                    <Link size={14} />
                  </button>
                  <button
                    onClick={async () => {
                      await cmsApi.media.delete(file.id);
                      loadMedia();
                    }}
                    className="p-1.5 bg-red-950 text-red-400 rounded hover:bg-red-900/20 transition"
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              <div className="p-3 text-left">
                <span className="block text-xs font-semibold text-slate-200 truncate">{file.original_filename}</span>
                <span className="block text-[9px] text-slate-500 font-mono mt-0.5">SIZE: {(file.file_size_bytes / 1024).toFixed(1)} KB</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
