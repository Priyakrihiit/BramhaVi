/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { VideoStreamAsset } from './types';
import { Play, Pause, Bookmark, FileText, Settings, Sparkles, Plus, Clock, SkipForward } from 'lucide-react';

export const Module7VideoStreaming: React.FC = () => {
  const [videos, setVideos] = useState<VideoStreamAsset[]>([
    {
      id: 'vid-1',
      title: '1. Vedic Mathematics Advanced Sutras',
      description: 'Introductory deep-dive into modular calculations speed tricks and curriculum maps.',
      duration: 1800, // 30 mins
      thumbnailUrl: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&q=80&w=300',
      videoUrl: '#',
      playbackSpeed: 1,
      lastPosition: 120, // 2 mins in, for "Continue Watching"
      bookmarks: [60, 300],
      notes: [
        { id: 'n-1', timestamp: 60, text: 'Core definition of Nikhilam remainder offsets.' },
        { id: 'n-2', timestamp: 300, text: 'Visualizing cross multiplication speed formulas.' }
      ]
    },
    {
      id: 'vid-2',
      title: '2. Multi-Tenant SaaS Routing Logic',
      description: 'Understanding custom subdomain DNS records, database isolations, and Express middleware routing.',
      duration: 2700, // 45 mins
      thumbnailUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=300',
      videoUrl: '#',
      playbackSpeed: 1,
      lastPosition: 0,
      bookmarks: [],
      notes: []
    }
  ]);

  const [activeVidId, setActiveVidId] = useState<string>('vid-1');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(120); // 2:00 mins
  const [quality, setQuality] = useState<'1080p' | '720p' | '480p'>('1080p');
  const [speed, setSpeed] = useState<number>(1);
  const [noteText, setNoteText] = useState('');

  const activeVid = videos.find(v => v.id === activeVidId) || videos[0];

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    setCurrentTime(val);
    setVideos(prev => prev.map(v => v.id === activeVid.id ? { ...v, lastPosition: val } : v));
  };

  const handleAddBookmark = () => {
    if (activeVid.bookmarks.includes(currentTime)) return;
    setVideos(prev => prev.map(v => {
      if (v.id === activeVid.id) {
        return {
          ...v,
          bookmarks: [...v.bookmarks, currentTime].sort((a,b) => a-b)
        };
      }
      return v;
    }));
  };

  const handleAddNote = (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteText.trim()) return;

    const newNote = {
      id: `note-${Date.now()}`,
      timestamp: currentTime,
      text: noteText
    };

    setVideos(prev => prev.map(v => {
      if (v.id === activeVid.id) {
        return {
          ...v,
          notes: [...v.notes, newNote].sort((a,b) => a.timestamp - b.timestamp)
        };
      }
      return v;
    }));
    setNoteText('');
  };

  const handleSpeedChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = parseFloat(e.target.value);
    setSpeed(val);
  };

  return (
    <div id="saas-module-7" className="space-y-6 text-slate-100">
      {/* Banner */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Play className="text-indigo-400 w-5 h-5" />
            Adaptive Video Streaming & Sync Annotation Engine
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Immersive video streaming workspace. Includes dynamic quality shifting, bookmark markers, note logs saved dynamically to player timestamps, and video progress tracking.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left pane: Video Player & progress bar */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-slate-950 border border-slate-900 rounded-2xl overflow-hidden relative">
            {/* Visual Thumbnail or playing screen */}
            <div className="relative h-96 bg-black flex items-center justify-center">
              <img
                src={activeVid.thumbnailUrl}
                alt="Video Cover"
                className="absolute inset-0 w-full h-full object-cover opacity-35"
              />
              
              {/* Play overlays */}
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                className="bg-indigo-600/90 text-white p-5 rounded-full hover:bg-indigo-500 hover:scale-110 transition relative z-10 shadow-lg shadow-indigo-950/50"
              >
                {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8" />}
              </button>

              <div className="absolute top-4 left-4 bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1 text-[10px] text-indigo-400 font-mono flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-indigo-400 animate-spin" /> Adaptive: <strong className="text-white">{quality}</strong>
              </div>
            </div>

            {/* Video Controls bar */}
            <div className="p-4 bg-slate-900/90 border-t border-slate-850 space-y-3">
              {/* Progress track slider */}
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-mono text-slate-400">{formatTime(currentTime)}</span>
                <input
                  type="range"
                  min={0}
                  max={activeVid.duration}
                  value={currentTime}
                  onChange={handleSeek}
                  className="flex-1 accent-indigo-500 h-1 rounded-lg bg-slate-800"
                />
                <span className="text-[10px] font-mono text-slate-400">{formatTime(activeVid.duration)}</span>
              </div>

              {/* Lower button controls row */}
              <div className="flex flex-wrap justify-between items-center gap-2 pt-1">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="bg-slate-800 hover:bg-slate-700 text-white p-2 rounded-lg transition"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={handleAddBookmark}
                    className="bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded-lg text-xs transition flex items-center gap-1"
                  >
                    <Bookmark className="w-3.5 h-3.5 text-indigo-400" /> Mark Timestamp
                  </button>
                </div>

                <div className="flex items-center gap-2 font-mono text-xs">
                  {/* Quality selector */}
                  <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-850 px-2.5 py-1 rounded-lg">
                    <Settings className="w-3.5 h-3.5 text-slate-500" />
                    <select
                      value={quality}
                      onChange={(e: any) => setQuality(e.target.value)}
                      className="bg-transparent border-none text-slate-300 text-[11px] focus:outline-none"
                    >
                      <option value="1080p">1080p (FHD)</option>
                      <option value="720p">720p (HD)</option>
                      <option value="480p">480p (SD)</option>
                    </select>
                  </div>

                  {/* Playback rate */}
                  <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-850 px-2.5 py-1 rounded-lg">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    <select
                      value={speed}
                      onChange={handleSpeedChange}
                      className="bg-transparent border-none text-slate-300 text-[11px] focus:outline-none"
                    >
                      <option value={0.5}>0.5x</option>
                      <option value={1}>1.0x</option>
                      <option value={1.25}>1.25x</option>
                      <option value={1.5}>1.5x</option>
                      <option value={2}>2.0x</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bookmarks bar */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-4 text-left">
            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block mb-2">Bookmarked Timestamps ({activeVid.bookmarks.length})</span>
            <div className="flex flex-wrap gap-1.5">
              {activeVid.bookmarks.map((bTime, i) => (
                <button
                  key={i}
                  onClick={() => setCurrentTime(bTime)}
                  className="bg-indigo-950/30 hover:bg-indigo-950 text-indigo-400 border border-indigo-900/40 text-[10px] px-3 py-1 rounded-lg transition font-mono font-bold flex items-center gap-1"
                >
                  <Clock className="w-3 h-3" /> {formatTime(bTime)}
                </button>
              ))}
              {activeVid.bookmarks.length === 0 && (
                <span className="text-[10px] text-slate-600 font-medium">No bookmarks set. Click "Mark Timestamp" above.</span>
              )}
            </div>
          </div>
        </div>

        {/* Right pane: Playlist & Video notes */}
        <div className="lg:col-span-4 space-y-6 text-left">
          {/* Playlist selection sidebar */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">Video Lecture Playlist</h3>
            <div className="space-y-2">
              {videos.map(v => {
                const isSelected = activeVid.id === v.id;
                const progressPct = Math.min(100, Math.round((v.lastPosition / v.duration) * 100));

                return (
                  <div
                    key={v.id}
                    onClick={() => {
                      setActiveVidId(v.id);
                      setCurrentTime(v.lastPosition);
                    }}
                    className={`p-3 border rounded-xl cursor-pointer transition ${isSelected ? 'bg-indigo-600/10 border-indigo-500 text-indigo-200 font-semibold' : 'hover:bg-slate-900/60 bg-slate-900/20 border-slate-900'}`}
                  >
                    <span className="block text-xs font-bold text-slate-200">{v.title}</span>
                    <span className="block text-[10px] text-slate-500 mt-1">{formatTime(v.duration)} Total Duration</span>
                    {/* Progress track bar */}
                    {progressPct > 0 && (
                      <div className="mt-2 text-left">
                        <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                          <div style={{ width: `${progressPct}%` }} className="h-full bg-indigo-500"></div>
                        </div>
                        <span className="text-[9px] text-slate-500 font-mono mt-0.5 block">Continue Watching ({progressPct}% done)</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sync Notebook Widget */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 flex flex-col justify-between h-[300px]">
            <div>
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-indigo-400" />
                Syllabus Sync Notebook
              </h3>
              
              <div className="space-y-2.5 max-h-[140px] overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-slate-800">
                {activeVid.notes.map(note => (
                  <div key={note.id} className="text-xs bg-slate-900/60 p-2.5 rounded-lg border border-slate-850/60">
                    <button
                      onClick={() => setCurrentTime(note.timestamp)}
                      className="text-[9px] text-indigo-400 font-mono font-bold bg-indigo-500/10 px-1.5 py-0.5 rounded-md hover:underline inline-block mb-1 cursor-pointer"
                    >
                      📌 {formatTime(note.timestamp)}
                    </button>
                    <p className="text-slate-300 leading-relaxed">{note.text}</p>
                  </div>
                ))}
                {activeVid.notes.length === 0 && (
                  <p className="text-[10px] text-slate-600">No synchronized annotations logged yet.</p>
                )}
              </div>
            </div>

            <form onSubmit={handleAddNote} className="flex gap-1 border-t border-slate-900 pt-2.5">
              <input
                type="text"
                required
                placeholder="Write study note synced to time..."
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-850 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500 placeholder-slate-600"
              />
              <button type="submit" className="bg-indigo-600 hover:bg-indigo-500 text-white p-1.5 rounded-lg transition">
                <Plus className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Module7VideoStreaming;
