/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useLayoutStore } from '../../stores/layoutStore';
import { useAuthStore } from '../../stores/authStore';
import { Product, Book } from '../../types';
import { Input, Button, LoadingSpinner } from '../../components/DesignSystem';
import { ArrowLeft, Briefcase, ChevronRight, Mail, DollarSign, Clock, Send, ShieldCheck, Tag, Sparkles, BookOpen } from 'lucide-react';

export const ServicesPage: React.FC = () => {
  const { currentPath, navigateTo } = useLayoutStore();
  const { currentUser } = useAuthStore();
  const [services, setServices] = useState<Product[]>([]);
  const [selectedService, setSelectedService] = useState<Product | null>(null);
  const [relatedBooks, setRelatedBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  // Lead form states
  const [name, setName] = useState('');
  const [email, setMail] = useState('');
  const [desc, setDesc] = useState('');
  const [budget, setBudget] = useState(5000);
  const [submittingLead, setSubmittingLead] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  // Extract ID parameter virtual matching: /services/:id
  const match = currentPath.match(/^\/services\/([^/]+)/);
  const serviceId = match ? match[1] : null;

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.marketplace.listProducts({ type: 'SERVICE' }),
      api.books.list()
    ])
      .then(([productsRes, booksRes]) => {
        if (productsRes.success && productsRes.data) {
          setServices(productsRes.data);
          if (serviceId) {
            const found = productsRes.data.find(s => s.id === serviceId);
            if (found) setSelectedService(found);
          }
        }
        if (booksRes.success && booksRes.data) {
          setRelatedBooks(booksRes.data.slice(0, 2));
        }
      })
      .finally(() => setLoading(false));
  }, [serviceId]);

  const handleLeadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      alert('Authentication required to submit project leads. Redirecting to login desk...');
      navigateTo('/auth');
      return;
    }
    if (!selectedService) return;
    setSubmittingLead(true);
    setSuccessMsg('');
    try {
      const res = await api.marketplace.submitServiceRequest({
        userId: currentUser.id,
        userName: currentUser.fullName,
        serviceType: selectedService.name,
        description: desc,
        budget,
      });
      if (res.success) {
        setSuccessMsg('Your service inquiry has been logged securely. Lead token generated.');
        setName('');
        setMail('');
        setDesc('');
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingLead(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Mapping service catalog nodes..." />;
  }

  // 1. DETAIL VIEW RENDER
  if (serviceId && selectedService) {
    return (
      <div className="flex-1 flex flex-col bg-[#070b19]">
        {/* Breadcrumb Header */}
        <div className="bg-[#0b1329] border-b border-indigo-950/40 px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between gap-4 text-xs">
            <button 
              onClick={() => navigateTo('/services')}
              className="flex items-center gap-1.5 text-slate-400 hover:text-white transition font-bold"
            >
              <ArrowLeft size={13} /> Services Catalog
            </button>
            <div className="text-slate-500 font-mono hidden sm:block">
              Home &gt; Services &gt; {selectedService.name.substring(0, 30)}...
            </div>
          </div>
        </div>

        {/* Detailed page grid */}
        <section className="py-12 px-6 max-w-4xl mx-auto w-full text-left grid grid-cols-1 md:grid-cols-12 gap-8">
          
          {/* Service descriptions */}
          <div className="md:col-span-7 space-y-6">
            <div className="space-y-3">
              <span className="px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-400 font-mono text-[9px] uppercase tracking-wider font-bold">
                Professional Service
              </span>
              <h1 className="text-2xl md:text-3xl font-black text-white leading-tight">{selectedService.name}</h1>
              <div className="flex gap-4 text-[10px] text-slate-500 font-mono">
                <span className="flex items-center gap-1"><Clock size={12} /> EST DELIVERY: 7-10 Days</span>
                <span>•</span>
                <span className="flex items-center gap-1"><Tag size={12} /> CATEGORY: Web Dev</span>
              </div>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed border-t border-b border-indigo-950/40 py-4">
              {selectedService.description || 'Our verified service providers design premium solutions custom integrated with BrahmaVidya API capabilities.'}
            </p>

            <div className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">Milestone Settlements</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Projects are paid dynamically in milestone chunks. Funding stays locked in the ledger until each checkpoint is reviewed and approved.
              </p>
            </div>
          </div>

          {/* Lead Inquiry Form */}
          <div className="md:col-span-5">
            <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl shadow-xl space-y-4">
              <h4 className="text-sm font-bold text-white flex items-center gap-1.5 border-b border-indigo-950/40 pb-3 mb-2">
                <Briefcase size={16} className="text-indigo-400" /> Start Inquiry Project
              </h4>

              {successMsg ? (
                <div className="p-4 bg-emerald-950/40 border border-emerald-900 text-xs text-emerald-350 font-medium rounded-xl space-y-2 text-center">
                  <ShieldCheck size={24} className="text-emerald-450 mx-auto animate-bounce" />
                  <p>{successMsg}</p>
                  <Button size="sm" variant="outline" className="text-[10px] mt-2" onClick={() => setSuccessMsg('')}>
                    Submit Another
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleLeadSubmit} className="space-y-4">
                  <Input label="Your Name" type="text" placeholder="Dr. Rajesh Patel" required value={name} onChange={(e) => setName(e.target.value)} />
                  <Input label="Your Email" type="email" placeholder="patel@domain.com" required value={email} onChange={(e) => setMail(e.target.value)} />
                  
                  <div className="flex flex-col gap-1.5 text-left w-full">
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Project Scope</label>
                    <textarea
                      required
                      placeholder="Explain your customized requirements..."
                      value={desc}
                      onChange={(e) => setDesc(e.target.value)}
                      className="w-full bg-slate-900 border border-indigo-950/80 rounded-xl p-3 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200 min-h-[90px]"
                    />
                  </div>

                  <div className="flex flex-col gap-1 text-xs">
                    <div className="flex justify-between font-bold text-slate-400 uppercase tracking-wider text-[9px]">
                      <span>Project Budget</span>
                      <span className="text-indigo-400 font-mono">₹{budget.toLocaleString()}</span>
                    </div>
                    <input
                      type="range"
                      min={1000}
                      max={100000}
                      step={500}
                      value={budget}
                      onChange={(e) => setBudget(Number(e.target.value))}
                      className="w-full h-1.5 rounded-lg bg-indigo-950 appearance-none cursor-pointer accent-indigo-600 mt-2"
                    />
                  </div>

                  <Button type="submit" isLoading={submittingLead} className="w-full flex items-center justify-center gap-2 mt-2">
                    <Send size={13} /> Submit Service Lead
                  </Button>
                </form>
              )}
            </div>
          </div>

        </section>

        {/* Recommended Books Section */}
        <section className="py-12 border-t border-indigo-950/30 max-w-4xl mx-auto w-full px-6 text-left space-y-6">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-widest text-indigo-400 font-mono flex items-center gap-1">
              <Sparkles size={11} /> Related Publications
            </span>
            <h3 className="text-lg font-bold text-white tracking-tight mt-0.5">Recommended Bookstore Guides</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {relatedBooks.map((b, idx) => (
              <div key={b.id || idx} className="p-5 bg-slate-900 border border-indigo-950 rounded-2xl flex justify-between items-center hover:border-indigo-900 transition">
                <div className="space-y-1">
                  <h4 className="text-xs font-bold text-white leading-snug">{b.title}</h4>
                  <span className="text-[9px] text-emerald-450 font-mono block">Estimated: ₹{b.price.toLocaleString()}</span>
                </div>
                <button 
                  onClick={() => navigateTo(`/bookstore/${b.id}`)}
                  className="p-2 bg-indigo-950/40 border border-indigo-900/40 rounded-xl text-indigo-400 hover:text-white hover:bg-indigo-650 transition cursor-pointer"
                >
                  <ChevronRight size={14} />
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>
    );
  }

  // 2. LISTING VIEW RENDER
  return (
    <div className="flex-1 flex flex-col bg-[#070b19]">
      {/* Hero Section */}
      <section className="relative py-16 px-8 text-left border-b border-indigo-950/40">
        <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-indigo-650/10 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="max-w-4xl mx-auto space-y-4">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Agency Services</span>
          <h1 className="text-3xl font-black text-white tracking-tight">Professional Services Marketplace</h1>
          <p className="text-slate-400 text-xs max-w-lg leading-relaxed">
            Directly contract certified service providers for development, SEO audits, UI/UX designs, and prompt engineering solutions.
          </p>
        </div>
      </section>

      {/* Services Grid */}
      <section className="py-16 px-6 max-w-5xl mx-auto w-full text-left">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {services.map((svc, idx) => (
            <div 
              key={svc.id || idx}
              className="bg-slate-900 border border-indigo-950 rounded-2xl flex flex-col justify-between overflow-hidden hover:border-indigo-900 transition duration-200"
            >
              <div className="p-5 space-y-3">
                <div className="p-2.5 bg-indigo-950/50 text-indigo-400 rounded-xl w-fit">
                  <Briefcase size={16} />
                </div>
                <h4 className="text-sm font-bold text-white leading-snug">{svc.name}</h4>
                <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
                  {svc.description || 'Custom integrated services managed securely via smart contract ledgers.'}
                </p>
              </div>
              <div className="p-4 border-t border-indigo-950/40 bg-slate-900/60 flex justify-between items-center text-xs font-mono">
                <span className="text-indigo-400 font-bold">₹{svc.price.toLocaleString()}</span>
                <button
                  onClick={() => navigateTo(`/services/${svc.id}`)}
                  className="text-xs font-bold text-indigo-400 hover:text-indigo-300 flex items-center gap-0.5 transition cursor-pointer"
                >
                  Details <ChevronRight size={13} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default ServicesPage;
