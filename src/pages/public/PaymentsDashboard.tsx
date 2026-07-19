import React, { useState, useEffect } from 'react';
import {
  Wallet as WalletIcon,
  CreditCard,
  History,
  Layers,
  FileText,
  Tag,
  DollarSign,
  ArrowRightLeft,
  TrendingUp,
  Share2,
  CheckCircle,
  AlertCircle,
  Download,
  Percent,
  PlusCircle,
  ArrowUpRight,
  ArrowDownCircle,
  UserPlus
} from 'lucide-react';
import { paymentsApi } from '../../services/paymentsApi';

interface PaymentsDashboardProps {
  currentUser?: any;
  onRefreshWallet?: () => void;
}

export const PaymentsDashboard: React.FC<PaymentsDashboardProps> = ({ currentUser, onRefreshWallet }) => {
  const [activeTab, setActiveTab] = useState<string>('wallet');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // States for sub-components
  const [walletBalance, setWalletBalance] = useState<string>('0.00');
  const [transactions, setTransactions] = useState<any[]>([]);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [payouts, setPayouts] = useState<any[]>([]);
  const [activeSub, setActiveSub] = useState<any>(null);
  const [revenueSummary, setRevenueSummary] = useState<any>(null);
  const [coupons, setCoupons] = useState<any[]>([]);

  // Add Funds form
  const [addFundsAmount, setAddFundsAmount] = useState<string>('');
  // Transfer form
  const [transferTarget, setTransferTarget] = useState<string>('');
  const [transferAmount, setTransferAmount] = useState<string>('');
  const [transferDesc, setTransferDesc] = useState<string>('');

  // Checkout Page states
  const [checkoutAmount, setCheckoutAmount] = useState<string>('999.00');
  const [couponCode, setCouponCode] = useState<string>('');
  const [appliedCoupon, setAppliedCoupon] = useState<any>(null);
  const [checkoutDiscount, setCheckoutDiscount] = useState<string>('0.00');
  const [checkoutFinal, setCheckoutFinal] = useState<string>('999.00');
  const [gstAmount, setGstAmount] = useState<string>('152.39');
  const [gstBase, setGstBase] = useState<string>('846.61');

  // Coupon validation
  const [valCouponCode, setValCouponCode] = useState<string>('');
  const [validatedRes, setValidatedRes] = useState<any>(null);

  // Payout request form
  const [payoutAmount, setPayoutAmount] = useState<string>('');
  const [payoutMethod, setPayoutMethod] = useState<string>('BANK_TRANSFER');

  // Invoice view details
  const [selectedInvoice, setSelectedInvoice] = useState<any>(null);

  // Load active tab data
  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (activeTab === 'wallet' || activeTab === 'history') {
        const txs = await paymentsApi.transactions.list();
        setTransactions(txs);
        // Try getting active wallet balance if currentUser wallet exists
        if (currentUser?.wallet_id) {
          const bal = await paymentsApi.wallet.getBalance(currentUser.wallet_id);
          setWalletBalance(bal.balance || '0.00');
        } else {
          setWalletBalance('500.00'); // Mocked fallback
        }
      } else if (activeTab === 'subscriptions') {
        const sub = await paymentsApi.subscriptions.getCurrent();
        setActiveSub(sub);
      } else if (activeTab === 'invoices') {
        const invs = await paymentsApi.invoices.list();
        setInvoices(invs);
      } else if (activeTab === 'earnings') {
        const pay = await paymentsApi.payouts.list();
        setPayouts(pay);
      } else if (activeTab === 'coupons') {
        const cps = await paymentsApi.coupons.list();
        setCoupons(cps);
      } else if (activeTab === 'revenue') {
        const rev = await paymentsApi.revenue.getSummary();
        setRevenueSummary(rev);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to fetch resource.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddFunds = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!addFundsAmount) return;
    setError(null);
    setSuccess(null);
    try {
      const wId = currentUser?.wallet_id || 'default-wallet-id';
      await paymentsApi.wallet.addFunds(wId, parseFloat(addFundsAmount));
      setSuccess(`Successfully credited ₹${addFundsAmount} to wallet.`);
      setAddFundsAmount('');
      loadData();
      if (onRefreshWallet) onRefreshWallet();
    } catch (err: any) {
      setError(err.message || 'Add funds failed.');
    }
  };

  const handleTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transferTarget || !transferAmount) return;
    setError(null);
    setSuccess(null);
    try {
      await paymentsApi.wallet.transfer(transferTarget, parseFloat(transferAmount), transferDesc || 'Peer Transfer');
      setSuccess(`Transferred ₹${transferAmount} to target wallet successfully.`);
      setTransferTarget('');
      setTransferAmount('');
      setTransferDesc('');
      loadData();
      if (onRefreshWallet) onRefreshWallet();
    } catch (err: any) {
      setError(err.message || 'Transfer failed.');
    }
  };

  const handleValidateCoupon = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!valCouponCode) return;
    setError(null);
    setValidatedRes(null);
    try {
      const res = await paymentsApi.coupons.validate(valCouponCode, 1000);
      setValidatedRes(res);
    } catch (err: any) {
      setError(err.message || 'Coupon validation failed.');
    }
  };

  const handleApplyCheckoutCoupon = async () => {
    if (!couponCode) return;
    setError(null);
    try {
      const res = await paymentsApi.coupons.apply(couponCode, parseFloat(checkoutAmount));
      setAppliedCoupon(res);
      setCheckoutDiscount(res.calculated_discount);
      const finalAmt = parseFloat(res.final_amount);
      setCheckoutFinal(res.final_amount);
      // Recalculate GST split (18% inclusive)
      const base = finalAmt / 1.18;
      setGstBase(base.toFixed(2));
      setGstAmount((finalAmt - base).toFixed(2));
      setSuccess('Coupon code applied successfully!');
    } catch (err: any) {
      setError(err.message || 'Coupon apply failed.');
    }
  };

  const handlePayCheckout = async () => {
    setError(null);
    setSuccess(null);
    try {
      const pmt = await paymentsApi.payments.create(parseFloat(checkoutFinal));
      await paymentsApi.payments.verify(pmt.id, `STRIPE-${Date.now()}`);
      setSuccess('Payment processed and verified successfully! Invoice created.');
      setActiveTab('invoices');
    } catch (err: any) {
      setError(err.message || 'Checkout failed.');
    }
  };

  const handleSubscribe = async (planName: string, price: number) => {
    setError(null);
    setSuccess(null);
    try {
      await paymentsApi.subscriptions.subscribe(planName, price);
      setSuccess(`Subscribed to ${planName} tier!`);
      loadData();
    } catch (err: any) {
      setError(err.message || 'Subscription failed.');
    }
  };

  const handleCancelSub = async (id: string) => {
    setError(null);
    try {
      await paymentsApi.subscriptions.cancel(id);
      setSuccess('Subscription cancelled.');
      loadData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handlePayoutRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!payoutAmount) return;
    setError(null);
    setSuccess(null);
    try {
      await paymentsApi.payouts.request(parseFloat(payoutAmount), payoutMethod);
      setSuccess('Payout withdrawal request submitted successfully.');
      setPayoutAmount('');
      loadData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        
        {/* Header Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-indigo-400">
              Payments & Ledger Dashboard
            </h1>
            <p className="text-slate-400 mt-1">
              Manage your student wallets, subscriptions, payout logs, coupons, and invoicing.
            </p>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 flex items-center gap-3">
            <WalletIcon className="text-sky-400 w-6 h-6 animate-pulse" />
            <div>
              <span className="text-xs text-slate-400 uppercase tracking-wider block">Wallet Balance</span>
              <span className="text-xl font-mono font-bold text-sky-400">₹{walletBalance}</span>
            </div>
          </div>
        </div>

        {/* Global Notifications */}
        {error && (
          <div className="bg-rose-950/50 border border-rose-800 rounded-lg p-4 flex items-center gap-3 text-rose-200">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}
        {success && (
          <div className="bg-emerald-950/50 border border-emerald-800 rounded-lg p-4 flex items-center gap-3 text-emerald-200">
            <CheckCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{success}</p>
          </div>
        )}

        {/* Dynamic Navigation Tabs */}
        <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3">
          {[
            { id: 'wallet', label: 'Wallet', icon: WalletIcon },
            { id: 'history', label: 'Ledger History', icon: History },
            { id: 'checkout', label: 'Checkout Page', icon: CreditCard },
            { id: 'subscriptions', label: 'Subscriptions', icon: Layers },
            { id: 'invoices', label: 'Invoices', icon: FileText },
            { id: 'coupons', label: 'Coupons Engine', icon: Tag },
            { id: 'earnings', label: 'Teacher Payouts', icon: DollarSign },
            { id: 'revenue', label: 'Analytics Panel', icon: TrendingUp },
            { id: 'referrals', label: 'Referrals', icon: Share2 }
          ].map(tab => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? 'bg-sky-500 text-slate-900 shadow-lg shadow-sky-500/20 font-bold scale-105'
                    : 'bg-slate-800 hover:bg-slate-750 text-slate-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Body Contents */}
        {loading ? (
          <div className="h-64 flex flex-col items-center justify-center gap-3">
            <div className="w-10 h-10 border-4 border-sky-400/30 border-t-sky-400 rounded-full animate-spin"></div>
            <p className="text-slate-400 text-sm">Synchronizing ledger states...</p>
          </div>
        ) : (
          <div className="bg-slate-950/40 border border-slate-850 rounded-2xl p-6 min-h-[350px]">
            
            {/* 1. Wallet Dashboard */}
            {activeTab === 'wallet' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Deposit Section */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h3 className="text-lg font-bold flex items-center gap-2 text-sky-400">
                    <PlusCircle className="w-5 h-5" /> Deposit Funds
                  </h3>
                  <p className="text-slate-400 text-xs">
                    Authorize adding mock points to credit your virtual dashboard ledger immediately.
                  </p>
                  <form onSubmit={handleAddFunds} className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Deposit Amount (INR)</label>
                      <input
                        type="number"
                        placeholder="e.g. 500"
                        value={addFundsAmount}
                        onChange={e => setAddFundsAmount(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                      />
                    </div>
                    <button
                      type="submit"
                      className="w-full bg-sky-500 hover:bg-sky-400 text-slate-900 font-bold py-2 rounded-lg text-sm transition-colors"
                    >
                      Authorize Credit
                    </button>
                  </form>
                </div>

                {/* Peer Transfer */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h3 className="text-lg font-bold flex items-center gap-2 text-indigo-400">
                    <ArrowRightLeft className="w-5 h-5" /> Transfer Funds
                  </h3>
                  <p className="text-slate-400 text-xs">
                    Transfer points securely to another student email or wallet ID instantly.
                  </p>
                  <form onSubmit={handleTransfer} className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Target Wallet ID / User ID</label>
                      <input
                        type="text"
                        placeholder="UUID format target"
                        value={transferTarget}
                        onChange={e => setTransferTarget(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Amount (INR)</label>
                      <input
                        type="number"
                        placeholder="e.g. 200"
                        value={transferAmount}
                        onChange={e => setTransferAmount(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Remarks / Remarks memo</label>
                      <input
                        type="text"
                        placeholder="e.g. Book share"
                        value={transferDesc}
                        onChange={e => setTransferDesc(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                      />
                    </div>
                    <button
                      type="submit"
                      className="w-full bg-indigo-500 hover:bg-indigo-400 text-slate-100 font-bold py-2 rounded-lg text-sm transition-colors"
                    >
                      Initialize Transfer
                    </button>
                  </form>
                </div>
              </div>
            )}

            {/* 2. Ledger History */}
            {activeTab === 'history' && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-slate-200">Ledger Statement & Purchases</h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-left text-sm text-slate-350">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                        <th className="py-3 px-4">Tx ID</th>
                        <th className="py-3 px-4">Direction</th>
                        <th className="py-3 px-4">Description</th>
                        <th className="py-3 px-4">Amount</th>
                        <th className="py-3 px-4">Issued At</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-850">
                      {transactions.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="py-8 text-center text-slate-500">
                            No ledger transitions found in transaction history.
                          </td>
                        </tr>
                      ) : (
                        transactions.map(tx => (
                          <tr key={tx.id} className="hover:bg-slate-900/30">
                            <td className="py-3.5 px-4 font-mono text-xs">{tx.id.substring(0, 8)}...</td>
                            <td className="py-3.5 px-4">
                              {tx.type === 'CREDIT' ? (
                                <span className="inline-flex items-center gap-1 text-emerald-400 font-bold text-xs bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-900/50">
                                  <ArrowUpRight className="w-3.5 h-3.5" /> Credit
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 text-rose-400 font-bold text-xs bg-rose-950/40 px-2 py-0.5 rounded border border-rose-900/50">
                                  <ArrowDownCircle className="w-3.5 h-3.5" /> Debit
                                </span>
                              )}
                            </td>
                            <td className="py-3.5 px-4 text-slate-300">{tx.description}</td>
                            <td className="py-3.5 px-4 font-mono font-bold text-slate-100">₹{tx.amount}</td>
                            <td className="py-3.5 px-4 text-xs text-slate-500">{new Date(tx.created_at).toLocaleDateString()}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 3. Checkout Page */}
            {activeTab === 'checkout' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Checkout billing details */}
                <div className="lg:col-span-2 bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h3 className="text-lg font-bold text-slate-200">Billing Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Cardholder Name</label>
                      <input
                        type="text"
                        defaultValue={currentUser?.name || 'Jane Doe'}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-300"
                        readOnly
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Billing Email</label>
                      <input
                        type="text"
                        defaultValue={currentUser?.email || 'jane@brahmavidya.edu'}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-300"
                        readOnly
                      />
                    </div>
                  </div>

                  <div className="space-y-2 pt-2">
                    <label className="text-xs text-slate-400 block">Payment Mock Gateway</label>
                    <div className="flex gap-4">
                      <label className="flex items-center gap-2 cursor-pointer text-sm">
                        <input type="radio" name="checkout_gw" defaultChecked className="text-sky-500" /> Stripe Mock
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer text-sm">
                        <input type="radio" name="checkout_gw" className="text-sky-500" /> Razorpay Mock
                      </label>
                    </div>
                  </div>

                  <button
                    onClick={handlePayCheckout}
                    className="w-full bg-sky-500 hover:bg-sky-400 text-slate-900 font-extrabold py-3 rounded-xl transition-colors mt-4 text-center block"
                  >
                    Confirm Order Payment (₹{checkoutFinal})
                  </button>
                </div>

                {/* Order Summary & Coupon code application */}
                <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 flex flex-col justify-between space-y-6">
                  <div>
                    <h3 className="text-lg font-bold border-b border-slate-800 pb-3 text-slate-200">Order Summary</h3>
                    
                    <div className="space-y-3 mt-4 text-sm text-slate-350">
                      <div className="flex justify-between">
                        <span>LMS Course Bundle:</span>
                        <span className="font-mono text-slate-200">₹{checkoutAmount}</span>
                      </div>
                      
                      {appliedCoupon && (
                        <div className="flex justify-between text-emerald-400 text-xs">
                          <span>Discount Applied ({appliedCoupon.code}):</span>
                          <span className="font-mono">-₹{checkoutDiscount}</span>
                        </div>
                      )}

                      <div className="border-t border-slate-800 pt-3 space-y-1.5 text-xs text-slate-400">
                        <div className="flex justify-between">
                          <span>Base Price:</span>
                          <span className="font-mono">₹{gstBase}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>GST (18% inclusive):</span>
                          <span className="font-mono">₹{gstAmount}</span>
                        </div>
                      </div>

                      <div className="border-t border-slate-800 pt-3 flex justify-between text-base font-extrabold text-sky-400">
                        <span>Total Checkout:</span>
                        <span className="font-mono">₹{checkoutFinal}</span>
                      </div>
                    </div>
                  </div>

                  {/* Coupon Apply Form */}
                  <div className="space-y-2 border-t border-slate-800 pt-4">
                    <label className="text-xs text-slate-400 block">Promo Code</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="ENTER CODE"
                        value={couponCode}
                        onChange={e => setCouponCode(e.target.value)}
                        className="bg-slate-950 border border-slate-750 rounded-lg px-3 py-1.5 text-sm uppercase text-slate-200 w-full"
                      />
                      <button
                        onClick={handleApplyCheckoutCoupon}
                        className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
                      >
                        Apply
                      </button>
                    </div>
                  </div>

                </div>
              </div>
            )}

            {/* 4. Subscription Plans */}
            {activeTab === 'subscriptions' && (
              <div className="space-y-6">
                
                {/* Active Sub description */}
                {activeSub ? (
                  <div className="bg-gradient-to-r from-sky-950/20 to-indigo-950/20 border border-sky-900/40 rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <span className="text-xs font-extrabold uppercase text-sky-400 tracking-widest bg-sky-950 px-2 py-0.5 rounded">Active Plan</span>
                      <h4 className="text-2xl font-bold mt-1 text-slate-200">{activeSub.plan_name}</h4>
                      <p className="text-slate-400 text-xs mt-1">
                        Subscription details: expires on {new Date(activeSub.expires_at).toLocaleDateString()}.
                      </p>
                    </div>
                    <button
                      onClick={() => handleCancelSub(activeSub.id)}
                      className="bg-rose-900/60 hover:bg-rose-800 text-rose-100 text-xs font-bold px-4 py-2 rounded-lg border border-rose-850 transition-all"
                    >
                      Cancel Membership
                    </button>
                  </div>
                ) : (
                  <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center text-sm text-slate-400">
                    No subscription registered yet. Defaulting to Free Tier.
                  </div>
                )}

                {/* Sub plans options */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
                  {[
                    { name: 'Student Premium', price: 99, desc: 'Ideal for access to live classroom replay tracks and certificates.' },
                    { name: 'Teacher Premium', price: 299, desc: 'Expands custom whiteboards, poll controls, and attendance archives.' },
                    { name: 'Institute Bundle', price: 999, desc: 'Centralized admin controls for colleges, departments, and cohorts.' }
                  ].map(p => (
                    <div key={p.name} className="bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all rounded-xl p-6 flex flex-col justify-between space-y-4">
                      <div>
                        <h4 className="text-lg font-bold text-slate-200">{p.name}</h4>
                        <div className="my-2">
                          <span className="text-3xl font-extrabold text-sky-400">₹{p.price}</span>
                          <span className="text-slate-500 text-xs">/month</span>
                        </div>
                        <p className="text-slate-400 text-xs">{p.desc}</p>
                      </div>
                      <button
                        onClick={() => handleSubscribe(p.name, p.price)}
                        className="w-full bg-slate-800 hover:bg-sky-500 hover:text-slate-900 text-slate-200 font-bold py-2 rounded-lg text-xs transition-all"
                      >
                        Choose Tier Plan
                      </button>
                    </div>
                  ))}
                </div>

              </div>
            )}

            {/* 5. Invoices List */}
            {activeTab === 'invoices' && (
              <div className="space-y-4">
                <h3 className="text-lg font-bold text-slate-200">Invoice Registry</h3>
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse text-left text-sm text-slate-350">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase text-xs tracking-wider">
                        <th className="py-3 px-4">Invoice #</th>
                        <th className="py-3 px-4">Base Amount</th>
                        <th className="py-3 px-4">GST Tax</th>
                        <th className="py-3 px-4">Grand Total</th>
                        <th className="py-3 px-4">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-850">
                      {invoices.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="py-8 text-center text-slate-500">
                            No billing invoice sheets found.
                          </td>
                        </tr>
                      ) : (
                        invoices.map(inv => (
                          <tr key={inv.id} className="hover:bg-slate-900/30">
                            <td className="py-3.5 px-4 font-mono text-xs">{inv.invoice_number}</td>
                            <td className="py-3.5 px-4">₹{inv.amount}</td>
                            <td className="py-3.5 px-4 text-xs">₹{inv.tax}</td>
                            <td className="py-3.5 px-4 font-mono font-bold text-slate-200">₹{inv.total}</td>
                            <td className="py-3.5 px-4 flex gap-2">
                              <a
                                href={paymentsApi.invoices.downloadUrl(inv.id)}
                                download
                                className="inline-flex items-center gap-1 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-xs transition-colors"
                              >
                                <Download className="w-3.5 h-3.5" /> Download TXT
                              </a>
                              <button
                                onClick={() => setSelectedInvoice(inv)}
                                className="bg-sky-500/20 border border-sky-500/30 hover:bg-sky-500 hover:text-slate-900 text-sky-400 px-3 py-1.5 rounded-lg text-xs font-bold transition-all"
                              >
                                Quick View
                              </button>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Quick View invoice contents overlay */}
                {selectedInvoice && (
                  <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 max-w-lg w-full space-y-4">
                      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                        <h4 className="text-lg font-bold text-sky-400">Invoice Quickview</h4>
                        <button
                          onClick={() => setSelectedInvoice(null)}
                          className="text-slate-400 hover:text-slate-200 font-bold"
                        >
                          ✕ Close
                        </button>
                      </div>
                      <div className="bg-slate-950 p-4 rounded-xl border border-slate-850 font-mono text-xs text-slate-300 whitespace-pre overflow-x-auto leading-relaxed">
                        {`INVOICE: ${selectedInvoice.invoice_number}\n`}
                        {`Client Email: ${selectedInvoice.user_email}\n`}
                        {`GSTIN Ref: ${selectedInvoice.gst_number}\n`}
                        {`-------------------------------------------------\n`}
                        {`Subtotal Excl Tax:            ₹${parseFloat(selectedInvoice.amount).toFixed(2)}\n`}
                        {`IGST split (18%):             ₹${parseFloat(selectedInvoice.tax).toFixed(2)}\n`}
                        {`-------------------------------------------------\n`}
                        {`GRAND TOTAL (PAID):           ₹${parseFloat(selectedInvoice.total).toFixed(2)}\n`}
                      </div>
                    </div>
                  </div>
                )}

              </div>
            )}

            {/* 6. Coupons Vouchers */}
            {activeTab === 'coupons' && (
              <div className="space-y-6">
                
                {/* Coupon Validation Form */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h4 className="text-base font-bold text-slate-200">Validate Coupon Code</h4>
                  <form onSubmit={handleValidateCoupon} className="flex gap-2">
                    <input
                      type="text"
                      placeholder="e.g. FESTIVE20"
                      value={valCouponCode}
                      onChange={e => setValCouponCode(e.target.value)}
                      className="bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm uppercase text-slate-200 w-full"
                    />
                    <button
                      type="submit"
                      className="bg-sky-500 hover:bg-sky-400 text-slate-950 px-4 py-2 rounded-lg font-bold text-sm transition-all"
                    >
                      Check Code
                    </button>
                  </form>

                  {/* Validate results */}
                  {validatedRes && (
                    <div className="bg-slate-950 border border-slate-850 rounded-lg p-4 text-xs font-mono text-slate-400 space-y-2">
                      <div className="flex justify-between">
                        <span>Code status:</span>
                        <span className="text-emerald-400 font-bold">✓ VALID</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Calculated Discount:</span>
                        <span>₹{validatedRes.calculated_discount}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Final Price (for ₹1000):</span>
                        <span className="text-sky-400 font-bold">₹{validatedRes.final_amount}</span>
                      </div>
                    </div>
                  )}
                </div>

                {/* List Coupons */}
                <div className="space-y-3">
                  <h4 className="text-base font-bold text-slate-200">Available Promotions</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {coupons.map(c => (
                      <div key={c.id} className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex justify-between items-center gap-3">
                        <div>
                          <span className="font-mono font-bold text-sky-400 tracking-wider text-sm bg-sky-950 px-2 py-0.5 rounded">{c.code}</span>
                          <p className="text-slate-400 text-xs mt-1.5">
                            {c.type === 'PERCENTAGE' ? `${c.value}% discount` : `₹${c.value} discount`}. Expiry: {c.expiry_date}
                          </p>
                        </div>
                        <div className="text-xs text-slate-500">
                          Used: {c.usage_count}/{c.usage_limit}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

            {/* 7. Teacher Earnings & Withdrawals */}
            {activeTab === 'earnings' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Submit Withdrawal request */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h4 className="text-base font-bold text-slate-200">Request Withdrawal Cashout</h4>
                  <p className="text-slate-400 text-xs">
                    Instructors can transfer cumulative balance profits to bank accounts or wallets directly.
                  </p>
                  <form onSubmit={handlePayoutRequest} className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Withdrawal Amount (INR)</label>
                      <input
                        type="number"
                        placeholder="e.g. 5000"
                        value={payoutAmount}
                        onChange={e => setPayoutAmount(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Transfer Destination Method</label>
                      <select
                        value={payoutMethod}
                        onChange={e => setPayoutMethod(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none"
                      >
                        <option value="BANK_TRANSFER">Bank Direct Transfer</option>
                        <option value="UPI">UPI Payment Direct</option>
                        <option value="PAYPAL">PayPal Address</option>
                      </select>
                    </div>
                    <button
                      type="submit"
                      className="w-full bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold py-2 rounded-lg text-sm transition-colors"
                    >
                      Authorize Cashout
                    </button>
                  </form>
                </div>

                {/* Withdrawal requests log history */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h4 className="text-base font-bold text-slate-200">Payout Requests History</h4>
                  <div className="space-y-3">
                    {payouts.length === 0 ? (
                      <p className="text-slate-500 text-xs">No past requests compiled.</p>
                    ) : (
                      payouts.map(p => (
                        <div key={p.id} className="bg-slate-950 border border-slate-850 rounded-lg p-3 flex justify-between items-center text-xs">
                          <div>
                            <span className="font-mono font-bold text-slate-300">₹{p.amount}</span>
                            <span className="text-slate-500 ml-2">via {p.payout_method}</span>
                          </div>
                          <span
                            className={`px-2 py-0.5 rounded font-extrabold tracking-wider ${
                              p.status === 'APPROVED' ? 'bg-emerald-950 text-emerald-400' : 'bg-amber-950 text-amber-400'
                            }`}
                          >
                            {p.status}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                </div>

              </div>
            )}

            {/* 8. Analytics Panel */}
            {activeTab === 'revenue' && (
              <div className="space-y-6">
                
                {/* Metric cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Daily Revenue', val: revenueSummary?.daily_revenue || '0.00', color: 'text-sky-400' },
                    { label: 'Monthly Revenue', val: revenueSummary?.monthly_revenue || '0.00', color: 'text-indigo-400' },
                    { label: 'Wallet Debit Purchases', val: revenueSummary?.wallet_revenue || '0.00', color: 'text-purple-400' },
                    { label: 'Subscriptions Volume', val: revenueSummary?.subscription_revenue || '0.00', color: 'text-emerald-400' }
                  ].map(m => (
                    <div key={m.label} className="bg-slate-900 border border-slate-800 rounded-xl p-4">
                      <span className="text-xs text-slate-400 block uppercase tracking-wider">{m.label}</span>
                      <span className={`text-xl font-mono font-bold mt-1 block ${m.color}`}>₹{m.val}</span>
                    </div>
                  ))}
                </div>

                {/* Plotly/Chartjs Mock placeholder for analytics visualization */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 h-64 flex flex-col items-center justify-center text-center space-y-2">
                  <TrendingUp className="w-12 h-12 text-slate-650 animate-bounce" />
                  <h4 className="text-sm font-bold text-slate-350">Interactive Financial Visualizations</h4>
                  <p className="text-slate-500 text-xs max-w-md">
                    Aggregate CGST/SGST taxes, refunds volumes, and payout fulfillment ratios plotted on timeline charts.
                  </p>
                </div>

              </div>
            )}

            {/* 9. Referral Panel */}
            {activeTab === 'referrals' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Link generator */}
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
                  <h4 className="text-base font-bold text-slate-200">Refer & Earn System</h4>
                  <p className="text-slate-400 text-xs">
                    Share your unique invitation link and earn up to 50 VIDYA point reward coins for each signup!
                  </p>
                  
                  <div className="space-y-2 pt-2">
                    <label className="text-xs text-slate-400 block">Invitation Code</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={`https://brahmavidya.edu/join?ref=${currentUser?.id || 'GALAXY-VIP'}`}
                        className="bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-slate-350 w-full font-mono"
                        readOnly
                      />
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(`https://brahmavidya.edu/join?ref=${currentUser?.id || 'GALAXY-VIP'}`);
                          setSuccess('Referral invitation link copied to clipboard!');
                        }}
                        className="bg-sky-500 hover:bg-sky-400 text-slate-950 px-4 py-2 rounded-lg font-bold text-xs transition-all"
                      >
                        Copy
                      </button>
                    </div>
                  </div>
                </div>

                {/* Rewards log */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
                  <div>
                    <h4 className="text-base font-bold text-slate-200 mb-2">My Referral Stats</h4>
                    <div className="grid grid-cols-2 gap-4 text-center mt-3">
                      <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl">
                        <span className="text-xl font-extrabold text-indigo-400 font-mono">0</span>
                        <span className="text-slate-500 text-xs block mt-1">Referred Friends</span>
                      </div>
                      <div className="bg-slate-950 border border-slate-850 p-4 rounded-xl">
                        <span className="text-xl font-extrabold text-emerald-400 font-mono">₹0.00</span>
                        <span className="text-slate-500 text-xs block mt-1">Coins Earned</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-4 text-xs text-slate-500 bg-slate-950/40 p-2.5 rounded border border-slate-850">
                    <UserPlus className="w-4 h-4 text-sky-400" />
                    <span>Your friends receive ₹50 wallet welcome credits when verifying account codes!</span>
                  </div>
                </div>

              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
};
