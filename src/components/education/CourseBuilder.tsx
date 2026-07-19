/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { Button, Input, Textarea, Select, Checkbox, Badge } from '../DesignSystem';
import { Layers, Plus, Trash2, Video, FileText, HelpCircle, Award, Settings, ShieldCheck } from 'lucide-react';

export const CourseBuilder: React.FC = () => {
  const [activeBuilderTab, setActiveBuilderTab] = useState<'curriculum' | 'pricing' | 'seo'>('curriculum');
  
  // Dynamic hierarchical outline state
  const [outline, setOutline] = useState([
    { id: '1', type: 'MODULE', title: 'Module 1: Vedic Math Multiplications', parentId: null },
    { id: '2', type: 'CHAPTER', title: 'Chapter 1.1: Multiply via Ekadhikena', parentId: '1' },
    { id: '3', type: 'LESSON', title: 'Lesson 1.1.1: Basic Principles', parentId: '2', lessonType: 'text', content: 'Vedic math principles utilize...' }
  ]);

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>('3');

  // Input states
  const [nodeTitle, setNodeTitle] = useState('');
  const [nodeType, setNodeType] = useState<'MODULE' | 'CHAPTER' | 'LESSON'>('MODULE');
  const [lessonType, setLessonType] = useState('text');
  const [richText, setRichText] = useState('');

  const handleAddNode = () => {
    if (!nodeTitle.trim()) return;
    const parentId = nodeType === 'MODULE' ? null : (selectedNodeId || '1');
    const newId = Math.random().toString(36).substring(2, 9);
    
    setOutline(prev => [
      ...prev,
      { id: newId, type: nodeType, title: nodeTitle, parentId, lessonType, content: richText }
    ]);
    
    setNodeTitle('');
    setRichText('');
    alert('Curriculum outline node appended successfully.');
  };

  const selectedNode = outline.find(n => n.id === selectedNodeId);

  return (
    <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6 text-left">
      
      {/* Header bar */}
      <div className="flex justify-between items-center border-b border-indigo-950/45 pb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-1.5 uppercase tracking-wider">
            <Layers size={16} className="text-indigo-400" /> Syllabus Course Builder
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Design program segments, modules, video/written lectures, and quizzes.</p>
        </div>

        {/* Builder tabs */}
        <div className="flex gap-2 text-xs font-mono select-none">
          <button onClick={() => setActiveBuilderTab('curriculum')} className={`px-3 py-1 rounded-lg border ${activeBuilderTab === 'curriculum' ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'border-indigo-950 text-slate-500 hover:text-slate-300'}`}>Curriculum</button>
          <button onClick={() => setActiveBuilderTab('pricing')} className={`px-3 py-1 rounded-lg border ${activeBuilderTab === 'pricing' ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'border-indigo-950 text-slate-500 hover:text-slate-300'}`}>Pricing</button>
          <button onClick={() => setActiveBuilderTab('seo')} className={`px-3 py-1 rounded-lg border ${activeBuilderTab === 'seo' ? 'bg-indigo-650 border-indigo-500 text-white font-bold' : 'border-indigo-950 text-slate-500 hover:text-slate-300'}`}>SEO</button>
        </div>
      </div>

      {/* CURRICULUM SCHEMA TREE EDITOR */}
      {activeBuilderTab === 'curriculum' && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          
          {/* Outline Sidebar Tree list */}
          <div className="md:col-span-5 space-y-4 border-r border-indigo-950/45 pr-4">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Syllabus Outline Nodes</h4>
            <div className="space-y-2">
              {outline.map(n => (
                <button
                  key={n.id}
                  onClick={() => setSelectedNodeId(n.id)}
                  className={`w-full text-left p-3 rounded-xl border transition flex items-center justify-between text-xs ${selectedNodeId === n.id ? 'bg-indigo-950/20 border-indigo-500 text-indigo-300 font-bold' : 'bg-slate-950 border-indigo-950/80 text-slate-400 hover:bg-slate-900/60'}`}
                >
                  <span className="truncate pr-2 flex items-center gap-1.5">
                    {n.type === 'LESSON' && <Video size={13} className="text-indigo-400 shrink-0" />}
                    {n.type !== 'LESSON' && <Layers size={13} className="text-indigo-400 shrink-0" />}
                    {n.title}
                  </span>
                  <Badge variant="primary" className="text-[8px]">{n.type}</Badge>
                </button>
              ))}
            </div>

            {/* Quick Appender */}
            <div className="p-4 bg-slate-950 rounded-xl space-y-3">
              <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wider block">Add Outline Node</span>
              <Input placeholder="Node Title" value={nodeTitle} onChange={(e) => setNodeTitle(e.target.value)} />
              <div className="grid grid-cols-2 gap-2 text-xs">
                <Select value={nodeType} onChange={(e: any) => setNodeType(e.target.value)}>
                  <option value="MODULE">MODULE</option>
                  <option value="CHAPTER">CHAPTER</option>
                  <option value="LESSON">LESSON</option>
                </Select>
                <Button size="sm" onClick={handleAddNode}>Append</Button>
              </div>
            </div>
          </div>

          {/* Outline Selected Node Editor details */}
          <div className="md:col-span-7 space-y-6">
            {selectedNode ? (
              <div className="space-y-4">
                <div className="border-b border-indigo-950/45 pb-3">
                  <span className="text-[9px] uppercase font-bold text-indigo-400 font-mono">Editing outlines node</span>
                  <h4 className="text-base font-bold text-white mt-1">{selectedNode.title}</h4>
                </div>

                {selectedNode.type === 'LESSON' ? (
                  <div className="space-y-4">
                    <Select label="Lesson Type" value={lessonType} onChange={(e) => setLessonType(e.target.value)}>
                      <option value="text">Written Article Lesson</option>
                      <option value="video">Lectures Video Upload</option>
                      <option value="mixed">Mixed Assets (Text + PDF + Video)</option>
                    </Select>

                    {lessonType === 'text' && (
                      <Textarea 
                        label="Rich Text Content Editor" 
                        placeholder="Write detailed written guidelines, calculations, or explanations..." 
                        value={richText} 
                        onChange={(e) => setRichText(e.target.value)} 
                      />
                    )}

                    {lessonType === 'video' && (
                      <div className="p-5 bg-slate-950 border border-indigo-950 rounded-xl space-y-3">
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Video Asset Upload</span>
                        <Input type="url" placeholder="https://youtube.com/embed/lesson-id" label="Video URL" />
                        <Input placeholder="Upload Thumbnail URL" type="url" />
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-xs text-slate-450 italic">Modular node selected. Attach chapter sub-lessons or quizzes to this item.</p>
                )}
              </div>
            ) : (
              <div className="text-center py-10 text-slate-500 text-xs italic">Select a node from the sidebar list to configure outline structures.</div>
            )}
          </div>

        </div>
      )}

      {/* PRICING PLANS CONFIGS */}
      {activeBuilderTab === 'pricing' && (
        <div className="max-w-xl space-y-4">
          <Select label="Pricing Strategy Strategy">
            <option value="free">Free Academic Course</option>
            <option value="paid">Paid Accreditation Syllabus</option>
          </Select>
          <Input label="Accreditation Retail Fee (INR)" type="number" placeholder="₹4,999" />
          <Checkbox label="Allow eBook compile version purchase on bookstore" />
        </div>
      )}

      {/* SEO META CONFIGS */}
      {activeBuilderTab === 'seo' && (
        <div className="max-w-xl space-y-4">
          <Input label="SEO Focus Keyword" placeholder="Vedic math multiplications" />
          <Textarea label="Google Snippet Meta Description" placeholder="Learn dynamic Vedic mental calculation shortcuts..." />
        </div>
      )}

    </div>
  );
};

export default CourseBuilder;
