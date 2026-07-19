/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { SubscriptionPlan, UserSubscription, SaaSInvoice, SubscriptionPlanType } from './types';
import { CreditCard, Check, Ticket, Award, CheckCircle2, FileText, Percent, Building2 } from 'lucide-react';

const PLANS: SubscriptionPlan[] = [
  {
    id: 'plan-free',
    name: 'FREE',
    priceMonthly: 0,
    priceYearly: 0,
    features: ['Core LMS Access', 'Basic Quizzes', 'Public Discussion Forums', 'Personal Portfolio Site'],
    maxUsers: 1,
    permissions: ['COURSES_READ', 'BOOKS_READ']
  },
  {
    id: 'plan-premium',
    name: 'PREMIUM',
    priceMonthly: 499,
    priceYearly: 4990,
    features: ['All FREE features', 'Ad-Free Content', 'Certified Badges & Certificates', 'Academic Book Store Discount (10%)', 'Vidya AI Guide Basic Mentorship'],
    maxUsers: 1,
    permissions: ['COURSES_READ', 'BOOKS_READ', 'CERTIFICATES_CLAIM', 'AI_TUTOR_BASIC']
  },
  {
    id: 'plan-professional',
    name: 'PROFESSIONAL',
    priceMonthly: 999,
    priceYearly: 9990,
    features: ['All PREMIUM features', 'Live Class Participation', 'Self-Publishing Platform Enabled', 'Royalty Income Share 70%', 'Unlimited Portfolio Sites', 'Vidya AI Premium Assistant (Unlimited)'],
    maxUsers: 1,
    permissions: ['COURSES_READ', 'BOOKS_READ', 'CERTIFICATES_CLAIM', 'AI_TUTOR_UNLIMITED', 'PUBLISH_BOOKS', 'JOIN_LIVE']
  },
  {
    id: 'plan-business',
    name: 'BUSINESS',
    priceMonthly: 2499,
    priceYearly: 24990,
    features: ['All PROFESSIONAL features', 'Organization Onboarding (Up to 15 Members)', 'Dedicated Brand Domain Routing', 'Affiliate Multi-Tier Program', 'Job/Internship Portal Employer Dashboard'],
    maxUsers: 15,
    permissions: ['COURSES_READ', 'BOOKS_READ', 'CERTIFICATES_CLAIM', 'AI_TUTOR_UNLIMITED', 'PUBLISH_BOOKS', 'JOIN_LIVE', 'ORG_CREATE', 'JOB_POST']
  },
  {
    id: 'plan-enterprise',
    name: 'ENTERPRISE',
    priceMonthly: 5999,
    priceYearly: 59990,
    features: ['All BUSINESS features', 'Organization Onboarding (Up to 100 Members)', 'Private Custom Video Streaming Playlists', 'Corporate HR API Integration', 'Dedicated Account Manager'],
    maxUsers: 100,
    permissions: ['COURSES_READ', 'BOOKS_READ', 'CERTIFICATES_CLAIM', 'AI_TUTOR_UNLIMITED', 'PUBLISH_BOOKS', 'JOIN_LIVE', 'ORG_CREATE', 'JOB_POST', 'ENTERPRISE_API']
  },
  {
    id: 'plan-institution',
    name: 'INSTITUTION',
    priceMonthly: 14999,
    priceYearly: 149990,
    features: ['All ENTERPRISE features', 'Unlimited Organization Members', 'Custom Live Stream Infrastructure', 'University Accreditation Integration', 'Audit Trail Logs export'],
    maxUsers: 9999,
    permissions: ['COURSES_READ', 'BOOKS_READ', 'CERTIFICATES_CLAIM', 'AI_TUTOR_UNLIMITED', 'PUBLISH_BOOKS', 'JOIN_LIVE', 'ORG_CREATE', 'JOB_POST', 'ENTERPRISE_API', 'AUDIT_EXPORT']
  }
];

export const Module1Subscriptions: React.FC = () => {
  const { currentUser, refreshProfile } = useAuthStore();
  const [billingCycle, setBillingCycle] = useState<'MONTHLY' | 'YEARLY'>('MONTHLY');
  const [couponCode, setCouponCode] = useState('');
  const [appliedDiscount, setAppliedDiscount] = useState<number>(0);
  const [appliedCode, setAppliedCode] = useState<string>('');
  const [couponError, setCouponError] = useState('');
  const [gstNumber, setGstNumber] = useState('');
  
  // Simulated active subscription state
  const [activeSub, setActiveSub] = useState<UserSubscription>({
    id: 'sub-active-sim',
    userId: currentUser?.id || 'user-student',
    plan: 'FREE',
    billingCycle: 'MONTHLY',
    startDate: new Date().toLocaleDateString(),
    expiryDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
    isActive: true,
    autoRenew: true
  });

  const [invoices, setInvoices] = useState<SaaSInvoice[]>([
    {
      id: 'INV-1092',
      userId: currentUser?.id || 'user-student',
      planName: 'FREE',
      amount: 0,
      gstAmount: 0,
      totalAmount: 0,
      status: 'PAID',
      billingCycle: 'MONTHLY',
      createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toLocaleDateString(),
      pdfUrl: '#'
    }
  ]);

  const [activeInvoice, setActiveInvoice] = useState<SaaSInvoice | null>(null);

  const applyCoupon = () => {
    setCouponError('');
    if (couponCode.toUpperCase() === 'GALAXY50') {
      setAppliedDiscount(50);
      setAppliedCode('GALAXY50');
    } else if (couponCode.toUpperCase() === 'BVIDYA20') {
      setAppliedDiscount(20);
      setAppliedCode('BVIDYA20');
    } else {
      setCouponError('Invalid coupon code. Try "GALAXY50" (50% off) or "BVIDYA20" (20% off).');
    }
  };

  const clearCoupon = () => {
    setAppliedDiscount(0);
    setAppliedCode('');
    setCouponCode('');
  };

  const handleSubscribe = (plan: SubscriptionPlan) => {
    const basePrice = billingCycle === 'MONTHLY' ? plan.priceMonthly : plan.priceYearly;
    const discount = (basePrice * appliedDiscount) / 100;
    const priceAfterDiscount = basePrice - discount;
    const gstAmount = parseFloat((priceAfterDiscount * 0.18).toFixed(2));
    const totalAmount = parseFloat((priceAfterDiscount + gstAmount).toFixed(2));

    const newSub: UserSubscription = {
      id: `sub-${Date.now()}`,
      userId: currentUser?.id || 'user',
      plan: plan.name,
      billingCycle,
      startDate: new Date().toLocaleDateString(),
      expiryDate: new Date(Date.now() + (billingCycle === 'MONTHLY' ? 30 : 365) * 24 * 60 * 60 * 1000).toLocaleDateString(),
      isActive: true,
      autoRenew: true,
      gstNumber: gstNumber || undefined,
      couponApplied: appliedCode || undefined
    };

    const newInvoice: SaaSInvoice = {
      id: `INV-${Math.floor(1000 + Math.random() * 9000)}`,
      userId: currentUser?.id || 'user',
      planName: plan.name,
      amount: priceAfterDiscount,
      gstAmount,
      totalAmount,
      status: 'PAID',
      billingCycle,
      createdAt: new Date().toLocaleDateString(),
      pdfUrl: '#'
    };

    setActiveSub(newSub);
    setInvoices(prev => [newInvoice, ...prev]);
    setActiveInvoice(newInvoice);
  };

  return (
    <div id="saas-module-1" className="space-y-6 text-slate-100">
      {/* Module Title Section */}
      <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CreditCard className="text-indigo-400 w-5 h-5" />
            Subscription & Recurring Billing Management
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            Enterprise grade subscription engine with multi-tier features, recurring cycles, discount coupons, auto-calculated 18% GST tax, and dynamic billing controls.
          </p>
        </div>
        <div className="flex items-center bg-slate-950 p-1 border border-slate-800 rounded-xl">
          <button
            onClick={() => setBillingCycle('MONTHLY')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition ${billingCycle === 'MONTHLY' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('YEARLY')}
            className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1 ${billingCycle === 'YEARLY' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}
          >
            Yearly
            <span className="text-[9px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded-full font-bold">Save 15%</span>
          </button>
        </div>
      </div>

      {/* Coupon & GST Auxiliary Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-4 flex flex-col gap-3">
          <label className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
            <Ticket className="w-3.5 h-3.5 text-indigo-400" />
            Promo / Discount Coupon Code
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder='Try "GALAXY50" or "BVIDYA20"'
              value={couponCode}
              onChange={(e) => setCouponCode(e.target.value)}
              disabled={!!appliedCode}
              className="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
            {appliedCode ? (
              <button onClick={clearCoupon} className="bg-rose-900/40 text-rose-300 hover:bg-rose-900 border border-rose-950 text-xs px-3 py-1.5 rounded-lg transition">
                Remove
              </button>
            ) : (
              <button onClick={applyCoupon} className="bg-indigo-900/40 text-indigo-200 hover:bg-indigo-900 border border-indigo-950 text-xs px-4 py-1.5 rounded-lg transition font-semibold">
                Apply
              </button>
            )}
          </div>
          {couponError && <span className="text-[10px] text-rose-400">{couponError}</span>}
          {appliedCode && (
            <span className="text-[10px] text-emerald-400 flex items-center gap-1">
              <Percent className="w-3 h-3" /> Coupon <strong>{appliedCode}</strong> active ({appliedDiscount}% savings applied!)
            </span>
          )}
        </div>

        <div className="bg-slate-950/40 border border-slate-900 rounded-xl p-4 flex flex-col gap-3">
          <label className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
            <Building2 className="w-3.5 h-3.5 text-indigo-400" />
            Corporate GST Registration Number (Optional)
          </label>
          <input
            type="text"
            placeholder="e.g. 27AADCB2231M1ZP"
            value={gstNumber}
            onChange={(e) => setGstNumber(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 uppercase"
          />
          <span className="text-[9px] text-slate-500 font-mono">
            Adds your business GST tax ID to tax invoices automatically for Input Tax Credit claims.
          </span>
        </div>
      </div>

      {/* Subscription Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {PLANS.map(plan => {
          const isCurrent = activeSub.plan === plan.name && activeSub.isActive;
          const price = billingCycle === 'MONTHLY' ? plan.priceMonthly : plan.priceYearly;
          const discount = (price * appliedDiscount) / 100;
          const finalPrice = price - discount;

          return (
            <div
              key={plan.id}
              className={`border rounded-2xl p-5 flex flex-col relative transition duration-300 ${isCurrent ? 'bg-indigo-950/20 border-indigo-500 shadow-lg shadow-indigo-950/40' : 'bg-slate-950/50 border-slate-900 hover:border-indigo-900/50'}`}
            >
              {isCurrent && (
                <span className="absolute -top-2.5 right-4 bg-indigo-500 text-white text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider">
                  Active Subscription
                </span>
              )}
              
              <div className="mb-4">
                <span className="text-[10px] bg-slate-900 text-slate-400 font-bold px-2 py-0.5 rounded-md uppercase tracking-widest">
                  {plan.name}
                </span>
                <div className="flex items-baseline mt-2 gap-1">
                  <span className="text-2xl font-black text-white">₹{finalPrice.toLocaleString()}</span>
                  {discount > 0 && <span className="text-xs line-through text-slate-500 font-medium">₹{price.toLocaleString()}</span>}
                  <span className="text-slate-500 text-xs font-semibold">/{billingCycle === 'MONTHLY' ? 'mo' : 'yr'}</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Supports up to {plan.maxUsers} organization users.</p>
              </div>

              {/* Action Button */}
              <button
                onClick={() => handleSubscribe(plan)}
                className={`w-full py-2 rounded-xl text-xs font-bold transition mb-5 ${isCurrent ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/50 cursor-default' : 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-md shadow-indigo-950'}`}
                disabled={isCurrent}
              >
                {isCurrent ? 'Your Current Tier' : 'Upgrade to this Tier'}
              </button>

              <hr className="border-slate-900 my-1" />

              {/* Features List */}
              <div className="space-y-2 mt-3 flex-1">
                <span className="text-[10px] text-indigo-400 uppercase tracking-widest font-bold">Includes:</span>
                {plan.features.map((feat, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-xs text-slate-300 text-left">
                    <Check className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                    <span>{feat}</span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Invoices List & active receipt renderer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-4">
        {/* Invoice List */}
        <div className="lg:col-span-5 bg-slate-950/40 border border-slate-900 rounded-2xl p-5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
            <FileText className="text-indigo-400 w-4 h-4" />
            Billing & Invoices History
          </h3>
          <div className="space-y-2">
            {invoices.map((inv) => (
              <div
                key={inv.id}
                onClick={() => setActiveInvoice(inv)}
                className={`flex items-center justify-between p-3 rounded-xl border cursor-pointer transition ${activeInvoice?.id === inv.id ? 'bg-slate-900/80 border-indigo-500' : 'bg-slate-900/30 border-slate-900 hover:border-slate-800'}`}
              >
                <div className="text-left">
                  <span className="text-xs font-bold text-white font-mono">{inv.id}</span>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    {inv.planName} Tier • {inv.createdAt}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-xs font-extrabold text-indigo-400 font-mono">₹{inv.totalAmount.toLocaleString()}</span>
                  <div className="text-[9px] bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded-full font-bold ml-auto mt-0.5 w-fit">
                    PAID
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Invoice Printable View */}
        <div className="lg:col-span-7 bg-slate-900/40 border border-indigo-950/50 rounded-2xl p-6 text-left relative overflow-hidden">
          {activeInvoice ? (
            <div id="saas-invoice-pdf" className="space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="text-base font-black text-white uppercase tracking-wider">BRAHMAVIDYA GALAXY</h4>
                  <p className="text-[10px] text-slate-400 font-mono mt-0.5">VAT/GST-ID: IN27AADCB2231M1ZP</p>
                  <p className="text-[9px] text-slate-500 max-w-xs mt-1">108 Cosmic Knowledge Tower, Outer Space Ring, Sector V, Pune, India.</p>
                </div>
                <div className="text-right">
                  <span className="text-xs bg-indigo-500/20 text-indigo-300 font-black px-2.5 py-1 rounded-md font-mono">
                    TAX INVOICE
                  </span>
                  <p className="text-xs text-slate-400 font-mono mt-2">ID: {activeInvoice.id}</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Date: {activeInvoice.createdAt}</p>
                </div>
              </div>

              <hr className="border-slate-800" />

              <div className="grid grid-cols-2 gap-4 text-xs text-slate-300 font-mono">
                <div>
                  <strong className="block text-[10px] text-slate-500 uppercase">Billed To:</strong>
                  <span className="block font-bold text-white mt-1">{currentUser?.fullName || 'Rahul Sharma'}</span>
                  <span className="block text-slate-400 text-[10px] mt-0.5">{currentUser?.email || 'student@brahmavidya.edu'}</span>
                  {activeSub.gstNumber && <span className="block text-indigo-400 text-[10px] mt-1 font-bold">GSTIN: {activeSub.gstNumber}</span>}
                </div>
                <div>
                  <strong className="block text-[10px] text-slate-500 uppercase">Payment Terms:</strong>
                  <span className="block mt-1">SaaS Recurring Ledger Debit</span>
                  <span className="block text-[10px] text-slate-400 mt-0.5">Billing Cycle: {activeInvoice.billingCycle}</span>
                  <span className="block text-[10px] text-slate-400">Status: <span className="text-emerald-400 font-bold">PAID (SUCCESS)</span></span>
                </div>
              </div>

              <div className="border border-slate-800 rounded-xl overflow-hidden mt-4">
                <table className="w-full text-xs font-mono">
                  <thead>
                    <tr className="bg-slate-950 text-slate-400 border-b border-slate-800 text-left">
                      <th className="p-3">Description</th>
                      <th className="p-3 text-right">Rate</th>
                      <th className="p-3 text-right">Tax (18% GST)</th>
                      <th className="p-3 text-right">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-300">
                    <tr className="border-b border-slate-800/50">
                      <td className="p-3 font-semibold">
                        {activeInvoice.planName} SaaS Plan Subscription Upgrade
                        <div className="text-[10px] text-slate-500 mt-0.5">Recurring digital licensing model</div>
                      </td>
                      <td className="p-3 text-right">₹{activeInvoice.amount.toLocaleString()}</td>
                      <td className="p-3 text-right">₹{activeInvoice.gstAmount.toLocaleString()}</td>
                      <td className="p-3 text-right font-bold text-white">₹{activeInvoice.totalAmount.toLocaleString()}</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="flex justify-end pt-2">
                <div className="w-64 space-y-1.5 font-mono text-xs">
                  <div className="flex justify-between text-slate-400">
                    <span>Subtotal:</span>
                    <span>₹{activeInvoice.amount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>CGST (9%):</span>
                    <span>₹{(activeInvoice.gstAmount / 2).toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>SGST (9%):</span>
                    <span>₹{(activeInvoice.gstAmount / 2).toLocaleString()}</span>
                  </div>
                  <hr className="border-slate-800 my-1" />
                  <div className="flex justify-between text-white font-extrabold text-sm">
                    <span>Total Amount:</span>
                    <span>₹{activeInvoice.totalAmount.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="text-center text-[9px] text-slate-600 font-mono mt-4 pt-4 border-t border-slate-850">
                This is a computer-generated tax invoice verified by BrahmaVidya Galaxy Ledger. No physical signature is required.
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 py-12">
              <FileText className="w-12 h-12 text-slate-700 stroke-[1.5] mb-2 animate-pulse" />
              <p className="text-xs">Select an invoice from the history ledger to view detailed breakdown, GST details, and tax summaries.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Module1Subscriptions;
