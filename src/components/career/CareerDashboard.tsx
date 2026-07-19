/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { StatsCard, ChartsWrapper, DataTable, Badge } from '../DesignSystem';
import { Briefcase, Award, TrendingUp, Compass, Calendar, ArrowRight, ShieldCheck } from 'lucide-react';

export const CareerDashboard: React.FC = () => {
  return (
    <div className="space-y-8 text-left">
      
      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <StatsCard label="Resume Completion" value="85%" change="Missing Certifications" />
        <StatsCard label="Portfolio Published" value="Active" change="Custom domain ready" />
        <StatsCard label="Applications Sent" value="12 Sent" change="3 Under Review" isPositive={true} />
        <StatsCard label="Interview Invites" value="2 Invited" change="Vedic Math Tutor role" isPositive={true} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Career Timeline Roadmap */}
        <div className="lg:col-span-8 space-y-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Compass size={14} className="text-indigo-400" /> AI Skill Learning Roadmap
          </h4>
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-6">
            <div className="flex gap-4 relative">
              <div className="absolute top-8 left-4.5 bottom-0 w-0.5 bg-indigo-950"></div>
              <div className="p-2.5 bg-indigo-950 text-indigo-400 rounded-full h-fit z-10"><Award size={14} /></div>
              <div>
                <strong className="block text-xs text-white">Vedic Mathematics Certification</strong>
                <span className="block text-[10px] text-slate-500 font-mono mt-0.5">EST DATE: JULY 2026 // RECOMMENDED</span>
                <p className="text-xs text-slate-400 leading-relaxed mt-1">Acquiring this certification boosts your match score for teaching vacancies by 35%.</p>
              </div>
            </div>
            
            <div className="flex gap-4">
              <div className="p-2.5 bg-slate-950 border border-indigo-950 text-slate-500 rounded-full h-fit"><Briefcase size={14} /></div>
              <div>
                <strong className="block text-xs text-slate-350">Django DB partitions internship</strong>
                <span className="block text-[10px] text-slate-600 font-mono mt-0.5">EST DATE: AUGUST 2026</span>
              </div>
            </div>
          </div>
        </div>

        {/* Certifications Verification logs */}
        <div className="lg:col-span-4 space-y-4">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <ShieldCheck size={14} className="text-indigo-400" /> Completed Diplomas
          </h4>
          <div className="p-6 bg-slate-900 border border-indigo-950 rounded-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-indigo-950/45 pb-3">
              <div className="text-xs">
                <strong className="block text-white leading-tight">SaaS Performance</strong>
                <span className="text-[9px] text-slate-500 font-mono">BVG-LDR-77</span>
              </div>
              <Badge variant="success">Verified</Badge>
            </div>
            <div className="flex justify-between items-center">
              <div className="text-xs">
                <strong className="block text-slate-350 leading-tight">Advanced Celery Tasks</strong>
                <span className="text-[9px] text-slate-500 font-mono">BVG-LDR-41</span>
              </div>
              <Badge variant="success">Verified</Badge>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default CareerDashboard;
