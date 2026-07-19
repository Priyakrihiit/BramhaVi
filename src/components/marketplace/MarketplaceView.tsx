import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Product, ServiceRequest, Quotation, Order, Invoice, User } from '../../types';
import { ShoppingCart, LayoutGrid, CheckCircle, FileText, Send, Sparkles, Filter, Trash, Tag, Percent, RefreshCw } from 'lucide-react';

interface MarketplaceViewProps {
  currentUser: User | null;
  onRefreshWallet: () => void;
}

export const MarketplaceView: React.FC<MarketplaceViewProps> = ({ currentUser, onRefreshWallet }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedType, setSelectedType] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Shopping Cart state
  const [cart, setCart] = useState<Array<{ product: Product; quantity: number }>>([]);
  const [couponCode, setCouponCode] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState('');
  const [billingAddress, setBillingAddress] = useState('');
  const [receipt, setReceipt] = useState<{ order: Order; invoice: Invoice } | null>(null);

  // Service Marketplace states
  const [serviceRequests, setServiceRequests] = useState<ServiceRequest[]>([]);
  const [serviceType, setServiceType] = useState('Web Development');
  const [serviceDesc, setServiceDesc] = useState('');
  const [serviceBudget, setServiceBudget] = useState(5000);

  // Quotation states (for teachers)
  const [pendingRequests, setPendingRequests] = useState<ServiceRequest[]>([]);
  const [selectedRequestForQuote, setSelectedRequestForQuote] = useState<ServiceRequest | null>(null);
  const [quoteAmount, setQuoteAmount] = useState(4000);
  const [quoteTimeline, setQuoteTimeline] = useState(5);
  const [quoteNotes, setQuoteNotes] = useState('');

  // Loaded quotations (for students to view/accept)
  const [quotations, setQuotations] = useState<Quotation[]>([]);

  // Status & loading
  const [activeTab, setActiveTab] = useState<'catalog' | 'cart' | 'services'>('catalog');
  const [msg, setMsg] = useState({ text: '', type: '' });
  const [loading, setLoading] = useState(false);

  const productTypes = ['All', 'BOOK', 'COURSE', 'PORTFOLIO_TEMPLATE', 'RESUME_TEMPLATE', 'DIGITAL_ASSET', 'SERVICE'];

  useEffect(() => {
    fetchProducts();
    if (currentUser) {
      fetchServiceRequestsAndQuotes();
    }
  }, [currentUser, selectedType]);

  const fetchProducts = async () => {
    setLoading(true);
    const res = await api.marketplace.listProducts({
      type: selectedType === 'All' ? undefined : selectedType,
      q: searchQuery || undefined
    });
    if (res.success && res.data) {
      setProducts(res.data);
    }
    setLoading(false);
  };

  const fetchServiceRequestsAndQuotes = async () => {
    const isTeacher = currentUser?.email === 'teacher@brahmavidya.edu';
    
    // Students see their requests. Teachers see all requests to draft quotes
    const reqsRes = await api.marketplace.listServiceRequests(isTeacher ? undefined : currentUser?.id);
    if (reqsRes.success && reqsRes.data) {
      setServiceRequests(reqsRes.data);
      if (isTeacher) {
        setPendingRequests(reqsRes.data.filter(r => r.status === 'PENDING' || r.status === 'QUOTED'));
      }
    }

    // Load all quotes on student requests
    const qtsRes = await api.marketplace.listQuotations();
    if (qtsRes.success && qtsRes.data) {
      setQuotations(qtsRes.data);
    }
  };

  // Cart operations
  const addToCart = (product: Product) => {
    const existing = cart.find(item => item.product.id === product.id);
    if (existing) {
      setCart(cart.map(item => item.product.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
    } else {
      setCart([...cart, { product, quantity: 1 }]);
    }
    setMsg({ text: `"${product.name}" added to shopping cart!`, type: 'success' });
    setTimeout(() => setMsg({ text: '', type: '' }), 3000);
  };

  const removeFromCart = (productId: string) => {
    setCart(cart.filter(item => item.product.id !== productId));
  };

  const clearCart = () => {
    setCart([]);
    setAppliedCoupon('');
    setCouponCode('');
  };

  const applyCoupon = () => {
    if (couponCode.toUpperCase() === 'BVG10') {
      setAppliedCoupon('BVG10');
      setMsg({ text: 'Promo code "BVG10" applied! 10% discount subtracted from subtotal.', type: 'success' });
    } else {
      setMsg({ text: 'Invalid promotional coupon code.', type: 'error' });
    }
  };

  // Cart math
  const subtotal = cart.reduce((acc, item) => acc + item.product.price * item.quantity, 0);
  const discount = appliedCoupon === 'BVG10' ? parseFloat((subtotal * 0.1).toFixed(2)) : 0;
  const netAmount = subtotal - discount;
  const gst = parseFloat((netAmount * 0.18).toFixed(2)); // 18% standard GST
  const total = parseFloat((netAmount + gst).toFixed(2));

  const handleCheckout = async () => {
    if (!currentUser) {
      setMsg({ text: 'Session expired. Please log in.', type: 'error' });
      return;
    }
    if (cart.length === 0) return;

    setLoading(true);
    const checkoutItems = cart.map(item => ({
      id: item.product.id,
      name: item.product.name,
      quantity: item.quantity
    }));

    const res = await api.marketplace.checkout({
      userId: currentUser.id,
      items: checkoutItems,
      couponCode: appliedCoupon || undefined,
      billingAddress: billingAddress || undefined
    });

    setLoading(false);
    if (res.success && res.data) {
      setReceipt(res.data);
      clearCart();
      onRefreshWallet();
      setMsg({ text: 'Checkout successful! Academic wallet debited, ledger transaction logged, and invoice generated.', type: 'success' });
    } else {
      setMsg({ text: res.message || 'Checkout failed.', type: 'error' });
    }
  };

  // Service Request Submission
  const submitServiceRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) return;

    const res = await api.marketplace.submitServiceRequest({
      userId: currentUser.id,
      userName: currentUser.fullName,
      serviceType,
      description: serviceDesc,
      budget: serviceBudget
    });

    if (res.success) {
      setServiceDesc('');
      setMsg({ text: 'Project service request posted successfully! Academic teachers can now submit quotations.', type: 'success' });
      fetchServiceRequestsAndQuotes();
    }
  };

  // Teacher Quotation drafting
  const submitQuotation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser || !selectedRequestForQuote) return;

    const res = await api.marketplace.createQuotation({
      requestId: selectedRequestForQuote.id,
      teacherId: currentUser.id,
      teacherName: currentUser.fullName,
      amount: quoteAmount,
      timelineDays: quoteTimeline,
      notes: quoteNotes
    });

    if (res.success) {
      setSelectedRequestForQuote(null);
      setQuoteNotes('');
      setMsg({ text: 'Project quote submitted successfully to the student dashboard!', type: 'success' });
      fetchServiceRequestsAndQuotes();
    }
  };

  // Student Accepts quotation
  const acceptQuote = async (quoteId: string) => {
    if (!currentUser) return;
    const res = await api.marketplace.acceptQuotation(quoteId, currentUser.id);
    if (res.success) {
      setMsg({ text: 'Quotation accepted! Funds securely wired from your wallet, and service project has officially started!', type: 'success' });
      fetchServiceRequestsAndQuotes();
      onRefreshWallet();
    } else {
      setMsg({ text: res.message || 'Quotation acceptance failed.', type: 'error' });
    }
  };

  const isTeacher = currentUser?.email === 'teacher@brahmavidya.edu';

  return (
    <div id="marketplace-root" className="min-h-screen bg-slate-50 text-slate-900 pb-12">
      {/* Brand Header */}
      <div className="bg-slate-900 text-white py-12 px-6 shadow-sm border-b border-slate-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-emerald-500 text-white text-[10px] font-mono px-2 py-0.5 rounded-full tracking-wider uppercase font-semibold">Taxes & Commissions Integrated</span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight font-sans">BrahmaVidya Central Marketplace</h1>
            <p className="text-slate-400 mt-2 max-w-2xl font-sans">
              Shop textbooks, modular course syllabi, portfolio shells, and professional academic development services.
              Supports wallet verification and automatic GST invoice receipts.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('catalog')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'catalog' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              Browse Catalogue
            </button>
            <button
              onClick={() => setActiveTab('services')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'services' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-indigo-400 hover:bg-slate-700'}`}
            >
              Service Marketplace
            </button>
            <button
              onClick={() => setActiveTab('cart')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-1.5 ${activeTab === 'cart' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              <ShoppingCart className="h-4 w-4" />
              Shopping Cart ({cart.length})
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 mt-8">
        {msg.text && (
          <div className={`p-4 rounded-xl mb-6 flex items-center justify-between border ${msg.type === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'}`}>
            <span className="text-sm font-medium">{msg.text}</span>
            <button onClick={() => setMsg({ text: '', type: '' })} className="text-xs underline font-bold cursor-pointer">Dismiss</button>
          </div>
        )}

        {/* 1. BROWSE CATALOG TAB */}
        {activeTab === 'catalog' && (
          <div>
            {/* Search & filters */}
            <div className="flex flex-col md:flex-row gap-4 mb-8 justify-between items-stretch">
              <div className="relative flex-1">
                <LayoutGrid className="absolute left-3 top-3.5 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Query unified marketplace products, templates, resources..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchProducts()}
                  className="w-full pl-10 pr-4 py-3 bg-white rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans text-sm shadow-sm"
                />
              </div>
              <div className="flex items-center gap-2 overflow-x-auto pb-1 md:pb-0">
                <span className="text-xs font-mono font-bold text-slate-500 flex items-center gap-1">
                  <Filter className="h-3.5 w-3.5" /> Type:
                </span>
                {productTypes.map(type => (
                  <button
                    key={type}
                    onClick={() => setSelectedType(type)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${selectedType === type ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'}`}
                  >
                    {type.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Product lists */}
            {loading ? (
              <div className="flex flex-col items-center justify-center py-20">
                <RefreshCw className="h-8 w-8 text-indigo-500 animate-spin mb-2" />
                <p className="text-sm text-slate-500">Retrieving academic inventories...</p>
              </div>
            ) : products.length === 0 ? (
              <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl max-w-md mx-auto">
                <LayoutGrid className="h-10 w-10 text-slate-300 mx-auto mb-2" />
                <h3 className="font-bold text-slate-800 text-base">No items available</h3>
                <p className="text-xs text-slate-500">Syllabus block or templates not registered under this filter.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {products.map(prod => (
                  <div key={prod.id} className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col hover:shadow-md transition-all">
                    <div className="relative aspect-video bg-slate-100 overflow-hidden">
                      <img src={prod.imageUrl} alt={prod.name} className="w-full h-full object-cover" />
                      <div className="absolute top-2 left-2 bg-indigo-600 text-white text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase">
                        {prod.type.replace('_', ' ')}
                      </div>
                    </div>
                    <div className="p-4 flex-1 flex flex-col justify-between">
                      <div>
                        <div className="flex items-center gap-1 text-xs text-slate-500 mb-1">
                          <span className="font-semibold text-indigo-600">{prod.category}</span>
                          <span>•</span>
                          <span>By {prod.sellerName}</span>
                        </div>
                        <h3 className="font-bold text-slate-900 leading-tight tracking-tight text-sm">
                          {prod.name}
                        </h3>
                        <p className="text-xs text-slate-500 line-clamp-2 mt-2 leading-relaxed">
                          {prod.description}
                        </p>
                      </div>

                      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                        <div>
                          <span className="text-xs text-slate-400 line-through block font-mono">
                            {prod.originalPrice ? `₹${prod.originalPrice}` : ''}
                          </span>
                          <span className="text-sm font-bold text-slate-900 font-mono">
                            {prod.price === 0 ? 'FREE' : `₹${prod.price}`}
                          </span>
                        </div>
                        <button
                          onClick={() => addToCart(prod)}
                          className="bg-slate-900 text-white text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-slate-800 transition-all flex items-center gap-1 cursor-pointer"
                        >
                          <ShoppingCart className="h-3.5 w-3.5" /> Buy
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 2. SHOPPING CART TAB */}
        {activeTab === 'cart' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cart Listings */}
            <div className="lg:col-span-2 space-y-4">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="font-bold text-lg text-slate-900 flex items-center gap-2">
                    <ShoppingCart className="h-5 w-5 text-indigo-500" />
                    Review Your Items
                  </h3>
                  {cart.length > 0 && (
                    <button onClick={clearCart} className="text-xs font-semibold text-rose-600 hover:underline cursor-pointer">Clear All</button>
                  )}
                </div>

                {cart.length === 0 ? (
                  <div className="text-center py-16 text-slate-400">
                    <ShoppingCart className="h-10 w-10 mx-auto mb-2 opacity-30" />
                    <p className="text-sm font-medium">Your shopping cart is empty.</p>
                    <button onClick={() => setActiveTab('catalog')} className="mt-2 text-xs font-bold text-indigo-600 underline">Browse Products</button>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {cart.map(item => (
                      <div key={item.product.id} className="py-4 flex items-center justify-between gap-4">
                        <div className="flex items-center gap-3">
                          <div className="h-12 w-12 rounded-lg bg-slate-100 overflow-hidden shrink-0">
                            <img src={item.product.imageUrl} alt={item.product.name} className="w-full h-full object-cover" />
                          </div>
                          <div>
                            <span className="text-[10px] font-mono text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded uppercase font-bold">{item.product.type}</span>
                            <h4 className="font-bold text-slate-800 text-sm mt-0.5 leading-tight">{item.product.name}</h4>
                            <span className="text-xs text-slate-500">Seller: {item.product.sellerName}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-sm font-bold text-slate-900 font-mono">₹{item.product.price}</span>
                          <button onClick={() => removeFromCart(item.product.id)} className="p-1.5 text-slate-400 hover:text-rose-600">
                            <Trash className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Billing Summary Box */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
                <h3 className="font-bold text-lg text-slate-900 border-b border-slate-100 pb-3">Checkout Breakdown</h3>
                
                {/* Promo Coupon */}
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-slate-600 uppercase">Coupon Promo Code</label>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Tag className="absolute left-2 top-2.5 h-3.5 w-3.5 text-slate-400" />
                      <input
                        type="text"
                        placeholder="e.g. BVG10 (10% Off)"
                        value={couponCode}
                        onChange={(e) => setCouponCode(e.target.value)}
                        className="w-full pl-7 pr-2 py-1.5 border border-slate-200 rounded-lg text-xs font-mono"
                      />
                    </div>
                    <button onClick={applyCoupon} className="bg-slate-950 text-white text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-slate-800 cursor-pointer">Apply</button>
                  </div>
                </div>

                {/* Billing fields */}
                <div>
                  <label className="block text-xs font-bold text-slate-600 uppercase mb-1">Billing Address (For GST Accounting) *</label>
                  <textarea
                    rows={2}
                    placeholder="Enter permanent billing address..."
                    value={billingAddress}
                    onChange={(e) => setBillingAddress(e.target.value)}
                    className="w-full text-xs px-3 py-2 border border-slate-200 rounded-lg font-sans"
                  />
                </div>

                {/* Totals */}
                <div className="space-y-2.5 font-sans pt-2">
                  <div className="flex justify-between text-xs text-slate-600">
                    <span>Subtotal:</span>
                    <span className="font-mono">₹{subtotal.toFixed(2)}</span>
                  </div>
                  {discount > 0 && (
                    <div className="flex justify-between text-xs text-emerald-600 font-semibold">
                      <span className="flex items-center gap-1"><Percent className="h-3 w-3" /> Discount (10%):</span>
                      <span className="font-mono">-₹{discount.toFixed(2)}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-xs text-slate-600">
                    <span>GST (18% Flat standard):</span>
                    <span className="font-mono">₹{gst.toFixed(2)}</span>
                  </div>
                  <div className="border-t border-slate-100 pt-3 flex justify-between text-sm font-bold text-slate-900 uppercase">
                    <span>Ledger Debit Total:</span>
                    <span className="font-mono text-indigo-600">₹{total.toFixed(2)}</span>
                  </div>
                </div>

                <button
                  onClick={handleCheckout}
                  disabled={cart.length === 0 || loading || !billingAddress}
                  className={`w-full py-3 rounded-xl text-xs font-bold uppercase tracking-wider transition-all ${
                    cart.length === 0 || loading || !billingAddress ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-indigo-600 text-white hover:bg-indigo-700 cursor-pointer shadow-sm'
                  }`}
                >
                  {loading ? 'Validating Wallet Ledger...' : 'Approve Wallet Settlement'}
                </button>
              </div>

              {receipt && (
                <div className="bg-emerald-950 text-emerald-100 p-6 rounded-2xl border border-emerald-800 space-y-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-400 shrink-0" />
                    <span className="font-bold text-sm">GST Receipt Generated!</span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <div>Order ID: <strong className="font-mono">{receipt.order.id}</strong></div>
                    <div>Invoice ID: <strong className="font-mono">{receipt.invoice.id}</strong></div>
                    <div>Billed To: <strong>{receipt.invoice.userName}</strong></div>
                    <div>Tax Standard: <strong>18% GST (India)</strong></div>
                    <div>Wallet Charge: <strong className="font-mono text-emerald-400">₹{receipt.order.total}</strong></div>
                  </div>
                  <button
                    onClick={() => alert(`Accessing system vault... Certified secure invoice PDF: ${receipt.invoice.id}.pdf`)}
                    className="w-full py-2 bg-emerald-800 hover:bg-emerald-700 text-white text-[11px] font-bold rounded-lg transition-all flex items-center justify-center gap-1.5"
                  >
                    <FileText className="h-3.5 w-3.5" /> Download Tax Invoice PDF
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 3. SERVICE MARKETPLACE TAB */}
        {activeTab === 'services' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Student request post form */}
            {!isTeacher ? (
              <div className="lg:col-span-1 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <div className="flex items-center gap-2 mb-4">
                  <Send className="h-5 w-5 text-indigo-600" />
                  <h3 className="font-bold text-lg text-slate-900">Post Service Project</h3>
                </div>
                <p className="text-xs text-slate-500 mb-6 leading-relaxed">
                  Need custom solutions built by certified academic teachers or super admins? Post your project briefs and budget escrow directly here.
                </p>

                <form onSubmit={submitServiceRequest} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Required Service Category *</label>
                    <select
                      value={serviceType}
                      onChange={(e) => setServiceType(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white"
                    >
                      <option value="Web Development">Web Development</option>
                      <option value="Mobile App Development">Mobile App Development</option>
                      <option value="Performance Marketing">Performance Marketing</option>
                      <option value="Search Engine Optimization (SEO)">Search Engine Optimization (SEO)</option>
                      <option value="AI Solutions & Machine Learning">AI Solutions & Machine Learning</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Budget Escrow (₹) *</label>
                    <input
                      type="number"
                      required
                      min={500}
                      value={serviceBudget}
                      onChange={(e) => setServiceBudget(parseInt(e.target.value))}
                      className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Detailed Brief & Requirements *</label>
                    <textarea
                      required
                      rows={5}
                      placeholder="Specify your technical expectations, database schema rules, or branding deliverables..."
                      value={serviceDesc}
                      onChange={(e) => setServiceDesc(e.target.value)}
                      className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-2.5 bg-slate-900 text-white text-xs font-bold rounded-lg hover:bg-slate-800 transition-all cursor-pointer shadow-sm"
                  >
                    Post Request to Teacher Board
                  </button>
                </form>
              </div>
            ) : (
              // Teacher Quotation Box (if teacher has clicked a request)
              <div className="lg:col-span-1 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="h-5 w-5 text-indigo-600 animate-pulse" />
                  <h3 className="font-bold text-lg text-slate-900">Draft Project Quotation</h3>
                </div>
                {selectedRequestForQuote ? (
                  <form onSubmit={submitQuotation} className="space-y-4">
                    <div className="p-3 bg-slate-50 border border-slate-100 rounded-lg">
                      <span className="text-[10px] font-mono text-slate-400">Target Request ID: {selectedRequestForQuote.id}</span>
                      <h4 className="font-bold text-xs text-slate-800 mt-1">Client: {selectedRequestForQuote.userName}</h4>
                      <p className="text-[11px] text-slate-500 mt-1 line-clamp-2">"{selectedRequestForQuote.description}"</p>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">Bid Amount (₹) *</label>
                      <input
                        type="number"
                        required
                        value={quoteAmount}
                        onChange={(e) => setQuoteAmount(parseInt(e.target.value))}
                        className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">Delivery Timeline (Days) *</label>
                      <input
                        type="number"
                        required
                        value={quoteTimeline}
                        onChange={(e) => setQuoteTimeline(parseInt(e.target.value))}
                        className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">Teacher Notes & Deliverables *</label>
                      <textarea
                        required
                        rows={4}
                        placeholder="Detail your delivery milestones, structural warranties, or service frameworks..."
                        value={quoteNotes}
                        onChange={(e) => setQuoteNotes(e.target.value)}
                        className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 font-sans"
                      />
                    </div>

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setSelectedRequestForQuote(null)}
                        className="flex-1 py-2 bg-slate-100 text-slate-600 text-xs font-semibold rounded-lg hover:bg-slate-200"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="flex-1 py-2 bg-indigo-600 text-white text-xs font-bold rounded-lg hover:bg-indigo-700 shadow-sm"
                      >
                        Submit Quotation
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="text-center py-12 text-slate-400">
                    <Send className="h-8 w-8 mx-auto mb-2 opacity-30" />
                    <p className="text-xs">Click "Bid on Project" from the list to draft your certified quotation statement.</p>
                  </div>
                )}
              </div>
            )}

            {/* List of service requests */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-lg text-slate-900 mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-indigo-500" />
                  Active Service Board Proposals
                </h3>

                {serviceRequests.length === 0 ? (
                  <div className="text-center py-12 text-slate-400">
                    <FileText className="h-8 w-8 mx-auto mb-2 opacity-30" />
                    <p className="text-xs">No service board requests currently tracked.</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {serviceRequests.map(req => {
                      const reqQuotes = quotations.filter(q => q.requestId === req.id);
                      return (
                        <div key={req.id} className="p-4 border border-slate-200 rounded-xl bg-slate-50 flex flex-col gap-4">
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <span className="text-[10px] font-mono text-slate-400">ID: {req.id}</span>
                                <span className="text-[10px] bg-slate-200 text-slate-800 px-2 py-0.5 rounded font-bold uppercase">{req.serviceType}</span>
                                <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                                  req.status === 'ACCEPTED' ? 'bg-emerald-100 text-emerald-800' : 'bg-indigo-100 text-indigo-800'
                                }`}>
                                  {req.status}
                                </span>
                              </div>
                              <h4 className="font-bold text-slate-800 text-sm">Posted By: {req.userName}</h4>
                            </div>
                            <span className="text-sm font-bold text-indigo-600 font-mono">Budget: ₹{req.budget}</span>
                          </div>

                          <p className="text-xs text-slate-600 leading-relaxed italic bg-white p-3 border border-slate-100 rounded-lg">
                            "{req.description}"
                          </p>

                          {/* Action for Teacher to Bid */}
                          {isTeacher && req.status === 'PENDING' && (
                            <button
                              onClick={() => { setSelectedRequestForQuote(req); setQuoteAmount(req.budget - 500); }}
                              className="self-end bg-indigo-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-all cursor-pointer shadow-sm"
                            >
                              Bid on Project
                            </button>
                          )}

                          {/* List of quotes for this request (visible to students) */}
                          {reqQuotes.length > 0 && (
                            <div className="border-t border-slate-200 pt-3 mt-2 space-y-3">
                              <h5 className="text-[11px] font-bold text-slate-500 uppercase tracking-wide font-mono">Quotes Received ({reqQuotes.length})</h5>
                              {reqQuotes.map(q => (
                                <div key={q.id} className="p-3 bg-white border border-slate-150 rounded-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                                  <div>
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className="text-xs font-bold text-slate-800">Bid by {q.teacherName}</span>
                                      <span className="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-bold font-mono">Timeline: {q.timelineDays} Days</span>
                                      <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-mono">Quote status: {q.status}</span>
                                    </div>
                                    <p className="text-xs text-slate-500 italic">"{q.notes}"</p>
                                  </div>
                                  <div className="flex items-center gap-3 self-stretch md:self-auto justify-between md:justify-end">
                                    <span className="text-sm font-bold text-slate-900 font-mono">₹{q.amount}</span>
                                    {!isTeacher && req.status !== 'ACCEPTED' && q.status === 'PENDING' && (
                                      <button
                                        onClick={() => acceptQuote(q.id)}
                                        className="bg-emerald-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-emerald-700 transition-all cursor-pointer shadow-sm"
                                      >
                                        Accept Quote
                                      </button>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
