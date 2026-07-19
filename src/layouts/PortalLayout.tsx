/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useLayoutStore } from '../stores/layoutStore';
import { useThemeStore } from '../stores/themeStore';
import { useGlobalSystem } from '../stores/globalSystemStore';
import { api } from '../services/api';
import { 
  Library, LogIn, LogOut, ShieldCheck, Sun, Moon, Search, Menu, X, 
  ChevronDown, CheckCircle, Wallet, Bell, Globe, Sparkles, BookOpen, 
  Layers, MessageSquare, Briefcase, Award, ShieldAlert, Settings, FileText 
} from 'lucide-react';
import { Button, Input, Dialog, Drawer, Badge } from '../components/DesignSystem';
import { NotificationCenter } from '../components/NotificationCenter';

export const PortalLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { currentUser, login, logout, refreshProfile } = useAuthStore();
  const { navigateTo, currentPath } = useLayoutStore();
  const { theme, setTheme, toggleTheme } = useThemeStore();
  const { locale, setLocale, translate, dialog, closeDialog } = useGlobalSystem();

  // Framework UI states
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any>(null);
  const [searching, setSearching] = useState(false);

  // Notifications mock data list
  const [notifications, setNotifications] = useState([
    { id: '1', title: 'Assignment Reviewed', body: 'Your NEET Physics module assignment has been marked approved.', time: '10m ago', unread: true },
    { id: '2', title: 'Royalty Statement Ready', body: 'June royalty statement for Authoring capability has been processed.', time: '2h ago', unread: true },
    { id: '3', title: 'Wallet Payment Settle', body: '₹12,500 milestone payment received for Web Development task.', time: '1d ago', unread: false }
  ]);

  // Context Navigation detector based on current URL path
  const getContextNavigation = () => {
    // Courses context
    if (currentPath === '/courses' || currentPath.startsWith('/courses/')) {
      return [
        { label: 'All Courses', path: '/courses' },
        { label: 'My Learning', path: '/student' },
        { label: 'Teaching Outlines', path: '/become-teacher' },
        { label: 'Certificates Verifier', path: '/certificates' }
      ];
    }
    // Bookstore context
    if (currentPath === '/bookstore' || currentPath.startsWith('/bookstore/')) {
      return [
        { label: 'eBook Library', path: '/bookstore' },
        { label: 'Publish Submission', path: '/become-author' },
        { label: 'Royalty Statements', path: '/dashboard' }
      ];
    }
    // Services context
    if (currentPath === '/marketplace' || currentPath === '/services' || currentPath.startsWith('/services/')) {
      return [
        { label: 'Services Marketplace', path: '/marketplace' },
        { label: 'Freelance Agency Projects', path: '/services' },
        { label: 'Become Provider', path: '/become-provider' }
      ];
    }
    // Templates/Builder context
    if (currentPath === '/portfolio' || currentPath === '/resumes') {
      return [
        { label: 'Portfolio Website Templates', path: '/portfolio' },
        { label: 'ATS Resume Outlines', path: '/resumes' }
      ];
    }
    // Forums context
    if (currentPath === '/community' || currentPath.startsWith('/community/')) {
      return [
        { label: 'Discussions Board', path: '/community' },
        { label: 'Community Q&A', path: '/community' },
        { label: 'Announcements log', path: '/blogs' }
      ];
    }
    return null;
  };

  const contextTabs = getContextNavigation();

  // Search trigger
  const handleGlobalSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await api.search.globalSearch(searchQuery);
      if (res.success && res.data) {
        setSearchResults(res.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSearching(false);
    }
  };

  const activeUnreadCount = notifications.filter(n => n.unread).length;

  return (
    <React.Fragment>
      <div id="bvg-portal-wrapper" className={`min-h-screen flex flex-col transition-colors duration-300 ${theme === 'light' ? 'bg-slate-50 text-slate-900' : 'bg-slate-950 text-slate-100'}`}>
        
        {/* Announcement Bar */}
        <div id="bvg-announcement-bar" className="bg-gradient-to-r from-indigo-900 to-purple-950 text-slate-200 py-1.5 px-4 text-center text-[10px] font-mono tracking-wider font-semibold border-b border-indigo-500/10 flex justify-center items-center gap-2 select-none">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-ping"></span>
          <span>📢 SYSTEM UPDATE: MULTI-CAPABILITY LEDGER VERIFICATIONS RUNNING HEALTHY. CHOOSE LOCALE:</span>
          <div className="flex gap-1.5 items-center pl-2">
            <button onClick={() => setLocale('en')} className={`px-1 rounded ${locale === 'en' ? 'bg-indigo-650 text-white font-bold' : 'text-slate-500 hover:text-white'}`}>EN</button>
            <span>|</span>
            <button onClick={() => setLocale('hi')} className={`px-1 rounded ${locale === 'hi' ? 'bg-indigo-650 text-white font-bold' : 'text-slate-500 hover:text-white'}`}>HI</button>
          </div>
        </div>

        {/* Global Top Navbar */}
        <header id="bvg-header" className={`border-b sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between shadow-xl transition-colors duration-300 ${theme === 'light' ? 'bg-white border-slate-200 text-slate-900' : 'bg-[#0b1329] border-indigo-950/80 text-slate-100'}`}>
          <div className="flex items-center gap-3">
            <button onClick={() => navigateTo('/')} className="bg-gradient-to-tr from-indigo-500 to-amber-500 p-2 rounded-xl shadow-lg hover:scale-105 transition">
              <Library className="text-white" size={18} />
            </button>
            <div className="text-left cursor-pointer" onClick={() => navigateTo('/')}>
              <h1 className="text-base font-black tracking-tight flex items-center gap-1.5">
                BrahmaVidya 
                <span className="text-indigo-400 font-light text-[8px] tracking-widest uppercase bg-indigo-950/60 px-1.5 py-0.5 rounded border border-indigo-900/40">Galaxy</span>
              </h1>
            </div>
          </div>

          {/* Desktop Global Navigation Menu */}
          <nav className="hidden lg:flex items-center gap-5 text-[11px] font-bold uppercase tracking-wider text-slate-400 select-none">
            <button onClick={() => navigateTo('/')} className={`hover:text-indigo-400 transition ${currentPath === '/' ? 'text-indigo-400 font-black' : ''}`}>Home</button>
            <button onClick={() => navigateTo('/courses')} className={`hover:text-indigo-400 transition ${currentPath.startsWith('/courses') ? 'text-indigo-400 font-black' : ''}`}>{translate('courses')}</button>
            <button onClick={() => navigateTo('/bookstore')} className={`hover:text-indigo-400 transition ${currentPath.startsWith('/bookstore') ? 'text-indigo-400 font-black' : ''}`}>{translate('bookstore')}</button>
            <button onClick={() => navigateTo('/services')} className={`hover:text-indigo-400 transition ${currentPath.startsWith('/services') || currentPath === '/marketplace' ? 'text-indigo-400 font-black' : ''}`}>{translate('services')}</button>
            <button onClick={() => navigateTo('/portfolio')} className={`hover:text-indigo-400 transition ${currentPath === '/portfolio' ? 'text-indigo-400 font-black' : ''}`}>{translate('portfolio')}</button>
            <button onClick={() => navigateTo('/resumes')} className={`hover:text-indigo-400 transition ${currentPath === '/resumes' ? 'text-indigo-400 font-black' : ''}`}>{translate('resume')}</button>
            <button onClick={() => navigateTo('/community')} className={`hover:text-indigo-400 transition ${currentPath.startsWith('/community') ? 'text-indigo-400 font-black' : ''}`}>{translate('community')}</button>
            <button onClick={() => navigateTo('/pricing')} className={`hover:text-indigo-400 transition ${currentPath === '/pricing' ? 'text-indigo-400 font-black' : ''}`}>{translate('pricing')}</button>
          </nav>

          {/* User Widgets, Themes & Notifications */}
          <div className="hidden lg:flex items-center gap-4 text-left">
            {/* Search Input click opens Global Search Dialog */}
            <div className="relative cursor-pointer" onClick={() => setIsSearchOpen(true)}>
              <Search className="absolute left-3 top-2 text-slate-500" size={13} />
              <input
                type="text"
                readOnly
                placeholder={translate('searchPlaceholder')}
                className="bg-slate-900/80 border border-indigo-950/80 rounded-full pl-8.5 pr-4 py-1 text-xs text-slate-400 w-44 cursor-pointer focus:outline-none"
              />
            </div>

            {/* Notification Bell */}
            <div className="relative">
              <button 
                onClick={() => setIsNotificationsOpen(true)}
                className="p-2 rounded-xl bg-slate-900 border border-indigo-950 text-slate-400 hover:text-white transition relative cursor-pointer"
              >
                <Bell size={14} />
                {activeUnreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-4 w-4 bg-rose-600 rounded-full border border-slate-950 flex items-center justify-center text-[8px] font-bold text-white">
                    {activeUnreadCount}
                  </span>
                )}
              </button>
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-slate-900 border border-indigo-950 text-slate-400 hover:text-white transition cursor-pointer"
            >
              {theme === 'light' ? <Sun size={14} /> : <Moon size={14} />}
            </button>

            {currentUser ? (
              <div className="flex items-center gap-3 relative">
                <NotificationCenter />
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center gap-2.5 p-1 rounded-full hover:bg-slate-900/60 transition text-left cursor-pointer"
                >
                  <img
                    src={currentUser.avatarUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=150'}
                    alt="Avatar"
                    className="h-8 w-8 rounded-full border border-indigo-500/85 object-cover"
                  />
                  <ChevronDown size={12} className="text-slate-500" />
                </button>

                {isProfileOpen && (
                  <div className="absolute right-0 mt-3 w-56 bg-[#0b1329] border border-indigo-950 rounded-2xl p-4 shadow-2xl z-50 text-xs space-y-3 animate-fade-in text-left">
                    <div>
                      <span className="block font-bold text-white">{currentUser.fullName}</span>
                      <span className="text-[10px] text-indigo-400 font-mono flex items-center gap-0.5 mt-0.5">
                        <Wallet size={9} /> ₹{currentUser.walletBalance.toLocaleString()}
                      </span>
                    </div>
                    
                    <div className="border-t border-indigo-950/60 pt-2.5 space-y-1.5 text-slate-400">
                      <button onClick={() => { setIsProfileOpen(false); navigateTo('/student'); }} className="w-full text-left py-1 hover:text-white transition flex items-center gap-1.5"><BookOpen size={12} /> Student Space</button>
                      <button onClick={() => { setIsProfileOpen(false); navigateTo('/dashboard'); }} className="w-full text-left py-1 hover:text-white transition flex items-center gap-1.5"><Layers size={12} /> Dashboard</button>
                      <button onClick={() => { setIsProfileOpen(false); navigateTo('/become-teacher'); }} className="w-full text-left py-1 hover:text-white transition flex items-center gap-1.5"><Settings size={12} /> Capability Settings</button>
                    </div>

                    <div className="border-t border-indigo-950/60 pt-2.5">
                      <button
                        onClick={() => { setIsProfileOpen(false); logout(); }}
                        className="w-full py-1.5 bg-slate-900 border border-slate-800 hover:text-white rounded-lg font-bold text-center transition flex items-center justify-center gap-1.5"
                      >
                        <LogOut size={12} /> {translate('signOut')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => navigateTo('/auth')}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-550 text-white rounded-xl text-xs font-semibold transition flex items-center gap-1.5 shadow-lg shadow-indigo-650/10 cursor-pointer"
              >
                <LogIn size={13} />
                {translate('signIn')}
              </button>
            )}
          </div>

          {/* Mobile hamburger menu toggle */}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 rounded-xl bg-slate-900 border border-indigo-950 text-slate-400 hover:text-white transition cursor-pointer"
          >
            <Menu size={16} />
          </button>
        </header>

        {/* Dynamic Context Navigation Bar (under headers) */}
        {contextTabs && (
          <div className={`border-b select-none transition-colors duration-300 ${theme === 'light' ? 'bg-slate-100 border-slate-200' : 'bg-slate-950 border-indigo-950/40'}`}>
            <div className="max-w-7xl mx-auto px-6 flex gap-6 text-[10px] font-bold uppercase tracking-widest font-mono">
              {contextTabs.map((tab, idx) => {
                const isTabActive = currentPath === tab.path || (tab.path !== '/' && currentPath.startsWith(tab.path));
                return (
                  <button
                    key={idx}
                    onClick={() => navigateTo(tab.path)}
                    className={`py-3 transition border-b-2 cursor-pointer ${isTabActive ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-500 hover:text-slate-350'}`}
                  >
                    {tab.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Mobile Navigation Drawer */}
        {isMobileMenuOpen && (
          <Drawer isOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)} title="Menu Navigation">
            <div className="flex flex-col gap-4 text-xs">
              <button onClick={() => { setIsMobileMenuOpen(false); navigateTo('/'); }} className="py-2.5 text-left border-b border-indigo-950/40 text-slate-400 hover:text-white">Home</button>
              <button onClick={() => { setIsMobileMenuOpen(false); navigateTo('/courses'); }} className="py-2.5 text-left border-b border-indigo-950/40 text-slate-400 hover:text-white">Courses</button>
              <button onClick={() => { setIsMobileMenuOpen(false); navigateTo('/bookstore'); }} className="py-2.5 text-left border-b border-indigo-950/40 text-slate-400 hover:text-white">Bookstore</button>
              <button onClick={() => { setIsMobileMenuOpen(false); navigateTo('/services'); }} className="py-2.5 text-left border-b border-indigo-950/40 text-slate-400 hover:text-white">Services</button>
              <button onClick={() => { setIsMobileMenuOpen(false); navigateTo('/community'); }} className="py-2.5 text-left border-b border-indigo-950/40 text-slate-400 hover:text-white">Community</button>
              <button onClick={() => { setIsMobileMenuOpen(false); navigateTo('/pricing'); }} className="py-2.5 text-left border-b border-indigo-950/40 text-slate-400 hover:text-white">Pricing</button>
            </div>
          </Drawer>
        )}

        {/* Dynamic Notifications Center Drawer */}
        {isNotificationsOpen && (
          <Drawer 
            isOpen={isNotificationsOpen} 
            onClose={() => setIsNotificationsOpen(false)} 
            title={`Notification Center (${activeUnreadCount})`}
            position="right"
          >
            <div className="space-y-4">
              {notifications.map(n => (
                <div 
                  key={n.id} 
                  onClick={() => {
                    setNotifications(prev => prev.map(item => item.id === n.id ? { ...item, unread: false } : item));
                  }}
                  className={`p-4 rounded-xl border text-xs text-left cursor-pointer transition ${n.unread ? 'bg-indigo-950/20 border-indigo-500/30' : 'bg-slate-900 border-indigo-950 text-slate-400'}`}
                >
                  <div className="flex justify-between items-start">
                    <strong className="text-white font-bold">{n.title}</strong>
                    <span className="text-[9px] text-slate-500 font-mono">{n.time}</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{n.body}</p>
                </div>
              ))}
            </div>
          </Drawer>
        )}

        {/* Global Search Dialog Modal */}
        <Dialog isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} title="Global Database Search" size="lg">
          <form onSubmit={handleGlobalSearch} className="space-y-6">
            <div className="relative">
              <Search className="absolute left-3.5 top-3.5 text-slate-500" size={16} />
              <input
                type="text"
                autoFocus
                placeholder="Search database nodes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900 border border-indigo-950 rounded-xl py-3 pl-11 pr-4 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200"
              />
            </div>

            {searching ? (
              <div className="py-8 text-center text-xs text-slate-500 font-mono">Querying database tables...</div>
            ) : searchResults ? (
              <div className="space-y-4 max-h-80 overflow-y-auto pr-2 text-xs">
                {searchResults.courses?.length > 0 && (
                  <div>
                    <h5 className="font-bold text-slate-500 uppercase tracking-widest text-[9px] mb-2">Courses Outlines</h5>
                    <div className="space-y-1.5">
                      {searchResults.courses.map((c: any) => (
                        <div key={c.id} onClick={() => { setIsSearchOpen(false); navigateTo(`/courses/${c.id}`); }} className="p-3 bg-slate-900/60 rounded-xl border border-indigo-950 cursor-pointer hover:border-indigo-500 transition leading-snug">
                          {c.title}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {searchResults.books?.length > 0 && (
                  <div>
                    <h5 className="font-bold text-slate-500 uppercase tracking-widest text-[9px] mb-2 mt-4">Ebook bookstore</h5>
                    <div className="space-y-1.5">
                      {searchResults.books.map((b: any) => (
                        <div key={b.id} onClick={() => { setIsSearchOpen(false); navigateTo(`/bookstore/${b.id}`); }} className="p-3 bg-slate-900/60 rounded-xl border border-indigo-950 cursor-pointer hover:border-indigo-500 transition leading-snug">
                          {b.title}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {(!searchResults.courses?.length && !searchResults.books?.length) && (
                  <div className="text-center py-6 text-slate-500 font-mono italic">No matching index found.</div>
                )}
              </div>
            ) : (
              <div className="text-center py-6 text-slate-500 font-mono italic">Enter terms above to index results.</div>
            )}
          </form>
        </Dialog>

        {/* Global Dialog system overlay driven by globalSystemStore */}
        {dialog.isOpen && (
          <Dialog isOpen={dialog.isOpen} onClose={closeDialog} title={dialog.title} size="sm">
            <div className="space-y-4 text-xs">
              <p className="text-slate-350 leading-relaxed">{dialog.message}</p>
              <div className="flex justify-end gap-3.5">
                <Button size="sm" variant="ghost" onClick={closeDialog}>Cancel</Button>
                <Button size="sm" variant={dialog.type === 'delete' ? 'danger' : 'primary'} onClick={() => { if (dialog.onConfirm) dialog.onConfirm(); closeDialog(); }}>Confirm</Button>
              </div>
            </div>
          </Dialog>
        )}

        {/* Main Content Body */}
        <main id="bvg-main-content" className="flex-1 flex flex-col relative">
          {children}
        </main>

        {/* Global Footer */}
        <footer id="bvg-footer" className={`border-t py-10 px-8 transition-colors duration-300 ${theme === 'light' ? 'bg-slate-100 border-slate-200 text-slate-655' : 'bg-[#070b19] border-indigo-950/40 text-slate-450'}`}>
          <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 text-left text-xs mb-8">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Library className="text-indigo-400" size={18} />
                <span className="text-sm font-bold text-white uppercase tracking-wider">BrahmaVidya Galaxy</span>
              </div>
              <p className="leading-relaxed text-slate-500">
                A dynamic AI-powered digital learning ecosystem powered by Capability-Based Access Control and cryptographic ledger audits.
              </p>
            </div>
            
            <div className="space-y-3">
              <span className="font-bold text-white uppercase tracking-wider text-[10px]">Academic Ecosystem</span>
              <ul className="space-y-2">
                <li><a href="#/courses" className="hover:text-indigo-400 transition">Syllabus Outlines</a></li>
                <li><a href="#/bookstore" className="hover:text-indigo-400 transition">eBook Library</a></li>
                <li><a href="#/services" className="hover:text-indigo-400 transition">Services Marketplace</a></li>
                <li><a href="#/pricing" className="hover:text-indigo-400 transition">Pricing Plans</a></li>
              </ul>
            </div>

            <div className="space-y-3">
              <span className="font-bold text-white uppercase tracking-wider text-[10px]">Security & Audits</span>
              <ul className="space-y-2">
                <li><a href="#/certificates" className="hover:text-indigo-400 transition">Signature Verifier</a></li>
                <li><a href="#/faq" className="hover:text-indigo-400 transition">FAQ Accordions</a></li>
                <li><span className="text-slate-500">Ledger Compliance Check</span></li>
              </ul>
            </div>

            <div className="space-y-3">
              <span className="font-bold text-white uppercase tracking-wider text-[10px]">Ecosystem Legal</span>
              <ul className="space-y-2">
                <li><a href="#/privacy" className="hover:text-indigo-400 transition">Privacy Sandbox</a></li>
                <li><a href="#/terms" className="hover:text-indigo-400 transition">Terms of Use</a></li>
                <li><span className="text-slate-500">Cryptographic Disclosures</span></li>
              </ul>
            </div>
          </div>

          <div className="max-w-7xl mx-auto border-t border-indigo-950/40 pt-6 flex flex-col sm:flex-row justify-between items-center gap-4 text-[10px] text-slate-500 select-none">
            <p>© 2026 BrahmaVidya Galaxy Academic Network. Secure cryptographically-audited state verification.</p>
            <div className="flex gap-4 font-mono text-indigo-500/80">
              <span>LATENCY: 12ms</span>
              <span>•</span>
              <span>LOCALE: {locale.toUpperCase()}</span>
            </div>
          </div>
        </footer>

      </div>
    </React.Fragment>
  );
};

export default PortalLayout;
