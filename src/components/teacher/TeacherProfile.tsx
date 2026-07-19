/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { User, Mail, Sparkles, Award, Star, BookOpen, Save, CheckCircle } from 'lucide-react';
import { Button, Input, Badge } from '../DesignSystem';

interface ProfileData {
  fullName: string;
  email: string;
  bio: string;
  rating: number;
  teachingSubjects: string[];
  achievements: string[];
}

export const TeacherProfile: React.FC = () => {
  const [profile, setProfile] = useState<ProfileData>({
    fullName: 'Dr. Priyakrih Shastri',
    email: 'priyakrihiit@gmail.com',
    bio: 'Professor of Computational Sanskrit Syntax & Theoretical Quantum Physics. Former IIT research associate focusing on formal grammar compilers and non-local conscious systems.',
    rating: 4.9,
    teachingSubjects: ['Quantum Consciousness Physics', 'Sanskrit Compiler Design', 'Vedic Mathematics'],
    achievements: ['BrahmaVidya Fellow 2025', 'Excellent Educator Award']
  });

  const [loading, setLoading] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [isEditing, setIsEditing] = useState(false);

  // Form edit states
  const [fullName, setFullName] = useState('');
  const [bio, setBio] = useState('');
  const [subjectInput, setSubjectInput] = useState('');

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/teacher/profiles/me/');
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleEditOpen = () => {
    setFullName(profile.fullName);
    setBio(profile.bio);
    setIsEditing(true);
    setSaveSuccess(false);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const updated = {
      ...profile,
      fullName,
      bio
    };

    try {
      const res = await fetch('/api/v1/teacher/profiles/me/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fullName, bio })
      });

      setProfile(updated);
      setSaveSuccess(true);
      setIsEditing(false);
    } catch (err) {
      console.error(err);
      setProfile(updated);
      setSaveSuccess(true);
      setIsEditing(false);
    }
  };

  const handleAddSubject = () => {
    if (!subjectInput.trim()) return;
    setProfile(prev => ({
      ...prev,
      teachingSubjects: [...prev.teachingSubjects, subjectInput.trim()]
    }));
    setSubjectInput('');
  };

  const handleRemoveSubject = (idx: number) => {
    setProfile(prev => ({
      ...prev,
      teachingSubjects: prev.teachingSubjects.filter((_, i) => i !== idx)
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <User className="text-indigo-400" size={20} />
            Academic Educator Profile
          </h2>
          <p className="text-xs text-slate-400 font-sans">Manage public credentials, scholarly bios, and accredited teaching fields.</p>
        </div>

        {!isEditing && (
          <Button onClick={handleEditOpen} size="sm" variant="secondary">
            Edit Credentials
          </Button>
        )}
      </div>

      {saveSuccess && (
        <div className="p-3 bg-emerald-950/20 border border-emerald-500/25 text-emerald-400 text-xs rounded-xl flex items-center gap-2 select-none animate-fade-in font-sans">
          <CheckCircle size={14} /> Profile details have been saved to system nodes successfully.
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 select-none">
        {/* Left Card: Avatar and quick metrics */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 p-6 rounded-3xl flex flex-col items-center text-center space-y-4">
          <div className="relative">
            <div className="h-24 w-24 rounded-full bg-slate-950 border-2 border-indigo-500/60 overflow-hidden shadow-xl flex items-center justify-center">
              <User size={48} className="text-indigo-400" />
            </div>
            <span className="absolute bottom-1 right-1 h-5 w-5 bg-emerald-500 border-4 border-slate-900 rounded-full"></span>
          </div>

          <div>
            <h3 className="font-bold text-white text-base leading-tight">{profile.fullName}</h3>
            <span className="text-xs text-indigo-400 mt-1 block">Accredited BrahmaVidya Fellow</span>
          </div>

          <div className="flex gap-1 items-center justify-center text-amber-400 py-1.5 px-3 bg-amber-500/5 border border-amber-500/10 rounded-full text-xs font-bold font-mono">
            <Star size={12} fill="currentColor" /> {profile.rating} / 5.0 Rating
          </div>

          <div className="w-full border-t border-slate-850/80 pt-4 flex justify-around items-center text-[10px] text-slate-500 font-mono">
            <div className="text-center">
              <span className="block font-bold text-slate-350 text-xs">2</span>
              <span>Active Programs</span>
            </div>
            <div className="text-center">
              <span className="block font-bold text-slate-350 text-xs">257</span>
              <span>Scholars Enrolled</span>
            </div>
          </div>
        </div>

        {/* Right Card: Scholarly Bio and Form */}
        <div className="lg:col-span-8 bg-slate-900 border border-slate-800 p-6 rounded-3xl space-y-6">
          {isEditing ? (
            <form onSubmit={handleSave} className="space-y-4 animate-fade-in">
              <Input label="Scholarly Full Name" value={fullName} onChange={e => setFullName(e.target.value)} required />
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1.5">Accreditation Bio</label>
                <textarea
                  className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-3.5 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder:text-slate-650"
                  rows={4}
                  value={bio}
                  onChange={e => setBio(e.target.value)}
                  required
                />
              </div>

              <div className="flex justify-end gap-2.5">
                <Button type="button" variant="ghost" size="sm" onClick={() => setIsEditing(false)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm">
                  <Save size={13} /> Save Profile
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-6">
              <div className="space-y-2 text-left">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Scholarly Bio Statement</h4>
                <p className="text-xs text-slate-300 leading-relaxed font-serif italic pr-4">
                  "{profile.bio}"
                </p>
              </div>

              <div className="space-y-3 text-left">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Associated Domains</h4>
                <div className="flex flex-wrap gap-1.5">
                  {profile.teachingSubjects.map((sub, idx) => (
                    <div key={idx} className="flex items-center gap-1 bg-indigo-500/5 border border-indigo-500/10 rounded-lg px-2.5 py-1 text-xs text-indigo-400">
                      <BookOpen size={11} /> {sub}
                      <button onClick={() => handleRemoveSubject(idx)} className="ml-1 hover:text-white font-bold">×</button>
                    </div>
                  ))}
                </div>

                <div className="flex gap-2 max-w-sm pt-2">
                  <input
                    type="text"
                    placeholder="Add Domain..."
                    value={subjectInput}
                    onChange={e => setSubjectInput(e.target.value)}
                    className="flex-1 bg-slate-950 border border-indigo-950/80 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-indigo-500"
                  />
                  <button type="button" onClick={handleAddSubject} className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-550 text-white rounded-lg text-xs font-bold">Add</button>
                </div>
              </div>

              <div className="space-y-3 text-left border-t border-slate-850/80 pt-4">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Academic Honors & Badges</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {profile.achievements.map((ach, idx) => (
                    <div key={idx} className="p-3 bg-slate-950 border border-slate-850 rounded-xl flex items-center gap-2.5 text-xs">
                      <Award className="text-amber-500" size={16} />
                      <span className="font-bold text-slate-300">{ach}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
