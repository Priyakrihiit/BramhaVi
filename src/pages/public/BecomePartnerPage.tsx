/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useLayoutStore } from '../../stores/layoutStore';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';
import { Input, Button, Checkbox } from '../../components/DesignSystem';
import { Award, BookOpen, Briefcase, ChevronRight, ShieldCheck, Mail } from 'lucide-react';

export const BecomePartnerPage: React.FC = () => {
  const { currentPath, navigateTo } = useLayoutStore();
  const { currentUser } = useAuthStore();
  
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  // Form Fields
  const [resumeUrl, setResumeUrl] = useState('');
  const [experience, setExperience] = useState('');
  const [interests, setInterests] = useState('');
  
  const [authorBio, setAuthorBio] = useState('');
  const [genre, setGenre] = useState('Computer Science');
  
  const [svcCategory, setSvcCategory] = useState('Web Development');
  const [svcBio, setSvcBio] = useState('');
  const [estimatedPrice, setEstimatedPrice] = useState(5000);

  const isTeacher = currentPath === '/become-teacher';
  const isAuthor = currentPath === '/become-author';
  const isProvider = currentPath === '/become-provider';

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      alert('Authentication required to submit capability requests. Redirecting to login desk...');
      navigateTo('/auth');
      return;
    }
    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const code = isTeacher ? 'TEACHING' : isAuthor ? 'AUTHORING' : 'SERVICES';
      const applicationData = isTeacher 
        ? { resume_url: resumeUrl, experience_summary: experience, subjects_requested: interests }
        : isAuthor 
          ? { biography: authorBio, genre_interests: genre }
          : { category: svcCategory, bio: svcBio, pricing_model: 'FIXED', price: estimatedPrice };

      const res = await api.capabilities.request(code, applicationData);
      if (res.success) {
        setSuccess('Application submitted successfully! Our administrators will audit and review your credentials.');
      } else {
        setError(res.message || 'Capability request failed. Please check active application history.');
      }
    } catch (err) {
      setError('Connection failed. Verify server authorization token headers.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-[#070b19] py-16 px-6">
      <div className="max-w-xl mx-auto w-full text-left space-y-6">
        
        {/* Header branding */}
        <div className="space-y-2 border-b border-indigo-950/40 pb-5">
          <div className="p-3 bg-indigo-950/50 text-indigo-400 rounded-xl w-fit">
            {isTeacher && <BookOpen size={20} />}
            {isAuthor && <Award size={20} />}
            {isProvider && <Briefcase size={20} />}
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight mt-1">
            {isTeacher && 'Become a Certified Teacher'}
            {isAuthor && 'Register as a Platform Author'}
            {isProvider && 'List as Freelance Service Provider'}
          </h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            {isTeacher && 'Publish curriculum outline trees, stream video lectures, and proctor quizzes.'}
            {isAuthor && 'Self-publish ebooks, compile print editions, and monitor royalty payouts.'}
            {isProvider && 'Consult clients, create milestone projects, and settle payments in your ledger.'}
          </p>
        </div>

        {/* Messaging banners */}
        {error && (
          <div className="p-3.5 bg-rose-950/40 border border-rose-900/50 text-xs text-rose-350 font-medium rounded-xl">
            {error}
          </div>
        )}
        {success && (
          <div className="p-4 bg-emerald-950/40 border border-emerald-900 text-xs text-emerald-350 font-medium rounded-xl text-center space-y-2">
            <ShieldCheck size={20} className="mx-auto text-emerald-400 animate-pulse" />
            <p>{success}</p>
            <Button size="sm" variant="outline" className="text-[10px]" onClick={() => navigateTo('/')}>
              Return Home
            </Button>
          </div>
        )}

        {!success && (
          <form onSubmit={handleApply} className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 shadow-xl">
            
            {/* Common Auth Check */}
            {!currentUser && (
              <div className="p-3 bg-amber-950/20 border border-amber-900/40 text-[11px] text-amber-450 rounded-xl flex items-start gap-2 mb-2 leading-relaxed">
                <span>⚠️ Note: You must be authenticated to associate capabilities. Clicking submit will prompt register options.</span>
              </div>
            )}

            {/* Teacher Form Fields */}
            {isTeacher && (
              <React.Fragment>
                <Input 
                  label="Resume / Portfolio URL" 
                  type="url" 
                  placeholder="https://yourprofile.com/resume.pdf" 
                  required 
                  value={resumeUrl}
                  onChange={(e) => setResumeUrl(e.target.value)}
                />
                <div className="flex flex-col gap-1.5 w-full">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Experience Summary</label>
                  <textarea
                    required
                    placeholder="Summarize your academic history and tutoring experience..."
                    value={experience}
                    onChange={(e) => setExperience(e.target.value)}
                    className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-3 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200 min-h-[90px]"
                  />
                </div>
                <Input 
                  label="Subject Areas (Comma Separated)" 
                  type="text" 
                  placeholder="Vedic Math, Physics, Data Structures" 
                  required 
                  value={interests}
                  onChange={(e) => setInterests(e.target.value)}
                />
              </React.Fragment>
            )}

            {/* Author Form Fields */}
            {isAuthor && (
              <React.Fragment>
                <div className="flex flex-col gap-1.5 w-full">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Author Biography</label>
                  <textarea
                    required
                    placeholder="Provide a bio for your bookstore public profile..."
                    value={authorBio}
                    onChange={(e) => setAuthorBio(e.target.value)}
                    className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-3 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200 min-h-[90px]"
                  />
                </div>
                <div className="flex flex-col gap-1.5 text-left w-full">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Preferred Genre</label>
                  <select 
                    value={genre}
                    onChange={(e) => setGenre(e.target.value)}
                    className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl py-2.5 px-3 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200"
                  >
                    <option value="Computer Science">Computer Science & Programming</option>
                    <option value="Mathematics">Vedic Mathematics</option>
                    <option value="Biology">NEET Preparatory Material</option>
                    <option value="Physics">Advanced Physics Modules</option>
                  </select>
                </div>
              </React.Fragment>
            )}

            {/* Service Provider Form Fields */}
            {isProvider && (
              <React.Fragment>
                <div className="flex flex-col gap-1.5 text-left w-full">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Service Category</label>
                  <select 
                    value={svcCategory}
                    onChange={(e) => setSvcCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl py-2.5 px-3 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200"
                  >
                    <option value="Web Development">Full-Stack Web Development</option>
                    <option value="Mobile App Development">Mobile App Development (Flutter)</option>
                    <option value="UI UX">UI/UX Interface Design</option>
                    <option value="SEO">SEO Page Optimization</option>
                    <option value="AI Automation">AI Agents & Workflow Automations</option>
                  </select>
                </div>
                <div className="flex flex-col gap-1.5 w-full">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Provider Bio</label>
                  <textarea
                    required
                    placeholder="Explain your client service capabilities, tech stack, and deliverable standards..."
                    value={svcBio}
                    onChange={(e) => setSvcBio(e.target.value)}
                    className="w-full bg-slate-950 border border-indigo-950/80 rounded-xl p-3 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200 min-h-[90px]"
                  />
                </div>
                <div className="flex flex-col gap-1 text-xs">
                  <div className="flex justify-between font-bold text-slate-400 uppercase tracking-wider text-[9px]">
                    <span>Estimated Baseline Price</span>
                    <span className="text-indigo-400 font-mono">₹{estimatedPrice.toLocaleString()}</span>
                  </div>
                  <input
                    type="range"
                    min={1000}
                    max={150000}
                    step={1000}
                    value={estimatedPrice}
                    onChange={(e) => setEstimatedPrice(Number(e.target.value))}
                    className="w-full h-1.5 rounded-lg bg-indigo-950 appearance-none cursor-pointer accent-indigo-600 mt-2"
                  />
                </div>
              </React.Fragment>
            )}

            <Button type="submit" isLoading={submitting} className="w-full mt-2">
              Submit Capability Request
            </Button>
          </form>
        )}

      </div>
    </div>
  );
};

export default BecomePartnerPage;
