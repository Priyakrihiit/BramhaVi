/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { useLayoutStore } from '../../stores/layoutStore';
import { Input, Button, Checkbox } from '../../components/DesignSystem';
import { Mail, Lock, User as UserIcon, ShieldCheck, Key, Github, Chrome, Terminal, ArrowLeft } from 'lucide-react';

type AuthScreen = 'SIGNIN' | 'REGISTER' | 'FORGOT_PASSWORD' | 'VERIFY_OTP' | 'RESET_PASSWORD' | 'SUCCESS';

export const AuthPage: React.FC = () => {
  const { login } = useAuthStore();
  const { navigateTo } = useLayoutStore();
  
  const [screen, setScreen] = useState<AuthScreen>('SIGNIN');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setError('Please provide a valid email address.');
      return;
    }
    if (!password || password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    
    setIsLoading(true);
    setError('');
    try {
      const success = await login(email);
      if (success) {
        setScreen('SUCCESS');
        setTimeout(() => {
          navigateTo('/dashboard');
        }, 1500);
      } else {
        setError('Invalid credentials or unregistered account.');
      }
    } catch (err) {
      setError('Authentication failed. Please verify server default status.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name) {
      setError('Please enter your full name.');
      return;
    }
    if (!email) {
      setError('Please enter your email.');
      return;
    }
    if (!password || password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (!acceptTerms) {
      setError('You must accept the terms of service.');
      return;
    }

    setIsLoading(true);
    setError('');
    setTimeout(() => {
      setIsLoading(false);
      setScreen('VERIFY_OTP');
    }, 1000);
  };

  const handleForgotPassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setError('Please enter your email address.');
      return;
    }
    setIsLoading(true);
    setError('');
    setTimeout(() => {
      setIsLoading(false);
      setScreen('VERIFY_OTP');
    }, 1000);
  };

  const handleVerifyOtp = (e: React.FormEvent) => {
    e.preventDefault();
    if (otp.length < 4) {
      setError('Please enter a valid 4-digit code.');
      return;
    }
    setIsLoading(true);
    setError('');
    setTimeout(() => {
      setIsLoading(false);
      setScreen('RESET_PASSWORD');
    }, 1000);
  };

  const handleResetPassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (!password || password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setIsLoading(true);
    setError('');
    setTimeout(() => {
      setIsLoading(false);
      setScreen('SUCCESS');
      setTimeout(() => {
        setScreen('SIGNIN');
        setPassword('');
        setConfirmPassword('');
      }, 1500);
    }, 1000);
  };

  const handleOAuthLogin = (provider: string) => {
    setIsLoading(true);
    setTimeout(async () => {
      const mockEmail = `${provider.toLowerCase()}User@brahmavidya.edu`;
      await login(mockEmail);
      setScreen('SUCCESS');
      setTimeout(() => {
        navigateTo('/dashboard');
      }, 1500);
    }, 800);
  };

  return (
    <div className="flex-1 flex flex-col md:flex-row min-h-[calc(100vh-200px)] bg-[#070b19]">
      {/* Visual Accent Column */}
      <div className="hidden md:flex md:w-1/2 bg-gradient-to-br from-indigo-950 via-[#0b1329] to-slate-950 p-12 flex-col justify-between items-start text-left relative overflow-hidden border-r border-indigo-950/40">
        <div className="absolute top-1/3 left-1/4 w-[350px] h-[350px] bg-indigo-500/10 rounded-full blur-[100px] pointer-events-none"></div>
        <button
          onClick={() => navigateTo('/')}
          className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400 hover:text-white transition"
        >
          <ArrowLeft size={14} /> Back to Gateway Home
        </button>

        <div className="space-y-6 max-w-md relative z-10">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 rounded-full text-[10px] font-bold uppercase tracking-wider">
            Identity & Authorization
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white leading-tight">
            Security Gate for the <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-amber-300">
              BrahmaVidya Galaxy
            </span>
          </h1>
          <p className="text-slate-400 text-sm leading-relaxed">
            One single cryptographic user account unlocks learning streams, content publishing workflows, smart contract payouts, and proctored examination nodes.
          </p>
        </div>

        <div className="text-xs text-slate-500 font-mono">
          SECURE PROTOCOL V1.0 // MULTI-TENANT VERIFIED
        </div>
      </div>

      {/* Form Interaction Column */}
      <div className="flex-1 flex items-center justify-center p-6 md:p-12">
        <div className="w-full max-w-sm bg-[#0b1329] border border-indigo-950/80 rounded-2xl p-8 space-y-6 shadow-2xl relative">
          
          {/* Header Branding */}
          <div className="text-center space-y-2">
            <div className="mx-auto w-12 h-12 bg-gradient-to-tr from-indigo-500 to-amber-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-600/10">
              <ShieldCheck className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-black text-white tracking-tight">
                {screen === 'SIGNIN' && 'Sign In to Galaxy'}
                {screen === 'REGISTER' && 'Register Account'}
                {screen === 'FORGOT_PASSWORD' && 'Forgot Password'}
                {screen === 'VERIFY_OTP' && 'Security Code'}
                {screen === 'RESET_PASSWORD' && 'Reset Password'}
                {screen === 'SUCCESS' && 'Access Granted'}
              </h2>
              <p className="text-xs text-slate-400">
                {screen === 'SIGNIN' && 'Access your digital workspace & profiles.'}
                {screen === 'REGISTER' && 'Join the BrahmaVidya network.'}
                {screen === 'FORGOT_PASSWORD' && 'Recover your workspace credentials.'}
                {screen === 'VERIFY_OTP' && 'Enter verification code.'}
                {screen === 'RESET_PASSWORD' && 'Setup your new password.'}
                {screen === 'SUCCESS' && 'Redirecting to your secure console...'}
              </p>
            </div>
          </div>

          {/* Global Error Banner */}
          {error && (
            <div className="p-3 bg-rose-950/40 border border-rose-900/50 rounded-xl text-xs text-rose-300 font-medium text-left">
              {error}
            </div>
          )}

          {/* Sign In Screen */}
          {screen === 'SIGNIN' && (
            <form onSubmit={handleSignIn} className="space-y-4 text-left">
              <Input
                label="Email Address"
                type="email"
                placeholder="operator@brahmavidya.edu"
                icon={<Mail size={16} />}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <div className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Password</label>
                  <button
                    type="button"
                    onClick={() => { setError(''); setScreen('FORGOT_PASSWORD'); }}
                    className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
                  >
                    Forgot?
                  </button>
                </div>
                <Input
                  type="password"
                  placeholder="••••••••"
                  icon={<Lock size={16} />}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <Checkbox
                label="Keep me signed in on this operator terminal"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <Button type="submit" isLoading={isLoading} className="w-full mt-2">
                Authenticate Token
              </Button>

              <div className="relative my-4 flex items-center justify-center">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-indigo-950/60"></div>
                </div>
                <span className="relative px-3 bg-[#0b1329] text-[10px] text-slate-500 uppercase tracking-widest font-bold">
                  OAuth Providers
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2">
                <Button type="button" variant="secondary" size="sm" onClick={() => handleOAuthLogin('Google')}>
                  <Chrome size={14} className="text-amber-500" />
                </Button>
                <Button type="button" variant="secondary" size="sm" onClick={() => handleOAuthLogin('GitHub')}>
                  <Github size={14} className="text-slate-200" />
                </Button>
                <Button type="button" variant="secondary" size="sm" onClick={() => handleOAuthLogin('Microsoft')}>
                  <Terminal size={14} className="text-indigo-400" />
                </Button>
              </div>

              <p className="text-center text-xs text-slate-500 pt-2">
                New to Galaxy?{' '}
                <button
                  type="button"
                  onClick={() => { setError(''); setScreen('REGISTER'); }}
                  className="font-bold text-indigo-400 hover:text-indigo-300 transition"
                >
                  Register here
                </button>
              </p>
            </form>
          )}

          {/* Register Screen */}
          {screen === 'REGISTER' && (
            <form onSubmit={handleRegister} className="space-y-4 text-left">
              <Input
                label="Full Name"
                type="text"
                placeholder="Dr. Rajesh Patel"
                icon={<UserIcon size={16} />}
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
              <Input
                label="Email Address"
                type="email"
                placeholder="patel@brahmavidya.edu"
                icon={<Mail size={16} />}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Input
                label="Choose Password"
                type="password"
                placeholder="••••••••"
                icon={<Lock size={16} />}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <Input
                label="Confirm Password"
                type="password"
                placeholder="••••••••"
                icon={<Lock size={16} />}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
              <Checkbox
                label="I accept the cryptographically binding terms of service"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
              />
              <Button type="submit" isLoading={isLoading} className="w-full mt-2">
                Create Account
              </Button>
              <p className="text-center text-xs text-slate-500 pt-2">
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => { setError(''); setScreen('SIGNIN'); }}
                  className="font-bold text-indigo-400 hover:text-indigo-300 transition"
                >
                  Sign In
                </button>
              </p>
            </form>
          )}

          {/* Forgot Password Screen */}
          {screen === 'FORGOT_PASSWORD' && (
            <form onSubmit={handleForgotPassword} className="space-y-4 text-left">
              <Input
                label="Recovery Email Address"
                type="email"
                placeholder="yourmail@domain.com"
                icon={<Mail size={16} />}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <Button type="submit" isLoading={isLoading} className="w-full">
                Send Verification Code
              </Button>
              <Button
                type="button"
                variant="ghost"
                className="w-full"
                onClick={() => { setError(''); setScreen('SIGNIN'); }}
              >
                Back to Sign In
              </Button>
            </form>
          )}

          {/* OTP Verification Screen */}
          {screen === 'VERIFY_OTP' && (
            <form onSubmit={handleVerifyOtp} className="space-y-4 text-left">
              <Input
                label="Enter 4-Digit Verification Code"
                type="text"
                maxLength={4}
                placeholder="1234"
                icon={<Key size={16} />}
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
                className="text-center tracking-widest font-mono text-lg"
              />
              <Button type="submit" isLoading={isLoading} className="w-full">
                Verify Security Code
              </Button>
              <p className="text-center text-xs text-slate-500 pt-2">
                Didn't receive the email?{' '}
                <button
                  type="button"
                  onClick={() => alert('Verification email resent!')}
                  className="font-bold text-indigo-400 hover:text-indigo-300 transition"
                >
                  Resend Code
                </button>
              </p>
            </form>
          )}

          {/* Reset Password Screen */}
          {screen === 'RESET_PASSWORD' && (
            <form onSubmit={handleResetPassword} className="space-y-4 text-left">
              <Input
                label="New Password"
                type="password"
                placeholder="••••••••"
                icon={<Lock size={16} />}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <Input
                label="Confirm New Password"
                type="password"
                placeholder="••••••••"
                icon={<Lock size={16} />}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
              <Button type="submit" isLoading={isLoading} className="w-full">
                Update Password
              </Button>
            </form>
          )}

          {/* Success Screen */}
          {screen === 'SUCCESS' && (
            <div className="flex flex-col items-center py-6 space-y-4">
              <div className="w-16 h-16 bg-emerald-950/60 border border-emerald-900 text-emerald-400 rounded-full flex items-center justify-center animate-pulse">
                <ShieldCheck size={36} />
              </div>
              <p className="text-sm font-semibold text-emerald-400">Secure Handshake Successful</p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
export default AuthPage;
