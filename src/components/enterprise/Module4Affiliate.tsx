/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { AffiliateProfile, ReferralReward } from './types';
import { Share2, Users, Wallet, Trophy, Clipboard, CheckCircle, Percent, ArrowRight } from 'lucide-react';

export const Module4Affiliate: React.FC = () => {
  const { currentUser } = useAuthStore();
  
  const [profile, setProfile] = useState<AffiliateProfile>({
    userId: currentUser?.id || 'user-student',
    referralCode: `${currentUser?.fullName.split(' ')[0].toUpperCase() || 'RAHUL'}99`,
    referralLink: `https://brahmavidya.edu/ref=${currentUser?.fullName.split(' ')[0].toLowerCase() || 'rahul'}99`,
    commissionWalletBalance: 1240,
    referredCount: 14,
    totalEarnings: 8450,
    tierLevel: 2
  });

  const [rewards, setRewards] = useState<ReferralReward[]>([
    {
      id: 'RWD-8812',
      referrerId: currentUser?.id || 'user-student',
      refereeName: 'Priyesh Pandey',
      planPurchased: 'PROFESSIONAL',
      commissionAmount: 999, // 10% of annual 9990 or monthly etc
      tierLevel: 1, // Direct referral
      status: 'PAID',
      createdAt: '2026-07-06'
    },
    {
      id: 'RWD-8813',
      referrerId: currentUser?.id || 'user-student',
      refereeName: 'Komal Gupta (referred by Priyesh)',
      planPurchased: 'BUSINESS',
      commissionAmount: 1249, // 5% tier 2 reward on Business
      tierLevel: 2, // Second level referral
      status: 'PAID',
      createdAt: '2026-07-04'
    },
    {
      id: 'RWD-8814',
      referrerId: currentUser?.id || 'user-student',
      refereeName: 'Sanjay Dutt',
      planPurchased: 'PREMIUM',
      commissionAmount: 49.9,
      tierLevel: 1,
      status: 'PENDING',
      createdAt: '2026-07-07'
    }
  ]);

  const [copied, setCopied] = useState(false);
  const [withdrawing, setWithdrawing] = useState(false);
  const [withdrawnSuccess, setWithdrawnSuccess] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(profile.referralLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const triggerWithdraw = () => {
    if (profile.commissionWalletBalance <= 0) return;
    setWithdrawing(true);
    setTimeout(() => {
      setProfile(prev => ({ ...prev, commissionWalletBalance: 0 }));
      setWithdrawing(false);
      setWithdrawnSuccess(true);
      setTimeout(() => setWithdrawnSuccess(false), 3000);
    }, 1500);
  };

  return (
    <div id="saas-module-4" className="space-y-6 text-slate-100">
      {/* Banner */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Share2 className="text-indigo-400 w-5 h-5" />
            Affiliate Marketing & Multi-Level Referral Rewards
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Grow BV Galaxy, earn money. Every student, teacher, or organization possesses a personalized referral system with level-based compounding rewards: 10% on direct signups (Tier 1), 5% on secondary (Tier 2), and 2% on tertiary (Tier 3).
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left column: Code Generator & Commission Wallet */}
        <div className="space-y-6 lg:col-span-1">
          {/* Referral links card */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Share2 className="w-4 h-4 text-indigo-400" />
              Your Shareable Referrals
            </h3>

            <div>
              <label className="block text-[10px] text-slate-500 uppercase font-bold mb-1">Referral Code</label>
              <div className="bg-slate-900 border border-slate-800 text-white font-mono text-sm px-3 py-1.5 rounded-lg w-fit font-black tracking-widest">
                {profile.referralCode}
              </div>
            </div>

            <div>
              <label className="block text-[10px] text-slate-500 uppercase font-bold mb-1">Referral Link</label>
              <div className="flex gap-2">
                <input
                  type="text"
                  readOnly
                  value={profile.referralLink}
                  className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 font-mono focus:outline-none"
                />
                <button
                  onClick={copyToClipboard}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white p-2 rounded-lg transition"
                >
                  {copied ? <CheckCircle className="w-4 h-4" /> : <Clipboard className="w-4 h-4" />}
                </button>
              </div>
              {copied && <span className="text-[10px] text-emerald-400 mt-1 block">Copied link to clipboard!</span>}
            </div>
          </div>

          {/* Commission Wallet */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left space-y-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Wallet className="w-4 h-4 text-indigo-400" />
              Commission Wallet balance
            </h3>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-black text-white font-mono">₹{profile.commissionWalletBalance.toLocaleString()}</span>
              <span className="text-slate-500 text-xs">INR Available</span>
            </div>
            
            <button
              onClick={triggerWithdraw}
              disabled={profile.commissionWalletBalance <= 0 || withdrawing}
              className={`w-full py-2 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 ${profile.commissionWalletBalance <= 0 ? 'bg-slate-900 text-slate-500 cursor-not-allowed' : 'bg-emerald-600 text-white hover:bg-emerald-500 shadow-md shadow-emerald-950'}`}
            >
              <Wallet className="w-4 h-4" /> {withdrawing ? 'Settling Transfer...' : 'Payout to Academic Wallet'}
            </button>
            {withdrawnSuccess && (
              <span className="text-[10px] text-emerald-400 block text-center font-bold">
                Success! ₹1,240 has been transferred into your core Academic Wallet balance.
              </span>
            )}
          </div>
        </div>

        {/* Center/Right Columns: Referral Analytics & Levels rewards */}
        <div className="lg:col-span-2 space-y-6">
          {/* Multi-Level compounding rewards schema */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
              <Trophy className="w-4 h-4 text-indigo-400" />
              Multi-Tier Compounding Commissions Structure
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl flex items-center gap-3">
                <div className="bg-indigo-500/10 p-2.5 rounded-lg text-indigo-400 font-black text-lg">
                  10%
                </div>
                <div>
                  <span className="block font-bold text-white text-xs">Direct (Level 1)</span>
                  <span className="block text-[10px] text-slate-400">Signups using code</span>
                </div>
              </div>

              <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl flex items-center gap-3">
                <div className="bg-emerald-500/10 p-2.5 rounded-lg text-emerald-400 font-black text-lg">
                  5%
                </div>
                <div>
                  <span className="block font-bold text-white text-xs">Indirect (Level 2)</span>
                  <span className="block text-[10px] text-slate-400">Referred by your refs</span>
                </div>
              </div>

              <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl flex items-center gap-3">
                <div className="bg-amber-500/10 p-2.5 rounded-lg text-amber-400 font-black text-lg">
                  2%
                </div>
                <div>
                  <span className="block font-bold text-white text-xs">Sub-Indirect (Level 3)</span>
                  <span className="block text-[10px] text-slate-400">Extended line signups</span>
                </div>
              </div>
            </div>
          </div>

          {/* Referral Analytics & activity table */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Analytics Counters */}
            <div className="md:col-span-5 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left flex flex-col justify-between">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                <Users className="w-4 h-4 text-indigo-400" />
                Referral Analytics
              </h3>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center bg-slate-900/40 p-3 rounded-xl border border-slate-850/60">
                  <span className="text-xs text-slate-400">Total Referred Users:</span>
                  <span className="text-sm font-black text-white font-mono">{profile.referredCount}</span>
                </div>
                <div className="flex justify-between items-center bg-slate-900/40 p-3 rounded-xl border border-slate-850/60">
                  <span className="text-xs text-slate-400">Direct Converts (Level 1):</span>
                  <span className="text-sm font-black text-white font-mono">11</span>
                </div>
                <div className="flex justify-between items-center bg-slate-900/40 p-3 rounded-xl border border-slate-850/60">
                  <span className="text-xs text-slate-400">Cumulative Earned (INR):</span>
                  <span className="text-sm font-black text-emerald-400 font-mono">₹{profile.totalEarnings.toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Commissions log */}
            <div className="md:col-span-7 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 text-left">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                <Trophy className="w-4 h-4 text-indigo-400" />
                Recent Commissions Log
              </h3>
              <div className="space-y-2 max-h-[180px] overflow-y-auto pr-1">
                {rewards.map(r => (
                  <div key={r.id} className="bg-slate-900/40 border border-slate-850 p-2.5 rounded-xl flex items-center justify-between">
                    <div className="text-left font-mono">
                      <span className="block font-sans font-bold text-slate-200 text-xs truncate max-w-[150px]">{r.refereeName}</span>
                      <span className="block text-[9px] text-slate-500 mt-0.5">Level {r.tierLevel} Referral • {r.planPurchased} plan</span>
                    </div>
                    <div className="text-right">
                      <span className="block text-xs font-bold font-mono text-emerald-400">+₹{r.commissionAmount}</span>
                      {r.status === 'PENDING' ? (
                        <span className="text-[8px] bg-amber-500/10 text-amber-400 px-1 py-0.2 rounded-full font-bold">PENDING</span>
                      ) : (
                        <span className="text-[8px] bg-emerald-500/10 text-emerald-400 px-1 py-0.2 rounded-full font-bold">SETTLED</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Module4Affiliate;
