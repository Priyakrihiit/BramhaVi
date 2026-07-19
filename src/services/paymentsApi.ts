/**
 * API client methods for Payments, Wallets, Subscriptions, Invoices, Coupons, Payouts & Revenue.
 */

async function request<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('bvg_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error ${res.status}`);
  }
  return res.json();
}

export const paymentsApi = {
  wallet: {
    getBalance: (walletId: string) => request<any>(`/api/v1/payments/wallets/${walletId}/balance/`),
    addFunds: (walletId: string, amount: number, desc: string = 'Add Funds') =>
      request<any>(`/api/v1/payments/wallets/${walletId}/add-funds/`, {
        method: 'POST',
        body: JSON.stringify({ amount, description: desc }),
      }),
    transfer: (targetWalletId: string, amount: number, desc: string) =>
      request<any>('/api/v1/payments/transactions/transfer/', {
        method: 'POST',
        body: JSON.stringify({ target_wallet_id: targetWalletId, amount, description: desc }),
      }),
  },

  transactions: {
    list: (type?: string) => request<any[]>(`/api/v1/payments/transactions/${type ? `?type=${type}` : ''}`),
  },

  payments: {
    create: (amount: number, enrollmentId?: string, gateway: string = 'STRIPE') =>
      request<any>('/api/v1/payments/payments/', {
        method: 'POST',
        body: JSON.stringify({ amount, enrollment: enrollmentId, gateway_provider: gateway }),
      }),
    verify: (paymentId: string, gatewayTxId: string) =>
      request<any>(`/api/v1/payments/payments/${paymentId}/verify/`, {
        method: 'POST',
        body: JSON.stringify({ gateway_transaction_id: gatewayTxId }),
      }),
  },

  subscriptions: {
    getCurrent: () => request<any>('/api/v1/payments/subscriptions/current-plan/'),
    subscribe: (planName: string, price: number) =>
      request<any>('/api/v1/payments/subscriptions/subscribe/', {
        method: 'POST',
        body: JSON.stringify({ plan_name: planName, price }),
      }),
    cancel: (id: string) =>
      request<any>(`/api/v1/payments/subscriptions/${id}/cancel/`, {
        method: 'POST',
      }),
    renew: (id: string) =>
      request<any>(`/api/v1/payments/subscriptions/${id}/renew/`, {
        method: 'POST',
      }),
  },

  invoices: {
    list: () => request<any[]>('/api/v1/payments/invoices/'),
    downloadUrl: (id: string) => `/api/v1/payments/invoices/${id}/download/`,
    receiptUrl: (id: string) => `/api/v1/payments/invoices/${id}/receipt/`,
  },

  refunds: {
    list: () => request<any[]>('/api/v1/payments/refunds/'),
    create: (paymentId: string, amount: number, reason: string) =>
      request<any>('/api/v1/payments/refunds/', {
        method: 'POST',
        body: JSON.stringify({ payment: paymentId, amount, reason }),
      }),
  },

  coupons: {
    list: () => request<any[]>('/api/v1/payments/coupons/'),
    validate: (code: string, cartAmount: number) =>
      request<any>('/api/v1/payments/coupons/validate-coupon/', {
        method: 'POST',
        body: JSON.stringify({ code, cart_amount: cartAmount }),
      }),
    apply: (code: string, cartAmount: number) =>
      request<any>('/api/v1/payments/coupons/apply-coupon/', {
        method: 'POST',
        body: JSON.stringify({ code, cart_amount: cartAmount }),
      }),
  },

  payouts: {
    list: () => request<any[]>('/api/v1/payments/payouts/'),
    request: (amount: number, method: string = 'BANK_TRANSFER') =>
      request<any>('/api/v1/payments/payouts/', {
        method: 'POST',
        body: JSON.stringify({ amount, payout_method: method }),
      }),
    approve: (id: string, refId: string) =>
      request<any>(`/api/v1/payments/payouts/${id}/approve/`, {
        method: 'POST',
        body: JSON.stringify({ reference_id: refId }),
      }),
  },

  revenue: {
    getSummary: () => request<any>('/api/v1/payments/revenue-analytics/summary/'),
  },
};
