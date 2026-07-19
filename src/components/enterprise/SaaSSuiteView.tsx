/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';

// Import All 15 Enterprise Modules
import { Module1Subscriptions } from './Module1Subscriptions';
import { Module2Organizations } from './Module2Organizations';
import { Module3Accounting } from './Module3Accounting';
import { Module4Affiliate } from './Module4Affiliate';
import { Module5Messaging } from './Module5Messaging';
import { Module6LiveLearning } from './Module6LiveLearning';
import { Module7VideoStreaming } from './Module7VideoStreaming';
import { Module8Community } from './Module8Community';
import { Module9Jobs } from './Module9Jobs';
import { Module10Internship } from './Module10Internship';
import { Module11Notifications } from './Module11Notifications';
import { Module12Search } from './Module12Search';
import { Module13Analytics } from './Module13Analytics';
import { Module14Security } from './Module14Security';
import { Module15EnterpriseAI } from './Module15EnterpriseAI';

// Import All 15 Production Modules
import { ProdModule1Workflow } from '../production/ProdModule1Workflow';
import { ProdModule2Celery } from '../production/ProdModule2Celery';
import { ProdModule3Settlement } from '../production/ProdModule3Settlement';
import { ProdModule4Contracts } from '../production/ProdModule4Contracts';
import { ProdModule5Verification } from '../production/ProdModule5Verification';
import { ProdModule6Websites } from '../production/ProdModule6Websites';
import { ProdModule7AIStudio } from '../production/ProdModule7AIStudio';
import { ProdModule8MobileAPI } from '../production/ProdModule8MobileAPI';
import { ProdModule9Monitoring } from '../production/ProdModule9Monitoring';
import { ProdModule10DevOps } from '../production/ProdModule10DevOps';
import { ProdModule11I18n } from '../production/ProdModule11I18n';
import { ProdModule12SEO } from '../production/ProdModule12SEO';
import { ProdModule13Accessibility } from '../production/ProdModule13Accessibility';
import { ProdModule14Performance } from '../production/ProdModule14Performance';
import { ProdModule15Audit } from '../production/ProdModule15Audit';

import {
  CreditCard,
  Building2,
  Calculator,
  UserCheck,
  MessageSquare,
  Video,
  Tv,
  Users,
  Briefcase,
  GraduationCap,
  Bell,
  Search,
  BarChart4,
  ShieldCheck,
  Brain,
  Layers,
  ChevronRight,
  Info,
  Sliders,
  Settings,
  Terminal,
  Activity,
  Award,
  Globe,
  FileText,
  Accessibility,
  Zap,
  Play,
  Smartphone
} from 'lucide-react';

interface SaaSModuleItem {
  id: number;
  name: string;
  desc: string;
  icon: any;
  component: React.ComponentType;
  color: string;
}

export const SaaSSuiteView: React.FC = () => {
  const { currentUser } = useAuthStore();
  const [suiteMode, setSuiteMode] = useState<'enterprise' | 'production'>('enterprise');
  const [activeModuleId, setActiveModuleId] = useState<number>(1);
  const [filterQuery, setFilterQuery] = useState<string>('');

  const ENTERPRISE_MODULES: SaaSModuleItem[] = [
    {
      id: 1,
      name: 'Tier Subscriptions',
      desc: 'Tier billing, GST invoicing, Coupon rules',
      icon: CreditCard,
      component: Module1Subscriptions,
      color: 'text-indigo-400'
    },
    {
      id: 2,
      name: 'Multi-Tenant Orgs',
      desc: 'Departments & Org invitations system',
      icon: Building2,
      component: Module2Organizations,
      color: 'text-emerald-400'
    },
    {
      id: 3,
      name: 'Double Accounting',
      desc: 'Double-entry ledger & platform costs',
      icon: Calculator,
      component: Module3Accounting,
      color: 'text-cyan-400'
    },
    {
      id: 4,
      name: 'Multi-Level Affiliate',
      desc: 'Commission splits & referee reward ledgers',
      icon: UserCheck,
      component: Module4Affiliate,
      color: 'text-sky-400'
    },
    {
      id: 5,
      name: 'Realtime Messaging',
      desc: 'Read-receipt channels & multimedia attach',
      icon: MessageSquare,
      component: Module5Messaging,
      color: 'text-rose-400'
    },
    {
      id: 6,
      name: 'Live Whiteboard',
      desc: 'Whiteboards & Raise hands queues',
      icon: Video,
      component: Module6LiveLearning,
      color: 'text-amber-400'
    },
    {
      id: 7,
      name: 'Video Notes Streaming',
      desc: 'Bookmarks, speed & sync notebook panels',
      icon: Tv,
      component: Module7VideoStreaming,
      color: 'text-purple-400'
    },
    {
      id: 8,
      name: 'Reputation Forums',
      desc: 'Best answer credentials & reputations',
      icon: Users,
      component: Module8Community,
      color: 'text-teal-400'
    },
    {
      id: 9,
      name: 'Jobs Board',
      desc: 'Employer dashboards & candidate resume tags',
      icon: Briefcase,
      component: Module9Jobs,
      color: 'text-orange-400'
    },
    {
      id: 10,
      name: 'Intern Deliverables',
      desc: 'Academic mentoring logs & hours completion',
      icon: GraduationCap,
      component: Module10Internship,
      color: 'text-pink-400'
    },
    {
      id: 11,
      name: 'Alert Dispatcher',
      desc: 'SendGrid & Twilio delivery queues',
      icon: Bell,
      component: Module11Notifications,
      color: 'text-indigo-400'
    },
    {
      id: 12,
      name: 'Elastic Global Search',
      desc: 'Sub-second indexed cross-domain search',
      icon: Search,
      component: Module12Search,
      color: 'text-emerald-400'
    },
    {
      id: 13,
      name: 'SaaS Analytics',
      desc: 'Recharts enrollment trends & subscription share',
      icon: BarChart4,
      component: Module13Analytics,
      color: 'text-amber-400'
    },
    {
      id: 14,
      name: 'Security Logs & 2FA',
      desc: 'TOTP Google Authenticator & Audit tables',
      icon: ShieldCheck,
      component: Module14Security,
      color: 'text-rose-400'
    },
    {
      id: 15,
      name: 'Gemini AI Tutor',
      desc: 'Vidya AI chatbot & smart prompt presets',
      icon: Brain,
      component: Module15EnterpriseAI,
      color: 'text-indigo-400'
    }
  ];

  const PRODUCTION_MODULES: SaaSModuleItem[] = [
    {
      id: 1,
      name: 'Workflow Engine',
      desc: 'Visual node pipeline simulator',
      icon: Play,
      component: ProdModule1Workflow,
      color: 'text-indigo-400'
    },
    {
      id: 2,
      name: 'Background Jobs',
      desc: 'Celery queue & worker status panels',
      icon: Terminal,
      component: ProdModule2Celery,
      color: 'text-emerald-400'
    },
    {
      id: 3,
      name: 'Settlement Engine',
      desc: 'Teacher revenue, GST & TDS ledgers',
      icon: Calculator,
      component: ProdModule3Settlement,
      color: 'text-cyan-400'
    },
    {
      id: 4,
      name: 'Digital Contracts',
      desc: 'Agreement templates & e-signatures',
      icon: FileText,
      component: ProdModule4Contracts,
      color: 'text-sky-400'
    },
    {
      id: 5,
      name: 'Credentials Portal',
      desc: 'QR verification & AI fraud metrics',
      icon: ShieldCheck,
      component: ProdModule5Verification,
      color: 'text-rose-400'
    },
    {
      id: 6,
      name: 'Website Builder',
      desc: 'Templates, mapping, and analytics',
      icon: Globe,
      component: ProdModule6Websites,
      color: 'text-amber-400'
    },
    {
      id: 7,
      name: 'Advanced AI Studio',
      desc: 'Draft structured courses via Gemini',
      icon: Brain,
      component: ProdModule7AIStudio,
      color: 'text-purple-400'
    },
    {
      id: 8,
      name: 'Enterprise Mobile API',
      desc: 'Flutter REST sync & push guides',
      icon: Smartphone,
      component: ProdModule8MobileAPI,
      color: 'text-teal-400'
    },
    {
      id: 9,
      name: 'System Monitoring',
      desc: 'Real-time CPU, RAM & Redis status',
      icon: Activity,
      component: ProdModule9Monitoring,
      color: 'text-orange-400'
    },
    {
      id: 10,
      name: 'Production DevOps',
      desc: 'Nginx proxies, backups & restore',
      icon: Sliders,
      component: ProdModule10DevOps,
      color: 'text-pink-400'
    },
    {
      id: 11,
      name: 'Internationalization',
      desc: 'Timezone, languages & RTL support',
      icon: Globe,
      component: ProdModule11I18n,
      color: 'text-indigo-400'
    },
    {
      id: 12,
      name: 'SEO Engine',
      desc: 'OpenGraph, Sitemap XML & Schema.org',
      icon: Search,
      component: ProdModule12SEO,
      color: 'text-emerald-400'
    },
    {
      id: 13,
      name: 'WCAG Accessibility',
      desc: 'Contrast rules & screen reader test',
      icon: Accessibility,
      component: ProdModule13Accessibility,
      color: 'text-amber-400'
    },
    {
      id: 14,
      name: 'Performance Optimization',
      desc: 'Gzip payload & SQL index warmups',
      icon: Zap,
      component: ProdModule14Performance,
      color: 'text-rose-400'
    },
    {
      id: 15,
      name: 'Final Production Audit',
      desc: 'Compliance registers & security scans',
      icon: Award,
      component: ProdModule15Audit,
      color: 'text-indigo-400'
    }
  ];

  const currentModuleList = suiteMode === 'enterprise' ? ENTERPRISE_MODULES : PRODUCTION_MODULES;

  const filteredModules = currentModuleList.filter(m =>
    m.name.toLowerCase().includes(filterQuery.toLowerCase()) ||
    m.desc.toLowerCase().includes(filterQuery.toLowerCase())
  );

  const activeModule = currentModuleList.find(m => m.id === activeModuleId) || currentModuleList[0];
  const ActiveComponent = activeModule.component;

  const handleSuiteModeChange = (mode: 'enterprise' | 'production') => {
    setSuiteMode(mode);
    setActiveModuleId(1);
    setFilterQuery('');
  };

  return (
    <div id="saas-suite-root" className="min-h-screen bg-[#070b19] text-slate-100 flex flex-col">
      {/* SaaS Hub Premium Header */}
      <div className="bg-[#0b1329] border-b border-indigo-950/80 px-6 py-8 shadow-2xl">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="text-left space-y-1">
            <span className="text-[10px] bg-indigo-500/10 text-indigo-400 px-3 py-1 rounded-full border border-indigo-900/40 font-mono uppercase tracking-widest font-black">
              Enterprise Suite v1.KP
            </span>
            <h1 className="text-2xl font-black text-white tracking-tight flex items-center gap-2 mt-1">
              <Layers className="text-indigo-500 w-6 h-6" />
              BrahmaVidya SaaS Hub
            </h1>
            <p className="text-slate-400 text-xs">
              Interact with all 30 business & DevOps modules from our comprehensive system roadmap.
            </p>
          </div>

          <div className="bg-indigo-950/20 border border-indigo-900/40 p-4 rounded-xl flex items-center gap-2 text-xs text-left max-w-md">
            <Info className="text-indigo-400 w-5 h-5 shrink-0" />
            <span className="text-slate-400 leading-relaxed font-sans text-[11px]">
              This control center validates end-to-end user subscription ledgers, collaborative classrooms, and double-entry auditing, fully prepared for actual production integration.
            </span>
          </div>
        </div>

        {/* Dynamic Mode Switcher */}
        <div className="max-w-7xl mx-auto mt-6 flex justify-start">
          <div className="bg-[#050914] border border-indigo-950 p-1.5 rounded-xl flex gap-1">
            <button
              onClick={() => handleSuiteModeChange('enterprise')}
              className={`px-4 py-2 rounded-lg text-xs font-bold font-sans transition flex items-center gap-2 ${suiteMode === 'enterprise' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <Building2 className="w-4 h-4" /> Enterprise Core (15)
            </button>
            <button
              onClick={() => handleSuiteModeChange('production')}
              className={`px-4 py-2 rounded-lg text-xs font-bold font-sans transition flex items-center gap-2 ${suiteMode === 'production' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'}`}
            >
              <Settings className="w-4 h-4" /> Prod Ops & DevOps (15)
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 w-full grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left column sidebar lists */}
        <div className="lg:col-span-4 space-y-4 text-left">
          <div className="bg-[#0b1329] border border-indigo-950/80 rounded-2xl p-4 space-y-4">
            <div className="bg-slate-950/60 border border-slate-900/80 rounded-xl px-3 py-1.5 flex items-center gap-2">
              <Search className="w-4 h-4 text-slate-500 shrink-0" />
              <input
                type="text"
                placeholder={`Search ${suiteMode === 'enterprise' ? 'Enterprise' : 'Production'} Modules...`}
                value={filterQuery}
                onChange={(e) => setFilterQuery(e.target.value)}
                className="bg-transparent border-none text-xs text-white focus:outline-none placeholder-slate-600 w-full font-sans"
              />
            </div>

            <div className="space-y-1 max-h-[500px] overflow-y-auto pr-1">
              {filteredModules.map(m => {
                const IconComp = m.icon;
                const isActive = m.id === activeModuleId;
                return (
                  <button
                    key={m.id}
                    onClick={() => setActiveModuleId(m.id)}
                    className={`w-full flex items-center justify-between p-3 rounded-xl transition group text-left border ${isActive ? 'bg-indigo-950/60 border-indigo-900/50 text-white' : 'bg-transparent border-transparent hover:bg-slate-900/40 text-slate-400 hover:text-slate-200'}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg bg-slate-950 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`}>
                        <IconComp className="w-4 h-4" />
                      </div>
                      <div>
                        <h4 className="text-xs font-black">{m.name}</h4>
                        <p className="text-[10px] text-slate-500 mt-0.5 line-clamp-1 font-sans">{m.desc}</p>
                      </div>
                    </div>
                    <ChevronRight className={`w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition ${isActive ? 'text-indigo-400' : 'text-slate-600'}`} />
                  </button>
                );
              })}
              {filteredModules.length === 0 && (
                <div className="text-center py-8 text-slate-600 text-xs">
                  No matching business modules found.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right column: Dynamic component container */}
        <div className="lg:col-span-8 bg-[#0b1329] border border-indigo-950/80 rounded-2xl p-6 shadow-2xl">
          <div className="border-b border-slate-900/80 pb-4 mb-6 flex justify-between items-center text-left">
            <div>
              <span className="text-[10px] text-indigo-400 font-mono font-bold uppercase tracking-wider">
                {suiteMode === 'enterprise' ? 'Enterprise Core' : 'Prod Ops'} Module {activeModule.id} of 15
              </span>
              <h2 className="text-lg font-black text-white mt-0.5">{activeModule.name}</h2>
            </div>
            <div className="bg-slate-950 px-3 py-1 rounded-xl text-[10px] text-indigo-400 font-mono font-bold border border-slate-900">
              STATE: STANDALONE_PRODUCTION_READY
            </div>
          </div>

          <ActiveComponent />
        </div>
      </div>
    </div>
  );
};

export default SaaSSuiteView;
