/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useLayoutStore } from '../../stores/layoutStore';
import { CourseStructure, Book, Blog, Tutorial, Product, SystemSettings } from '../../types';
import { Button, SkeletonCard, LoadingSpinner } from '../../components/DesignSystem';
import { 
  Sparkles, ArrowRight, Search, Star, BookOpen, ShoppingBag, 
  Layers, MessageSquare, Briefcase, Award, ShieldCheck, CheckCircle2, ChevronRight 
} from 'lucide-react';

import { useAuthStore } from '../../stores/authStore';

export const HomeShell: React.FC = () => {
  const { navigateTo } = useLayoutStore();
  const { currentUser } = useAuthStore();
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  
  // Dynamic API states
  const [courses, setCourses] = useState<CourseStructure[]>([]);
  const [books, setBooks] = useState<Book[]>([]);
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [tutorials, setTutorials] = useState<Tutorial[]>([]);
  const [services, setServices] = useState<Product[]>([]);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.settings.get(),
      api.courses.list(),
      api.books.list(),
      api.blogs.list({ limit: 3 }),
      api.tutorials.list({ limit: 3 }),
      api.marketplace.listProducts({ type: 'SERVICE' })
    ])
      .then(([settingsRes, coursesRes, booksRes, blogsRes, tutorialsRes, servicesRes]) => {
        if (settingsRes.success && settingsRes.data) setSettings(settingsRes.data);
        if (coursesRes.success && coursesRes.data) setCourses(coursesRes.data.slice(0, 3));
        if (booksRes.success && booksRes.data) setBooks(booksRes.data.slice(0, 3));
        if (blogsRes.success && blogsRes.data) setBlogs(blogsRes.data);
        if (tutorialsRes.success && tutorialsRes.data) setTutorials(tutorialsRes.data);
        if (servicesRes.success && servicesRes.data) setServices(servicesRes.data.slice(0, 3));
      })
      .catch(err => console.error('Failed to load landing home modules:', err))
      .finally(() => setLoading(false));
  }, []);

  const handleGlobalSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigateTo(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const categories = [
    { name: 'Vedic Math', desc: 'Ancient calculation shortcuts.', count: '145 topics', icon: BookOpen, color: 'from-amber-500/20 to-amber-600/5 text-amber-400' },
    { name: 'SaaS Architecture', desc: 'Relational partitions & queues.', count: '89 topics', icon: Layers, color: 'from-indigo-500/20 to-indigo-600/5 text-indigo-400' },
    { name: 'NEET Practice', desc: 'Proctored biology & anatomy checks.', count: '210 topics', icon: Sparkles, color: 'from-emerald-500/20 to-emerald-600/5 text-emerald-400' },
    { name: 'JEE Prep', desc: 'Advanced math & physics nodes.', count: '178 topics', icon: Award, color: 'from-purple-500/20 to-purple-600/5 text-purple-400' },
  ];

  if (loading) {
    return <LoadingSpinner text="Assembling dynamic landing blocks..." />;
  }

  return (
    <div id="bvg-home-shell" className="flex flex-col bg-[#070b19]">
      
      {/* Dynamic Visitor Onboarding Banner */}
      {!currentUser && (
        <div className="bg-gradient-to-r from-indigo-900 via-indigo-950 to-purple-950 border-b border-indigo-500/20 py-3 px-6 text-center text-xs flex flex-wrap items-center justify-center gap-4 text-slate-200">
          <span className="flex items-center gap-1.5 font-medium">
            <Sparkles size={14} className="text-amber-400 animate-pulse shrink-0" />
            New to BrahmaVidya Galaxy? Unlock 15+ Capabilities with one account.
          </span>
          <div className="flex gap-2">
            <button onClick={() => navigateTo('/auth')} className="bg-indigo-600 hover:bg-indigo-550 text-white font-bold px-3 py-1 rounded-lg transition text-[11px] shadow-md shadow-indigo-600/10">
              Get Started
            </button>
            <button onClick={() => navigateTo('/pricing')} className="bg-slate-900 border border-indigo-950 text-slate-350 hover:text-white px-3 py-1 rounded-lg transition text-[11px]">
              Learn Pricing
            </button>
          </div>
        </div>
      )}
      
      {/* 1. HERO SECTION */}
      <section className="relative py-24 md:py-32 px-8 overflow-hidden text-left border-b border-indigo-950/40">
        <div className="absolute top-1/4 left-1/4 w-[400px] h-[400px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none animate-pulse"></div>
        <div className="absolute bottom-10 right-10 w-[300px] h-[300px] bg-amber-500/5 rounded-full blur-[90px] pointer-events-none"></div>
        
        <div className="max-w-5xl mx-auto space-y-6 relative z-10">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 rounded-full text-[10px] font-bold uppercase tracking-wider">
            <Sparkles size={11} className="animate-pulse" />
            Dynamic Enterprise Academic Network
          </span>
          
          <h1 className="text-4xl md:text-6xl font-black text-white leading-tight tracking-tight">
            One Single Platform. <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-amber-300">
              Infinite Capabilities.
            </span>
          </h1>
          
          <p className="text-sm md:text-base text-slate-400 max-w-xl leading-relaxed">
            {settings?.platformDescription || 'BrahmaVidya Galaxy is an AI-powered enterprise knowledge ecosystem where you can learn courses, publish ebooks, build portfolios, provide client services, and verify credentials.'}
          </p>

          {/* Interactive Search Bar */}
          <form onSubmit={handleGlobalSearch} className="flex flex-col sm:flex-row gap-3 max-w-lg pt-4">
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-3.5 text-slate-500" size={16} />
              <input
                type="text"
                placeholder="Search across courses, books, services..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900 border border-indigo-950 rounded-xl py-3 pl-11 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-350"
              />
            </div>
            <Button type="submit" variant="primary" className="py-3">
              Explore Galaxy
            </Button>
          </form>
        </div>
      </section>

      {/* 2. STATS SECTION */}
      <section className="bg-slate-950 border-b border-indigo-950/20 py-12 px-6">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="p-5 bg-slate-900/40 border border-indigo-950 rounded-2xl text-left relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-indigo-500/5 rounded-full blur-xl"></div>
            <span className="block text-3xl font-extrabold text-white">100K+</span>
            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mt-1 block">Tutorials Published</span>
          </div>
          <div className="p-5 bg-slate-900/40 border border-indigo-950 rounded-2xl text-left relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-indigo-500/5 rounded-full blur-xl"></div>
            <span className="block text-3xl font-extrabold text-white">50K+</span>
            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mt-1 block">Active Learners</span>
          </div>
          <div className="p-5 bg-slate-900/40 border border-indigo-950 rounded-2xl text-left relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-indigo-500/5 rounded-full blur-xl"></div>
            <span className="block text-3xl font-extrabold text-white">25K+</span>
            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mt-1 block">Ledger Certificates</span>
          </div>
          <div className="p-5 bg-slate-900/40 border border-indigo-950 rounded-2xl text-left relative overflow-hidden">
            <div className="absolute top-0 right-0 w-20 h-20 bg-indigo-500/5 rounded-full blur-xl"></div>
            <span className="block text-3xl font-extrabold text-white">15+</span>
            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mt-1 block">User Capabilities</span>
          </div>
        </div>
      </section>

      {/* 3. CATEGORIES SECTION */}
      <section className="py-20 px-8 max-w-5xl mx-auto w-full text-left">
        <div className="mb-10">
          <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 font-mono">Academic Segments</span>
          <h2 className="text-2xl font-black text-white tracking-tight mt-1">Browse Syllabus Trees</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {categories.map((cat, idx) => {
            const Icon = cat.icon;
            return (
              <div 
                key={idx}
                onClick={() => navigateTo('/courses')}
                className={`p-5 rounded-2xl border border-indigo-950/60 bg-gradient-to-br ${cat.color} cursor-pointer hover:-translate-y-1 transition duration-200 text-left space-y-3 relative overflow-hidden group`}
              >
                <div className="p-3 bg-slate-950/45 rounded-xl w-fit border border-indigo-900/30">
                  <Icon size={18} />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-white group-hover:text-indigo-300 transition">{cat.name}</h4>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">{cat.desc}</p>
                </div>
                <div className="flex items-center justify-between pt-1 text-[10px] text-slate-500 font-mono">
                  <span>{cat.count}</span>
                  <ChevronRight size={12} className="group-hover:translate-x-0.5 transition" />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* 4. FEATURED PRODUCTS & SERVICES (GRID MAPPING) */}
      <section className="py-20 px-8 bg-slate-950 border-t border-indigo-950/30 text-left">
        <div className="max-w-5xl mx-auto space-y-16">
          
          {/* Courses Segment */}
          <div className="space-y-6">
            <div className="flex justify-between items-end">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 font-mono">Top Syllabus Outlines</span>
                <h3 className="text-xl font-bold text-white tracking-tight mt-0.5">Featured Learning Programs</h3>
              </div>
              <Button size="sm" variant="outline" onClick={() => navigateTo('/courses')}>
                See All
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {courses.map((course, idx) => (
                <div key={course.id || idx} className="bg-slate-900 border border-indigo-950 rounded-2xl overflow-hidden hover:border-indigo-900 transition flex flex-col justify-between">
                  <div className="p-5 space-y-3">
                    <span className="text-[9px] font-bold bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded uppercase tracking-wider">
                      {course.nodeType}
                    </span>
                    <h4 className="text-sm font-bold text-white leading-snug">{course.title}</h4>
                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{course.description || 'Access structured study nodes and verify learning checkpoints.'}</p>
                  </div>
                  <div className="p-4 border-t border-indigo-950/40 flex justify-between items-center">
                    <span className="text-[10px] text-slate-500 font-mono">Academic Node</span>
                    <button 
                      onClick={() => navigateTo(`/courses/${course.id}`)}
                      className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition"
                    >
                      Learn Syllabus <ChevronRight size={13} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bookstore Segment */}
          <div className="space-y-6">
            <div className="flex justify-between items-end">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-widest text-amber-500 font-mono">Popular Ebooks</span>
                <h3 className="text-xl font-bold text-white tracking-tight mt-0.5">Academic Bookstore</h3>
              </div>
              <Button size="sm" variant="outline" onClick={() => navigateTo('/bookstore')}>
                Library
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {books.map((book, idx) => (
                <div key={book.id || idx} className="bg-slate-900 border border-indigo-950 rounded-2xl overflow-hidden hover:border-indigo-900 transition flex flex-col justify-between">
                  <div className="p-5 space-y-3">
                    <span className="text-[9px] font-bold bg-amber-950/40 text-amber-400 font-mono px-2 py-0.5 rounded uppercase tracking-wider">
                      {book.bookType}
                    </span>
                    <h4 className="text-sm font-bold text-white leading-snug">{book.title}</h4>
                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{book.description}</p>
                  </div>
                  <div className="p-4 border-t border-indigo-950/40 flex justify-between items-center bg-slate-900/60">
                    <span className="text-xs font-bold text-white">₹{book.price.toLocaleString()}</span>
                    <button 
                      onClick={() => navigateTo('/bookstore')}
                      className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition"
                    >
                      Preview <ChevronRight size={13} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Freelance Services Segment */}
          <div className="space-y-6">
            <div className="flex justify-between items-end">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-widest text-emerald-500 font-mono">Consulting & Dev</span>
                <h3 className="text-xl font-bold text-white tracking-tight mt-0.5">Professional Agency Services</h3>
              </div>
              <Button size="sm" variant="outline" onClick={() => navigateTo('/marketplace')}>
                Request Quote
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {services.map((svc, idx) => (
                <div key={svc.id || idx} className="bg-slate-900 border border-indigo-950 rounded-2xl overflow-hidden hover:border-indigo-900 transition flex flex-col justify-between">
                  <div className="p-5 space-y-3">
                    <span className="text-[9px] font-bold bg-emerald-950/40 text-emerald-400 font-mono px-2 py-0.5 rounded uppercase tracking-wider">
                      Services
                    </span>
                    <h4 className="text-sm font-bold text-white leading-snug">{svc.name}</h4>
                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{svc.description}</p>
                  </div>
                  <div className="p-4 border-t border-indigo-950/40 flex justify-between items-center bg-slate-900/60">
                    <span className="text-xs font-bold text-emerald-400">Est: ₹{svc.price.toLocaleString()}</span>
                    <button 
                      onClick={() => navigateTo('/marketplace')}
                      className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition"
                    >
                      Inquire <ChevronRight size={13} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* 5. TESTIMONIALS & SOCIAL PROOF */}
      <section className="py-20 px-8 max-w-5xl mx-auto w-full text-left">
        <div className="mb-10 text-center">
          <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 font-mono">Member Testimonials</span>
          <h2 className="text-2xl font-black text-white tracking-tight mt-1">Ecosystem Feedback</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 text-left">
            <div className="flex items-center gap-1 text-amber-400">
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
            </div>
            <p className="text-xs text-slate-350 leading-relaxed italic">
              "The single-account capability system is revolutionary. I teach SaaS databases in the morning and buy proctored NEET physics guide sets in the afternoon."
            </p>
            <div className="text-xs">
              <strong className="block text-slate-200">Dr. Vivek Sharma</strong>
              <span className="text-slate-500">Associate Professor</span>
            </div>
          </div>
          
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 text-left">
            <div className="flex items-center gap-1 text-amber-400">
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
            </div>
            <p className="text-xs text-slate-350 leading-relaxed italic">
              "Earning digital certificate cryptographic keys here helped me pass five corporate ATS resume checks instantly. The automated builder works perfectly!"
            </p>
            <div className="text-xs">
              <strong className="block text-slate-200">Neha Iyer</strong>
              <span className="text-slate-500">Full-Stack Engineer</span>
            </div>
          </div>

          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4 text-left">
            <div className="flex items-center gap-1 text-amber-400">
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
              <Star size={12} fill="currentColor" />
            </div>
            <p className="text-xs text-slate-350 leading-relaxed italic">
              "I publish tutorials, manage client dev contracts, and verify double-entry payments safely in my integrated ledger. Truly a complete digital workspace."
            </p>
            <div className="text-xs">
              <strong className="block text-slate-200">Rahul Sen</strong>
              <span className="text-slate-500">Freelance Publisher</span>
            </div>
          </div>
        </div>
      </section>

      {/* 6. PARTNERS LOGO GRID */}
      <section className="bg-slate-950 border-t border-indigo-950/20 py-12 px-6">
        <div className="max-w-5xl mx-auto flex flex-wrap justify-center items-center gap-12 opacity-40 grayscale hover:grayscale-0 transition duration-300">
          <span className="text-xs font-bold font-mono tracking-widest text-slate-400">IIT BOMBAY CO-OP</span>
          <span className="text-xs font-bold font-mono tracking-widest text-slate-400">BITS PILANI NODES</span>
          <span className="text-xs font-bold font-mono tracking-widest text-slate-400">AMAZON WEB SERVICES</span>
          <span className="text-xs font-bold font-mono tracking-widest text-slate-400">GOOGLE GENAI PARTNER</span>
        </div>
      </section>

    </div>
  );
};

export default HomeShell;
