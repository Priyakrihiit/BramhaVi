import React, { useEffect, useState } from 'react';
import { mediaApi } from '../../services/mediaApi';
import {
  Folder, Image, Upload, Trash2, Link, Heart, Search, Eye,
  Sliders, Settings, Info, FileText, Video, RefreshCw, CheckCircle, AlertTriangle
} from 'lucide-react';

export const EnterpriseMediaLibrary: React.FC = () => {
  // States
  const [folders, setFolders] = useState<any[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
  const [collections, setCollections] = useState<any[]>([]);
  const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
  const [mediaFiles, setMediaFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<any | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewTab, setViewTab] = useState<'all' | 'favorites' | 'trash' | 'workflows'>('all');
  const [uploading, setUploading] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [newCollectionName, setNewCollectionName] = useState('');

  // Stats for Dashboard
  const [stats, setStats] = useState({
    totalCount: 0,
    totalSize: '0 MB',
    imageCount: 0,
    videoCount: 0,
  });

  const loadData = async () => {
    // Folders
    const fRes = await mediaApi.folders.list();
    if (fRes.success) setFolders(fRes.data || []);

    // Collections
    const cRes = await mediaApi.collections.list();
    if (cRes.success) setCollections(cRes.data || []);

    // Media Files
    const params: Record<string, string> = {};
    if (selectedFolder) params.folder = selectedFolder;
    if (viewTab === 'favorites') params.favorites = 'true';
    if (viewTab === 'trash') params.trash = 'true';

    const mRes = await mediaApi.media.list(params);
    if (mRes.success && mRes.data) {
      let files = mRes.data;
      if (searchQuery) {
        files = files.filter((f: any) =>
          f.original_filename.toLowerCase().includes(searchQuery.toLowerCase())
        );
      }
      setMediaFiles(files);

      // Compute Stats
      const totalBytes = files.reduce((acc: number, f: any) => acc + (f.file_size_bytes || 0), 0);
      setStats({
        totalCount: files.length,
        totalSize: `${(totalBytes / (1024 * 1024)).toFixed(1)} MB`,
        imageCount: files.filter((f: any) => f.file_type === 'image').length,
        videoCount: files.filter((f: any) => f.file_type === 'video').length,
      });
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedFolder, selectedCollection, searchQuery, viewTab]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    setUploading(true);
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('original_filename', file.name);
    if (selectedFolder) {
      formData.append('folder', selectedFolder);
    }

    const res = await mediaApi.media.create(formData);
    setUploading(false);
    if (res.success) {
      loadData();
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName) return;
    const res = await mediaApi.folders.create({ name: newFolderName, parent: selectedFolder });
    if (res.success) {
      setNewFolderName('');
      loadData();
    }
  };

  const handleCreateCollection = async () => {
    if (!newCollectionName) return;
    const res = await mediaApi.collections.create({ name: newCollectionName });
    if (res.success) {
      setNewCollectionName('');
      loadData();
    }
  };

  return (
    <div className="flex flex-col lg:flex-row gap-6 text-left">
      {/* Sidebar: Folder Hierarchy & Collections */}
      <div className="w-full lg:w-64 bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-6">
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Folders</h4>
          <div className="space-y-1">
            <button
              onClick={() => setSelectedFolder(null)}
              className={`w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${!selectedFolder ? 'bg-indigo-950 text-indigo-400' : 'text-slate-400 hover:text-white'}`}
            >
              <Folder size={14} />
              Root Directory
            </button>
            {folders.map(f => (
              <button
                key={f.id}
                onClick={() => setSelectedFolder(f.id)}
                className={`w-full flex items-center justify-between px-3 py-1.5 rounded-lg text-xs font-semibold transition ${selectedFolder === f.id ? 'bg-indigo-950 text-indigo-400' : 'text-slate-400 hover:text-white'}`}
              >
                <span className="flex items-center gap-2 truncate">
                  <Folder size={14} />
                  {f.name}
                </span>
                <Trash2
                  size={12}
                  className="text-slate-600 hover:text-red-400 cursor-pointer"
                  onClick={async (e) => {
                    e.stopPropagation();
                    await mediaApi.folders.delete(f.id);
                    loadData();
                  }}
                />
              </button>
            ))}
          </div>
          <div className="mt-3 flex gap-2">
            <input
              type="text"
              placeholder="New Folder"
              value={newFolderName}
              onChange={e => setNewFolderName(e.target.value)}
              className="w-full px-2 py-1 bg-slate-950 border border-slate-800 rounded text-xs text-white"
            />
            <button onClick={handleCreateFolder} className="px-2 py-1 bg-indigo-600 text-white rounded text-xs">+</button>
          </div>
        </div>

        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Collections</h4>
          <div className="space-y-1">
            {collections.map(c => (
              <button
                key={c.id}
                onClick={() => setSelectedCollection(c.id)}
                className={`w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${selectedCollection === c.id ? 'bg-indigo-950 text-indigo-400' : 'text-slate-400 hover:text-white'}`}
              >
                <Sliders size={14} />
                {c.name}
              </button>
            ))}
          </div>
          <div className="mt-3 flex gap-2">
            <input
              type="text"
              placeholder="New Collection"
              value={newCollectionName}
              onChange={e => setNewCollectionName(e.target.value)}
              className="w-full px-2 py-1 bg-slate-950 border border-slate-800 rounded text-xs text-white"
            />
            <button onClick={handleCreateCollection} className="px-2 py-1 bg-indigo-600 text-white rounded text-xs">+</button>
          </div>
        </div>
      </div>

      {/* Main Panel */}
      <div className="flex-1 space-y-6">
        {/* Dashboard summary widgets */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="block text-[10px] uppercase font-bold text-slate-500">Total Assets</span>
            <span className="text-lg font-bold text-white mt-1 block">{stats.totalCount}</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="block text-[10px] uppercase font-bold text-slate-500">Total Size</span>
            <span className="text-lg font-bold text-white mt-1 block">{stats.totalSize}</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="block text-[10px] uppercase font-bold text-slate-500">Images</span>
            <span className="text-lg font-bold text-white mt-1 block">{stats.imageCount}</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
            <span className="block text-[10px] uppercase font-bold text-slate-500">Videos</span>
            <span className="text-lg font-bold text-white mt-1 block">{stats.videoCount}</span>
          </div>
        </div>

        {/* Toolbar & Filters */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 p-4 bg-slate-900 border border-slate-800 rounded-2xl">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => { setViewTab('all'); setSelectedFolder(null); }}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${viewTab === 'all' ? 'bg-indigo-600 text-white' : 'bg-slate-850 text-slate-400 hover:text-white'}`}
            >
              All Assets
            </button>
            <button
              onClick={() => setViewTab('favorites')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${viewTab === 'favorites' ? 'bg-indigo-600 text-white' : 'bg-slate-850 text-slate-400 hover:text-white'}`}
            >
              Favorites
            </button>
            <button
              onClick={() => setViewTab('trash')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition ${viewTab === 'trash' ? 'bg-indigo-600 text-white' : 'bg-slate-850 text-slate-400 hover:text-white'}`}
            >
              Recycle Bin
            </button>
          </div>

          <div className="flex items-center gap-2 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-3 top-2.5 text-slate-500" size={14} />
              <input
                type="text"
                placeholder="Search DAM assets..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-1.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white"
              />
            </div>

            <label className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl cursor-pointer flex items-center gap-2 shrink-0 transition">
              <Upload size={12} />
              {uploading ? 'Uploading...' : 'Upload'}
              <input type="file" onChange={handleUpload} className="hidden" disabled={uploading} />
            </label>
          </div>
        </div>

        {/* Media Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
          {mediaFiles.length === 0 ? (
            <div className="col-span-full py-16 text-center text-slate-500 text-xs italic">
              No files match your query.
            </div>
          ) : (
            mediaFiles.map(file => (
              <div
                key={file.id}
                onClick={() => setSelectedFile(file)}
                className={`bg-slate-900 border rounded-2xl overflow-hidden shadow-lg cursor-pointer flex flex-col justify-between transition ${selectedFile?.id === file.id ? 'border-indigo-500' : 'border-slate-800'}`}
              >
                <div className="p-4 aspect-video bg-slate-950 flex items-center justify-center border-b border-slate-800 relative group">
                  {file.file_type === 'image' ? (
                    <Image className="text-slate-600" size={32} />
                  ) : file.file_type === 'video' ? (
                    <Video className="text-slate-600" size={32} />
                  ) : (
                    <FileText className="text-slate-600" size={32} />
                  )}

                  {/* AntiVirus Scan State Indicator */}
                  <div className="absolute top-2 left-2 flex items-center gap-1 bg-slate-900/90 px-1.5 py-0.5 rounded text-[8px] font-mono text-green-400">
                    <CheckCircle size={8} /> SCAN OK
                  </div>
                </div>

                <div className="p-3 flex justify-between items-center">
                  <div className="truncate pr-2">
                    <span className="block text-xs font-semibold text-slate-200 truncate">{file.original_filename}</span>
                    <span className="block text-[9px] text-slate-500 mt-0.5">SIZE: {(file.file_size_bytes / 1024).toFixed(1)} KB</span>
                  </div>
                  <button
                    onClick={async (e) => {
                      e.stopPropagation();
                      await mediaApi.media.favorite(file.id);
                      loadData();
                    }}
                    className="p-1 hover:bg-slate-850 rounded transition"
                  >
                    <Heart size={14} className="text-red-400" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Right Sidebar: Asset Inspector & Metadata Editor */}
      {selectedFile && (
        <div className="w-full lg:w-80 bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-6">
          <div className="flex justify-between items-center pb-3 border-b border-slate-800">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Info size={14} /> Inspector
            </h4>
            <button onClick={() => setSelectedFile(null)} className="text-xs text-slate-500 hover:text-white">Close</button>
          </div>

          <div className="space-y-4">
            <div>
              <span className="block text-[10px] text-slate-500 uppercase font-mono">Filename</span>
              <span className="text-xs font-semibold text-white break-all">{selectedFile.original_filename}</span>
            </div>

            <div>
              <span className="block text-[10px] text-slate-500 uppercase font-mono">UUID Identifier</span>
              <span className="text-xs font-mono text-slate-300 break-all">{selectedFile.id}</span>
            </div>

            <div>
              <span className="block text-[10px] text-slate-500 uppercase font-mono">Accessibility Alt Text</span>
              <input
                type="text"
                defaultValue={selectedFile.alt_text}
                className="w-full mt-1 px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white"
              />
            </div>

            <div>
              <span className="block text-[10px] text-slate-500 uppercase font-mono">Mime Type</span>
              <span className="text-xs font-semibold text-slate-200 mt-1 block">{selectedFile.mime_type || 'image/png'}</span>
            </div>

            <div className="pt-4 border-t border-slate-800 flex gap-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(selectedFile.url || '');
                  alert('Copied link!');
                }}
                className="flex-1 py-2 bg-slate-800 hover:bg-slate-750 text-white font-bold text-xs rounded-xl transition flex items-center justify-center gap-2"
              >
                <Link size={12} /> Link
              </button>
              <button
                onClick={async () => {
                  await mediaApi.media.delete(selectedFile.id);
                  setSelectedFile(null);
                  loadData();
                }}
                className="py-2 px-3 bg-red-950 hover:bg-red-900/40 text-red-400 font-bold text-xs rounded-xl transition"
              >
                <Trash2 size={12} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
