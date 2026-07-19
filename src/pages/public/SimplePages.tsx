/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useLayoutStore } from '../../stores/layoutStore';
import { Button, Input, Checkbox } from '../../components/DesignSystem';
import { 
  Users, Target, Compass, Award, Shield, CheckCircle, Mail, Phone, 
  MapPin, Clock, ArrowRight, HelpCircle, Briefcase, Send, ChevronDown 
} from 'lucide-react';

export const SimplePages: React.FC = () => {
  const { currentPath, navigateTo } = useLayoutStore();

  // 1. ABOUT PAGE RENDER
  if (currentPath === '/about') {
    return (
      <div className="flex-1 flex flex-col bg-[#070b19]">
        {/* Hero Section */}
        <section className="relative py-20 px-8 text-left border-b border-indigo-950/40">
          <div className="absolute top-1/4 left-1/3 w-[300px] h-[300px] bg-indigo-650/10 rounded-full blur-[100px] pointer-events-none"></div>
          <div className="max-w-4xl mx-auto space-y-4">
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Our Heritage</span>
            <h1 className="text-3xl md:text-5xl font-black text-white leading-tight">About BrahmaVidya Galaxy</h1>
            <p className="text-slate-400 text-sm max-w-xl leading-relaxed">
              BrahmaVidya Galaxy is an advanced multi-tenant academic and digital services network, combining proctored learning with double-entry cryptographic accounting and micro-credentials.
            </p>
          </div>
        </section>

        {/* Mission grid */}
        <section className="py-16 px-6 max-w-5xl mx-auto w-full text-left grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3">
            <div className="p-3 bg-indigo-950 text-indigo-400 rounded-xl w-fit"><Target size={18} /></div>
            <h4 className="text-sm font-bold text-white">Ecosystem Vision</h4>
            <p className="text-xs text-slate-400 leading-relaxed">To collapse the boundary between learning academic skills and selling professional freelance work.</p>
          </div>
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3">
            <div className="p-3 bg-indigo-950 text-indigo-400 rounded-xl w-fit"><Compass size={18} /></div>
            <h4 className="text-sm font-bold text-white">Global Compliance</h4>
            <p className="text-xs text-slate-400 leading-relaxed">Providing secure double-entry financial settlements and immutable certification audits.</p>
          </div>
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-3">
            <div className="p-3 bg-indigo-950 text-indigo-400 rounded-xl w-fit"><Users size={18} /></div>
            <h4 className="text-sm font-bold text-white">Capability Driven</h4>
            <p className="text-xs text-slate-400 leading-relaxed">Users activate dynamic skills—Student, Teacher, Author—under one central profile identity.</p>
          </div>
        </section>
      </div>
    );
  }

  // 2. PRICING PAGE RENDER
  if (currentPath === '/pricing') {
    const plans = [
      { name: 'Learner', price: 'Free', desc: 'Browse courses, practice quiz sessions, and verify cert hashes.', features: ['Access to Free Syllabus Trees', 'Public Forum Discussions', 'Digital Certificate Verification', 'Basic Vidya AI Chat (5 prompts/day)'] },
      { name: 'Professional Creator', price: '₹4,999/yr', desc: 'Activate Teacher, Author, and Freelance Service Provider capabilities.', features: ['Create & Publish Courses (subject to admin review)', 'Self-Publish EPUB/PDF Ebooks to Bookstore', 'List Freelance Development & UI Services', 'Unlimited AI Curriculum & Quiz Generator'] },
      { name: 'Enterprise Hub', price: '₹24,999/yr', desc: 'Setup multi-tenant Organization nodes with dynamic subdomain hosting.', features: ['Private Organization Subdomain', 'Custom Theme Palette Controls', 'Invite Members & Bulk Student Enrollments', 'Priority Settlement & Ledger Audit Reports'] },
    ];
    return (
      <div className="flex-1 flex flex-col bg-[#070b19] py-16 px-6">
        <div className="max-w-4xl mx-auto text-center space-y-4 mb-14">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Simple Billing</span>
          <h2 className="text-3xl font-black text-white tracking-tight">Flexible Platform Plans</h2>
          <p className="text-slate-400 text-xs max-w-md mx-auto leading-relaxed">Choose a subscription to unlock specific user capabilities and administrator approvals.</p>
        </div>

        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 w-full text-left">
          {plans.map((plan, idx) => (
            <div key={idx} className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl flex flex-col justify-between space-y-6 hover:border-indigo-900 transition">
              <div className="space-y-4">
                <div>
                  <h4 className="text-base font-bold text-white">{plan.name}</h4>
                  <span className="text-2xl font-black text-white block mt-1">{plan.price}</span>
                  <p className="text-xs text-slate-500 mt-1">{plan.desc}</p>
                </div>
                <div className="border-t border-indigo-950/40 pt-4 space-y-2.5">
                  {plan.features.map((feat, fIdx) => (
                    <div key={fIdx} className="flex items-start gap-2 text-xs text-slate-350">
                      <CheckCircle size={14} className="text-emerald-500 mt-0.5 shrink-0" />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>
              <Button onClick={() => navigateTo('/auth')} className="w-full">
                Activate Capabilities
              </Button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 3. FAQ PAGE RENDER
  if (currentPath === '/faq') {
    const faqs = [
      { q: 'What is Capability-Based Access Control (CBAC)?', a: 'Instead of separate teacher and student accounts, CBAC allows a single account to have multiple active capabilities. A user can learn a course, author a book, and accept service requests simultaneously.' },
      { q: 'How do I publish an eBook in the bookstore?', a: 'You need to request the Author capability. Once approved by the administrator, you can upload PDFs or EPUB files, which undergo formatting audits before becoming public.' },
      { q: 'How are payments and transactions secured?', a: 'Every financial transfer uses a double-entry balance sheet database ledger system. Payout transactions can only occur after milestone verification.' },
      { q: 'Is the certificate verifier free to use?', a: 'Yes. Anyone, including recruiters and third-party employers, can verify digital certificate signature hashes on the public certificates page without logging in.' },
    ];
    return (
      <div className="flex-1 flex flex-col bg-[#070b19] py-16 px-6">
        <div className="max-w-3xl mx-auto w-full text-left space-y-8">
          <div>
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Support Hub</span>
            <h2 className="text-2xl font-black text-white tracking-tight mt-1">Frequently Asked Questions</h2>
          </div>
          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <div key={idx} className="p-5 bg-slate-900 border border-indigo-950/60 rounded-2xl space-y-2">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <HelpCircle size={15} className="text-indigo-400" />
                  {faq.q}
                </h4>
                <p className="text-xs text-slate-400 leading-relaxed pl-5">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 4. CAREERS PAGE RENDER
  if (currentPath === '/careers') {
    const jobs = [
      { title: 'Senior SaaS Frontend Engineer', dept: 'Engineering', loc: 'Remote (India)', desc: 'Design responsive React modules using TailwindCSS, Recharts, and dynamic virtual routing switch architectures.' },
      { title: 'AI Research Lead (Gemini API)', dept: 'Vidya AI Team', loc: 'Bengaluru Office', desc: 'Build prompt schemas and structured JSON curriculum builders using Google GenAI SDK integrations.' },
      { title: 'DRF Security Architect', dept: 'Backend Platform', loc: 'Remote', desc: 'Optimize database partitioning and implement advanced Capability-Based Access Control validators in Django REST Framework.' },
    ];
    return (
      <div className="flex-1 flex flex-col bg-[#070b19] py-16 px-6">
        <div className="max-w-4xl mx-auto w-full text-left space-y-10">
          <div>
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Join the Galaxy</span>
            <h2 className="text-2xl font-black text-white tracking-tight mt-1">Available Job Openings</h2>
            <p className="text-slate-400 text-xs mt-1">Help us construct the future of decentralized education and dynamic digital service economies.</p>
          </div>
          <div className="space-y-4">
            {jobs.map((job, idx) => (
              <div key={idx} className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4 hover:border-indigo-900 transition">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <h4 className="text-sm font-bold text-white">{job.title}</h4>
                    <span className="text-[9px] bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded font-bold uppercase">{job.dept}</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed max-w-xl">{job.desc}</p>
                  <span className="block text-[10px] text-slate-500 font-mono">LOCATION: {job.loc}</span>
                </div>
                <Button size="sm" onClick={() => alert('Application form submitted to recruitment queue.')}>
                  Apply Now
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 5. CONTACT PAGE RENDER
  if (currentPath === '/contact') {
    const handleContactSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      alert('Your message was successfully submitted to support. Ticket hash generated.');
    };
    return (
      <div className="flex-1 flex flex-col bg-[#070b19] py-16 px-6">
        <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 w-full text-left">
          {/* Info Column */}
          <div className="space-y-6">
            <div>
              <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Get In Touch</span>
              <h2 className="text-2xl font-black text-white tracking-tight mt-1">Contact Support Center</h2>
              <p className="text-slate-400 text-xs mt-1 leading-relaxed">Have custom integration questions, pricing inquiries, or require technical support? Drop us a line.</p>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center gap-3.5 text-xs text-slate-350">
                <div className="p-2.5 bg-indigo-950 text-indigo-400 rounded-lg"><Mail size={16} /></div>
                <div>
                  <span className="block text-slate-500 font-bold uppercase tracking-wider text-[9px]">Direct Email</span>
                  <span>support@brahmavidya.edu</span>
                </div>
              </div>
              <div className="flex items-center gap-3.5 text-xs text-slate-350">
                <div className="p-2.5 bg-indigo-950 text-indigo-400 rounded-lg"><Phone size={16} /></div>
                <div>
                  <span className="block text-slate-500 font-bold uppercase tracking-wider text-[9px]">Support Desk Phone</span>
                  <span>+91 80 4912 9000</span>
                </div>
              </div>
              <div className="flex items-center gap-3.5 text-xs text-slate-350">
                <div className="p-2.5 bg-indigo-950 text-indigo-400 rounded-lg"><MapPin size={16} /></div>
                <div>
                  <span className="block text-slate-500 font-bold uppercase tracking-wider text-[9px]">Ecosystem Hub</span>
                  <span>Silicon Valley Tech Park, Block E, Bengaluru</span>
                </div>
              </div>
            </div>
          </div>

          {/* Form Column */}
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl shadow-xl">
            <form onSubmit={handleContactSubmit} className="space-y-4">
              <Input label="Your Name" type="text" placeholder="Dr. Ananya Iyer" required />
              <Input label="Your Email" type="email" placeholder="ananya@domain.com" required />
              <div className="flex flex-col gap-1.5 text-left w-full">
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Your Message</label>
                <textarea
                  required
                  placeholder="How can our technical operators assist you?"
                  className="w-full bg-slate-900 border border-indigo-950/80 rounded-xl p-3 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 text-slate-200 min-h-[100px]"
                />
              </div>
              <Button type="submit" className="w-full flex items-center justify-center gap-2">
                <Send size={14} /> Send Secure Message
              </Button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  // 6. PRIVACY POLICY & TERMS RENDER
  if (currentPath === '/privacy' || currentPath === '/terms') {
    const isPrivacy = currentPath === '/privacy';
    return (
      <div className="flex-1 flex flex-col bg-[#070b19] py-16 px-6">
        <div className="max-w-3xl mx-auto w-full text-left space-y-6">
          <div>
            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Ecosystem Legal</span>
            <h2 className="text-2xl font-black text-white tracking-tight mt-1">
              {isPrivacy ? 'Privacy Sandbox Guidelines' : 'Platform Terms & Conditions'}
            </h2>
            <span className="block text-[10px] text-slate-500 font-mono mt-1">VERSION 1.0.4 // VERIFIED SECURITY SHA-256</span>
          </div>

          <div className="prose prose-invert max-w-none text-xs text-slate-400 space-y-4 leading-relaxed">
            <p>
              {isPrivacy 
                ? 'Your privacy is core to the BrahmaVidya Galaxy platform. We verify account details only through secure token-based logins, double-entry audit history ledgers, and dynamic capability approvals.'
                : 'Welcome to BrahmaVidya Galaxy. Accessing this academic and digital services network binds you to cryptographically audited ledger parameters, anti-abuse content regulations, and capabilities authorization codes.'
              }
            </p>
            <h4 className="text-sm font-bold text-slate-200 mt-6 uppercase tracking-wider">1. Data Audits & Checkpoints</h4>
            <p>
              Every transaction, application submission, and certificate verification signature is recorded on a secure ledger. Inactive capability profiles are automatically suspended after six months of system dormancy.
            </p>
            <h4 className="text-sm font-bold text-slate-200 mt-6 uppercase tracking-wider">2. System Compliance</h4>
            <p>
              Users are responsible for ensuring that all published tutorials, bookstore PDF/EPUB ebooks, and freelance agency service code uploads conform to appropriate license terms.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default SimplePages;
