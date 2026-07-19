/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { BookOpen, Play, Calendar, Award, Zap, Bot, ArrowRight, Loader2, Plus, Trash2 } from 'lucide-react';
import { CourseStructure } from '../types';

interface CurriculumViewProps {
  course: CourseStructure;
  structures: CourseStructure[];
  onClose: () => void;
  isAdmin?: boolean;
  onAddNode?: (node: Partial<CourseStructure>) => void;
  onDeleteNode?: (id: string) => void;
  onGenerateSyllabus?: (title: string) => Promise<void>;
  isGenerating?: boolean;
}

export default function CurriculumView({
  course,
  structures,
  onClose,
  isAdmin = false,
  onAddNode,
  onDeleteNode,
  onGenerateSyllabus,
  isGenerating = false
}: CurriculumViewProps) {
  const [activeLessonVideo, setActiveLessonVideo] = useState<string | null>(null);
  const [newNodeTitle, setNewNodeTitle] = useState('');
  const [newNodeType, setNewNodeType] = useState<'MODULE' | 'LESSON' | 'TASK'>('MODULE');
  const [newNodeDesc, setNewNodeDesc] = useState('');
  const [newNodeDuration, setNewNodeDuration] = useState('');
  const [selectedParentId, setSelectedParentId] = useState<string>('');

  // Filter modules/lessons belonging to this course
  const children = structures.filter(s => s.parentId === course.id);
  
  // Find nested children (e.g. lessons in modules)
  const getSubNodes = (parentId: string) => {
    return structures.filter(s => s.parentId === parentId);
  };

  const handleCreateNode = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNodeTitle.trim() || !onAddNode) return;

    onAddNode({
      parentId: selectedParentId || course.id,
      type: newNodeType,
      title: newNodeTitle,
      description: newNodeDesc,
      metadata: newNodeType === 'LESSON' ? { duration: newNodeDuration || '20 Mins' } : undefined
    });

    setNewNodeTitle('');
    setNewNodeDesc('');
    setNewNodeDuration('');
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex justify-end transition-all">
      <div className="w-full max-w-3xl bg-slate-900 border-l border-slate-800 h-full flex flex-col shadow-2xl text-slate-100">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-800 flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-500/15 text-indigo-400 rounded">
                {course.metadata?.difficulty || 'General'} Course
              </span>
              <span className="text-xs text-slate-400">• {course.metadata?.duration || 'Self-paced'}</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-white">{course.title}</h2>
            <p className="text-sm text-slate-400 mt-1">{course.description}</p>
          </div>
          <button 
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Video Player Section */}
        {activeLessonVideo && (
          <div className="bg-black aspect-video w-full relative">
            <video 
              src={activeLessonVideo} 
              className="w-full h-full" 
              controls 
              autoPlay
            />
            <button 
              onClick={() => setActiveLessonVideo(null)}
              className="absolute top-4 right-4 px-3 py-1 bg-slate-900/80 rounded-full text-xs text-white hover:bg-slate-950"
            >
              Close Video
            </button>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* AI Helper Banner */}
          {isAdmin && onGenerateSyllabus && (
            <div className="p-4 bg-gradient-to-r from-indigo-950 via-slate-900 to-indigo-950 border border-indigo-500/20 rounded-xl flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
              <div>
                <h4 className="font-bold text-white flex items-center gap-1.5 text-sm">
                  <Bot className="text-indigo-400" size={16} />
                  Vidya AI Syllabus Generator
                </h4>
                <p className="text-xs text-slate-400 mt-0.5">
                  Autonomously design detailed curriculum schedules, lessons, and modules for this course topic using Google Gemini.
                </p>
              </div>
              <button
                disabled={isGenerating}
                type="button"
                onClick={() => onGenerateSyllabus(course.title)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all shadow-md shrink-0 disabled:opacity-50"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="animate-spin" size={14} />
                    Designing Curriculum...
                  </>
                ) : (
                  <>
                    <Zap size={14} />
                    Generate Outline
                  </>
                )}
              </button>
            </div>
          )}

          {/* Curriculum Index */}
          <div>
            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
              <BookOpen size={18} className="text-indigo-400" />
              Syllabus Outline
            </h3>

            {children.length === 0 ? (
              <div className="p-12 text-center border border-dashed border-slate-800 rounded-xl">
                <p className="text-sm text-slate-400">No syllabus modules defined yet.</p>
                {isAdmin && <p className="text-xs text-slate-500 mt-1">Use the generator above or add a manual node below.</p>}
              </div>
            ) : (
              <div className="space-y-4">
                {children.map(mod => {
                  const subNodes = getSubNodes(mod.id);
                  return (
                    <div key={mod.id} className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest block">Module</span>
                          <h4 className="font-semibold text-white mt-0.5">{mod.title}</h4>
                          <p className="text-xs text-slate-400 mt-0.5">{mod.description}</p>
                        </div>
                        {isAdmin && onDeleteNode && (
                          <button 
                            onClick={() => onDeleteNode(mod.id)}
                            className="p-1.5 hover:bg-red-500/10 text-slate-500 hover:text-red-400 rounded-lg transition-all"
                            title="Delete module"
                          >
                            <Trash2 size={14} />
                          </button>
                        )}
                      </div>

                      {/* Nested Lessons / Tasks */}
                      {subNodes.length > 0 && (
                        <div className="pl-4 border-l-2 border-slate-800 space-y-2.5">
                          {subNodes.map(sub => (
                            <div key={sub.id} className="flex justify-between items-center p-2.5 bg-slate-950/40 rounded-lg border border-slate-900/80">
                              <div className="flex items-center gap-2.5">
                                <span className={`px-2 py-0.5 text-[10px] font-bold rounded ${
                                  sub.type === 'LESSON' ? 'bg-amber-500/10 text-amber-400' : 'bg-emerald-500/10 text-emerald-400'
                                }`}>
                                  {sub.type}
                                </span>
                                <div>
                                  <h5 className="text-xs font-medium text-slate-200">{sub.title}</h5>
                                  <p className="text-[11px] text-slate-400 mt-0.5">{sub.description}</p>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                {sub.type === 'LESSON' && (
                                  <>
                                    <span className="text-[10px] text-slate-400 mr-1">{sub.metadata?.duration || '15 Mins'}</span>
                                    <button
                                      onClick={() => setActiveLessonVideo(sub.metadata?.videoUrl || 'https://www.w3schools.com/html/mov_bbb.mp4')}
                                      className="p-1.5 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-400 hover:text-white rounded-lg transition-all"
                                      title="Play lesson"
                                    >
                                      <Play size={12} fill="currentColor" />
                                    </button>
                                  </>
                                )}
                                {isAdmin && onDeleteNode && (
                                  <button 
                                    onClick={() => onDeleteNode(sub.id)}
                                    className="p-1 text-slate-600 hover:text-red-400 rounded transition-all"
                                  >
                                    <Trash2 size={12} />
                                  </button>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Add Syllabus Item Form (Admins Only) */}
          {isAdmin && onAddNode && (
            <form onSubmit={handleCreateNode} className="p-4 border border-slate-800 rounded-xl bg-slate-950/40 space-y-4">
              <h4 className="font-bold text-white text-sm flex items-center gap-1.5">
                <Plus size={16} className="text-indigo-400" />
                Add Syllabus Component
              </h4>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Node Type</label>
                  <select
                    value={newNodeType}
                    onChange={(e) => setNewNodeType(e.target.value as any)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-indigo-500"
                  >
                    <option value="MODULE">MODULE (Parent Structure)</option>
                    <option value="LESSON">LESSON (Video Block)</option>
                    <option value="TASK">TASK (Assignment Block)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Parent Module</label>
                  <select
                    value={selectedParentId}
                    onChange={(e) => setSelectedParentId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-indigo-500"
                  >
                    <option value="">Course Root (Create module)</option>
                    {children.filter(c => c.type === 'MODULE').map(m => (
                      <option key={m.id} value={m.id}>{m.title}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Component Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Lesson 1.2: Structuring Dynamic Variables"
                  value={newNodeTitle}
                  onChange={(e) => setNewNodeTitle(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Description</label>
                <textarea
                  placeholder="Summarize the instructional goals or requirements."
                  value={newNodeDesc}
                  onChange={(e) => setNewNodeDesc(e.target.value)}
                  rows={2}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-indigo-500 resize-none"
                />
              </div>

              {newNodeType === 'LESSON' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Estimated Duration</label>
                  <input
                    type="text"
                    placeholder="e.g. 25 Mins"
                    value={newNodeDuration}
                    onChange={(e) => setNewNodeDuration(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>
              )}

              <button
                type="submit"
                className="w-full py-2 bg-slate-800 hover:bg-indigo-600 text-white rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5"
              >
                Create Node
              </button>
            </form>
          )}

        </div>
      </div>
    </div>
  );
}
