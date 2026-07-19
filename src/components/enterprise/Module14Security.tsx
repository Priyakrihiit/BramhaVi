import React, { useState, useEffect, useCallback } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { SecurityLogEntry } from './types';
import { ShieldAlert, Smartphone, CheckCircle, RefreshCw, UserCheck, Lock, Unlock, FileText, Check, X, Shield, Settings, Info } from 'lucide-react';
import { api } from '../../services/api';

export const Module14Security: React.FC = () => {
  const { currentUser, hasCapability } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'MFA' | 'CAPABILITIES'>('MFA');
  const [logs, setLogs] = useState<SecurityLogEntry[]>([
    {
      id: 'SEC-99812',
      event: 'Successful Authentication JWT Sign-In',
      ipAddress: '103.88.22.141',
      location: 'Pune, India',
      status: 'SUCCESS',
      createdAt: '2026-07-07 14:15:22'
    },
    {
      id: 'SEC-99813',
      event: '2FA Verification Requested',
      ipAddress: '103.88.22.141',
      location: 'Pune, India',
      status: 'SUCCESS',
      createdAt: '2026-07-07 14:15:30'
    },
    {
      id: 'SEC-99814',
      event: 'Database Tenant Backup Dispatched',
      ipAddress: '18.220.10.22',
      location: 'AWS Ingress Cron',
      status: 'SUCCESS',
      createdAt: '2026-07-07 02:00:00'
    },
    {
      id: 'SEC-99815',
      event: 'Failed Login Attempt - Invalid Credentials',
      ipAddress: '42.110.12.98',
      location: 'Beijing, China',
      status: 'FAILED',
      createdAt: '2026-07-06 18:22:10'
    }
  ]);

  const [tfaEnabled, setTfaEnabled] = useState(false);
  const [tfaStep, setTfaStep] = useState<'OFF' | 'SCAN' | 'VERIFY' | 'DONE'>('OFF');
  const [otpInput, setOtpInput] = useState('');
  const [otpError, setOtpError] = useState('');
  
  const [backupCodes] = useState<string[]>([
    'BVIDYA-9871-2201',
    'BVIDYA-4491-0982',
    'BVIDYA-1102-4490',
    'BVIDYA-8812-7744'
  ]);

  // CBAC states
  const [userCapabilities, setUserCapabilities] = useState<any[]>([]);
  const [applications, setApplications] = useState<any[]>([]);
  const [systemCaps, setSystemCaps] = useState<any[]>([]);
  const [loadingCaps, setLoadingCaps] = useState(false);
  const [appNotes, setAppNotes] = useState<Record<string, string>>({});
  const [suspendUserId, setSuspendUserId] = useState('');
  const [actionStatus, setActionStatus] = useState<string | null>(null);

  const isSuperAdmin = currentUser?.email === 'admin@brahmavidya.edu' || hasCapability('ADMIN');

  const fetchCapabilityData = useCallback(async () => {
    setLoadingCaps(true);
    try {
      const mineRes = await api.capabilities.getMine();
      if (mineRes.success && mineRes.data) {
        setUserCapabilities(mineRes.data);
      } else {
        // Fallback simulated mine
        setUserCapabilities([
          { capability_codename: 'LEARNING', capability_display_name: 'Learner Portal Access', status: 'ACTIVE' },
          ...(currentUser?.email === 'teacher@brahmavidya.edu' ? [{ capability_codename: 'TEACHING', capability_display_name: 'Teacher Workspace', status: 'ACTIVE' }] : []),
          ...(isSuperAdmin ? [{ capability_codename: 'ADMIN', capability_display_name: 'Enterprise Admin', status: 'ACTIVE' }] : [])
        ]);
      }
      
      const allRes = await api.capabilities.list();
      if (allRes.success && allRes.data) {
        setSystemCaps(allRes.data);
      } else {
        // Fallback list of capabilities
        setSystemCaps([
          { codename: 'LEARNING', display_name: 'Learner Portal Access', category: 'INSTANT' },
          { codename: 'TEACHING', display_name: 'Teacher Workspace', category: 'APPROVAL' },
          { codename: 'AUTHORING', display_name: 'Book Authoring Studio', category: 'APPROVAL' },
          { codename: 'PUBLISHING', display_name: 'Publisher Portal', category: 'APPROVAL' },
          { codename: 'SERVICES', display_name: 'Service Provider Desk', category: 'APPROVAL' },
          { codename: 'RECRUITING', display_name: 'Recruiter Dashboard', category: 'APPROVAL' },
          { codename: 'ORGANIZATION', display_name: 'Organization Owner Console', category: 'APPROVAL' },
          { codename: 'AI_PREMIUM', display_name: 'Advanced Generative AI', category: 'APPROVAL' },
          { codename: 'AI_BASIC', display_name: 'Basic AI Assistants', category: 'INSTANT' }
        ]);
      }

      if (isSuperAdmin) {
        const appRes = await api.adminCapabilities.listApplications();
        if (appRes.success && appRes.data) {
          setApplications(appRes.data);
        } else {
          // Fallback mock applications
          setApplications([
            { id: 'app_1', user_email: 'student@brahmavidya.edu', capability_codename: 'TEACHING', status: 'PENDING', submitted_at: '2026-07-09' }
          ]);
        }
      }
    } catch (err) {
      console.error('Failed to load capability structures:', err);
    } finally {
      setLoadingCaps(false);
    }
  }, [currentUser, isSuperAdmin]);

  useEffect(() => {
    if (activeTab === 'CAPABILITIES') {
      fetchCapabilityData();
    }
  }, [activeTab, fetchCapabilityData]);

  const handleStart2FA = () => {
    setTfaStep('SCAN');
  };

  const handleVerify2FA = (e: React.FormEvent) => {
    e.preventDefault();
    if (otpInput === '123456') {
      setTfaEnabled(true);
      setTfaStep('DONE');
      setOtpError('');
      const log: SecurityLogEntry = {
        id: `SEC-${Date.now()}`,
        event: 'Two-Factor Authentication (2FA) Activated',
        ipAddress: '103.88.22.141',
        location: 'Pune, India',
        status: 'SUCCESS',
        createdAt: new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString()
      };
      setLogs(prev => [log, ...prev]);
    } else {
      setOtpError('Invalid authorization token. Try typing "123456" for simulation demo.');
    }
  };

  const handleDisable2FA = () => {
    setTfaEnabled(false);
    setTfaStep('OFF');
    setOtpInput('');
  };

  // CBAC Handlers
  const handleRequestCapability = async (code: string) => {
    setActionStatus(`Submitting activation request for ${code}...`);
    const res = await api.capabilities.request(code);
    if (res.success) {
      setActionStatus(`Success: ${res.message || 'Request submitted successfully.'}`);
      fetchCapabilityData();
    } else {
      setActionStatus(`Error requesting capability: ${res.message || 'Unknown issue'}`);
    }
  };

  const handleDeactivateCapability = async (code: string) => {
    setActionStatus(`Deactivating capability ${code}...`);
    const res = await api.capabilities.deactivate(code);
    if (res.success) {
      setActionStatus(`Successfully deactivated ${code}.`);
      fetchCapabilityData();
    } else {
      setActionStatus(`Deactivation failed.`);
    }
  };

  const handleReactivateCapability = async (code: string) => {
    setActionStatus(`Reactivating capability ${code}...`);
    const res = await api.capabilities.reactivate(code);
    if (res.success) {
      setActionStatus(`Successfully reactivated ${code}.`);
      fetchCapabilityData();
    } else {
      setActionStatus(`Reactivation failed.`);
    }
  };

  const handleApproveApplication = async (appId: string) => {
    const notes = appNotes[appId] || '';
    setActionStatus(`Approving application...`);
    const res = await api.adminCapabilities.approveApplication(appId, notes);
    if (res.success) {
      setActionStatus(`Application approved.`);
      fetchCapabilityData();
    } else {
      setActionStatus(`Approval failed.`);
    }
  };

  const handleRejectApplication = async (appId: string) => {
    const notes = appNotes[appId] || '';
    setActionStatus(`Rejecting application...`);
    const res = await api.adminCapabilities.rejectApplication(appId, notes);
    if (res.success) {
      setActionStatus(`Application rejected.`);
      fetchCapabilityData();
    } else {
      setActionStatus(`Rejection failed.`);
    }
  };

  const handleSuspendCapability = async (userId: string, code: string) => {
    if (!userId) return;
    setActionStatus(`Suspending user capability...`);
    const res = await api.adminCapabilities.suspendUserCapability(userId, code);
    if (res.success) {
      setActionStatus(`Suspended ${code} for user ${userId}.`);
      fetchCapabilityData();
    } else {
      setActionStatus(`Suspension failed.`);
    }
  };

  const handleReinstateCapability = async (userId: string, code: string) => {
    if (!userId) return;
    setActionStatus(`Reinstating user capability...`);
    const res = await api.adminCapabilities.reinstateUserCapability(userId, code);
    if (res.success) {
      setActionStatus(`Reinstated ${code} for user ${userId}.`);
      fetchCapabilityData();
    } else {
      setActionStatus(`Reinstatement failed.`);
    }
  };

  return (
    <div id="saas-module-14" className="space-y-6 text-slate-100">
      {/* Tab Navigation header */}
      <div className="flex border-b border-slate-800 gap-6">
        <button
          onClick={() => setActiveTab('MFA')}
          className={`pb-3 text-sm font-bold transition flex items-center gap-1.5 ${activeTab === 'MFA' ? 'border-b-2 border-indigo-500 text-white' : 'text-slate-400 hover:text-white'}`}
        >
          <Shield className="w-4 h-4" /> MFA & Intrusion Threat Logging
        </button>
        <button
          onClick={() => setActiveTab('CAPABILITIES')}
          className={`pb-3 text-sm font-bold transition flex items-center gap-1.5 ${activeTab === 'CAPABILITIES' ? 'border-b-2 border-indigo-500 text-white' : 'text-slate-400 hover:text-white'}`}
        >
          <UserCheck className="w-4 h-4" /> Capability-Based Access Control (CBAC)
        </button>
      </div>

      {activeTab === 'MFA' ? (
        <>
          <div className="bg-slate-900/60 border border-indigo-950 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 text-left">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <ShieldAlert className="text-indigo-400 w-5 h-5" />
                Security Center, Multi-Factor Auth & Threat Logging
              </h2>
              <p className="text-slate-400 text-xs mt-1">
                Enterprise threat compliance workspace. Monitor geolocated access attempts, configure Time-Based One-Time Password (TOTP 2FA) keys, and inspect audit ledger tables.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-5 space-y-6 text-left">
              <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <Smartphone className="w-4 h-4 text-indigo-400" /> Two-Factor Auth (2FA) Setup
                </h3>
                
                {tfaStep === 'OFF' && (
                  <div className="space-y-3">
                    <p className="text-xs text-slate-400 leading-relaxed">
                      Two-Factor Authentication adds an extra layer of protection to your BV Galaxy account. When activated, you must present a 6-digit verification code from Google Authenticator.
                    </p>
                    <button
                      onClick={handleStart2FA}
                      className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2 px-4 rounded-xl transition shadow-md shadow-indigo-950"
                    >
                      Activate Multi-Factor Authenticator
                    </button>
                  </div>
                )}

                {tfaStep === 'SCAN' && (
                  <div className="space-y-4 text-center">
                    <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-widest block font-mono">Step 1: Scan Barcode</span>
                    <div className="bg-white p-3 rounded-xl inline-block">
                      <svg width="120" height="120" viewBox="0 0 100 100" className="mx-auto">
                        <rect x="10" y="10" width="15" height="15" fill="black" />
                        <rect x="15" y="15" width="5" height="5" fill="white" />
                        <rect x="75" y="10" width="15" height="15" fill="black" />
                        <rect x="75" y="15" width="5" height="5" fill="white" />
                        <rect x="10" y="75" width="15" height="15" fill="black" />
                        <rect x="15" y="75" width="5" height="5" fill="white" />
                        <rect x="35" y="10" width="10" height="5" fill="black" />
                        <rect x="55" y="25" width="5" height="15" fill="black" />
                        <rect x="30" y="45" width="20" height="10" fill="black" />
                        <rect x="65" y="60" width="15" height="5" fill="black" />
                        <rect x="45" y="75" width="5" height="15" fill="black" />
                        <rect x="65" y="45" width="5" height="5" fill="black" />
                        <rect x="15" y="35" width="5" height="5" fill="black" />
                      </svg>
                    </div>
                    <p className="text-[11px] text-slate-400">Scan this barcode inside your Google Authenticator or Authy app. Then proceed to verification.</p>
                    
                    <button
                      onClick={() => setTfaStep('VERIFY')}
                      className="w-full bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 text-xs font-bold py-2 rounded-xl transition"
                    >
                      Configure Code Verification
                    </button>
                  </div>
                )}

                {tfaStep === 'VERIFY' && (
                  <form onSubmit={handleVerify2FA} className="space-y-4">
                    <span className="text-[10px] text-indigo-400 font-bold uppercase tracking-widest block font-mono">Step 2: Verification Code</span>
                    <div>
                      <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Enter Authenticator Token</label>
                      <input
                        type="text"
                        required
                        maxLength={6}
                        placeholder='Type "123456" for demo...'
                        value={otpInput}
                        onChange={(e) => setOtpInput(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-mono text-center tracking-widest font-black text-sm"
                      />
                      {otpError && <span className="text-[10px] text-rose-400 block mt-1 leading-relaxed font-sans">{otpError}</span>}
                    </div>

                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setTfaStep('SCAN')}
                        className="flex-1 bg-slate-900 border border-slate-800 text-slate-400 text-xs py-2 rounded-xl transition"
                      >
                        Back
                      </button>
                      <button
                        type="submit"
                        className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold py-2 rounded-xl transition"
                      >
                        Confirm & Save
                      </button>
                    </div>
                  </form>
                )}

                {tfaStep === 'DONE' && (
                  <div className="space-y-4">
                    <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-widest block font-mono">Security Confirmed!</span>
                    <div className="bg-emerald-950/20 border border-emerald-900 text-emerald-300 p-3 rounded-xl text-xs flex items-center gap-2">
                      <CheckCircle className="w-5 h-5 shrink-0" />
                      <span>Google TOTP 2FA Verification successfully activated for your account.</span>
                    </div>

                    <div className="space-y-2">
                      <span className="text-[10px] text-slate-500 font-bold uppercase">Back up codes (Keep safe)</span>
                      <div className="bg-slate-900 border border-slate-850 p-3 rounded-xl grid grid-cols-2 gap-1.5 font-mono text-[10px] text-slate-300">
                        {backupCodes.map((code, idx) => (
                          <span key={idx}>{code}</span>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={handleDisable2FA}
                      className="w-full bg-rose-950/20 border border-rose-900/40 text-rose-400 hover:bg-rose-900 hover:text-white text-xs font-bold py-2 rounded-xl transition"
                    >
                      Disable Two-Factor Auth
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="lg:col-span-7 space-y-4 text-left">
              <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 flex flex-col justify-between h-[450px]">
                <div>
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-1.5">
                    <ShieldAlert className="w-4 h-4 text-indigo-400" />
                    Active Intrusion Threat Audit Logs
                  </h3>

                  <div className="space-y-2.5 max-h-[350px] overflow-y-auto pr-1">
                    {logs.map(log => (
                      <div key={log.id} className="bg-slate-900/40 border border-slate-850 p-3 rounded-xl flex flex-col gap-1 font-mono text-[11px]">
                        <div className="flex justify-between items-start">
                          <span className={`font-sans font-bold ${log.status === 'SUCCESS' ? 'text-slate-200' : 'text-rose-400 animate-pulse'}`}>{log.event}</span>
                          <span className={`text-[8px] font-bold px-1.5 py-0.2 rounded ${log.status === 'SUCCESS' ? 'bg-indigo-500/10 text-indigo-400' : 'bg-rose-500/10 text-rose-400'}`}>
                            {log.status}
                          </span>
                        </div>

                        <div className="flex justify-between text-[9px] text-slate-500 mt-1">
                          <span>Source IP: {log.ipAddress} ({log.location})</span>
                          <span>{log.createdAt}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        /* CAPABILITIES ACTIVE TAB */
        <div className="space-y-6 text-left">
          {actionStatus && (
            <div className="bg-indigo-950/40 border border-indigo-850 p-3 rounded-xl text-xs flex justify-between items-center text-indigo-200">
              <span>{actionStatus}</span>
              <button onClick={() => setActionStatus(null)} className="text-slate-400 hover:text-white font-bold">×</button>
            </div>
          )}

          {/* User Active Capabilities Section */}
          <div className="bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <UserCheck className="w-4 h-4 text-indigo-400" /> My Activated Capabilities
              </h3>
              <button onClick={fetchCapabilityData} className="text-slate-400 hover:text-white p-1 rounded transition">
                <RefreshCw className={`w-3.5 h-3.5 ${loadingCaps ? 'animate-spin' : ''}`} />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {systemCaps.map(cap => {
                const mine = userCapabilities.find(uc => uc.capability_codename === cap.codename);
                const status = mine ? mine.status : 'INACTIVE';
                
                return (
                  <div key={cap.codename} className={`p-4 rounded-xl border flex flex-col justify-between gap-3 transition ${
                    status === 'ACTIVE' ? 'bg-indigo-950/20 border-indigo-900/60' :
                    status === 'PENDING' ? 'bg-amber-950/15 border-amber-900/40' :
                    status === 'SUSPENDED' ? 'bg-rose-950/20 border-rose-900/50' :
                    'bg-slate-900/30 border-slate-900'
                  }`}>
                    <div>
                      <div className="flex justify-between items-start">
                        <h4 className="text-xs font-bold text-white">{cap.display_name}</h4>
                        <span className={`text-[8px] font-bold px-1.5 py-0.2 rounded font-mono ${
                          status === 'ACTIVE' ? 'bg-indigo-500/10 text-indigo-400' :
                          status === 'PENDING' ? 'bg-amber-500/10 text-amber-400' :
                          status === 'SUSPENDED' ? 'bg-rose-500/10 text-rose-400' :
                          status === 'DEACTIVATED' ? 'bg-slate-800 text-slate-400' :
                          'bg-slate-950 text-slate-600'
                        }`}>
                          {status}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-500 mt-1 font-mono">{cap.codename}</p>
                    </div>

                    <div className="flex items-center justify-between text-[9px] text-slate-400 border-t border-slate-900/80 pt-2">
                      <span>Type: <strong className="font-mono text-indigo-400">{cap.category}</strong></span>
                      
                      <div className="flex gap-1.5">
                        {status === 'INACTIVE' && (
                          <button
                            onClick={() => handleRequestCapability(cap.codename)}
                            className="bg-indigo-600 hover:bg-indigo-500 text-white text-[9px] font-bold py-1 px-2.5 rounded-lg transition"
                          >
                            Activate
                          </button>
                        )}
                        {status === 'DEACTIVATED' && (
                          <button
                            onClick={() => handleReactivateCapability(cap.codename)}
                            className="bg-emerald-600 hover:bg-emerald-500 text-white text-[9px] font-bold py-1 px-2.5 rounded-lg transition"
                          >
                            Reactivate
                          </button>
                        )}
                        {status === 'ACTIVE' && cap.codename !== 'LEARNING' && (
                          <button
                            onClick={() => handleDeactivateCapability(cap.codename)}
                            className="bg-slate-850 hover:bg-slate-800 text-slate-300 text-[9px] font-bold py-1 px-2.5 rounded-lg transition border border-slate-800"
                          >
                            Deactivate
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Admin Review Workspace Section */}
          {isSuperAdmin && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Review Applications Panel */}
              <div className="lg:col-span-7 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <FileText className="w-4.5 h-4.5 text-indigo-400" /> Pending Capability Applications
                </h3>

                <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                  {applications.filter(app => app.status === 'PENDING').length === 0 ? (
                    <div className="text-center py-6 text-slate-500 text-xs flex flex-col items-center gap-1.5">
                      <Check className="w-8 h-8 text-slate-700" />
                      No pending applications to review.
                    </div>
                  ) : (
                    applications.filter(app => app.status === 'PENDING').map(app => (
                      <div key={app.id} className="bg-slate-900/60 border border-slate-850 p-4 rounded-xl space-y-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="text-xs font-bold text-slate-200 block">{app.user_email}</span>
                            <span className="text-[9px] text-slate-500 font-mono">Requesting: {app.capability_codename}</span>
                          </div>
                          <span className="text-[8px] font-mono text-slate-500">{app.submitted_at}</span>
                        </div>

                        <input
                          type="text"
                          placeholder="Review notes..."
                          value={appNotes[app.id] || ''}
                          onChange={(e) => setAppNotes(prev => ({ ...prev, [app.id]: e.target.value }))}
                          className="w-full bg-slate-950 border border-slate-900 rounded-lg px-2.5 py-1 text-xs text-white placeholder-slate-700 focus:outline-none focus:border-indigo-850"
                        />

                        <div className="flex gap-2 justify-end">
                          <button
                            onClick={() => handleRejectApplication(app.id)}
                            className="bg-rose-950/30 hover:bg-rose-900 border border-rose-900/40 text-rose-400 text-[10px] font-bold py-1 px-3 rounded-lg transition flex items-center gap-1"
                          >
                            <X className="w-3.5 h-3.5" /> Reject
                          </button>
                          <button
                            onClick={() => handleApproveApplication(app.id)}
                            className="bg-emerald-950/30 hover:bg-emerald-900 border border-emerald-900/40 text-emerald-400 text-[10px] font-bold py-1 px-3 rounded-lg transition flex items-center gap-1"
                          >
                            <Check className="w-3.5 h-3.5" /> Approve
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Administrative User Capabilities Controller */}
              <div className="lg:col-span-5 bg-slate-950/40 border border-slate-900 rounded-2xl p-5 space-y-4">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                  <Shield className="w-4 h-4 text-indigo-400" /> Admin Access Controller
                </h3>

                <div className="space-y-4 text-xs">
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    Manually override access privileges. Suspend or reinstate user active capabilities instantly by User ID and capability code.
                  </p>

                  <div className="space-y-3">
                    <div>
                      <label className="block text-[10px] text-slate-400 uppercase font-bold mb-1">Target User ID</label>
                      <input
                        type="text"
                        placeholder="Enter UUID..."
                        value={suspendUserId}
                        onChange={(e) => setSuspendUserId(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-850 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-700 focus:outline-none focus:border-indigo-500 font-mono"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <button
                        onClick={() => handleSuspendCapability(suspendUserId, 'TEACHING')}
                        disabled={!suspendUserId}
                        className="bg-slate-900 border border-slate-850 hover:bg-rose-950/20 hover:border-rose-900 hover:text-rose-400 text-slate-400 text-[10px] font-bold py-2 rounded-xl transition flex items-center justify-center gap-1.5 disabled:opacity-40"
                      >
                        <Lock className="w-3.5 h-3.5" /> Suspend Teach
                      </button>
                      <button
                        onClick={() => handleReinstateCapability(suspendUserId, 'TEACHING')}
                        disabled={!suspendUserId}
                        className="bg-slate-900 border border-slate-850 hover:bg-emerald-950/20 hover:border-emerald-900 hover:text-emerald-400 text-slate-400 text-[10px] font-bold py-2 rounded-xl transition flex items-center justify-center gap-1.5 disabled:opacity-40"
                      >
                        <Unlock className="w-3.5 h-3.5" /> Reinstate Teach
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Module14Security;
