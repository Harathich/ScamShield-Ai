import React, { useState } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert, User, Mail, Lock, AlertCircle, ArrowRight, Loader2 } from 'lucide-react';

export default function SignupPage() {
  const navigate = useNavigate();
  const { register, isAuthenticated } = useAuth();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // If already authenticated, redirect to home/dashboard
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const validateEmail = (email) => {
    // Requires standard username@domain.extension format (e.g. user@gmail.com, name@company.org)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const nameClean = formData.name.trim();
    const emailClean = formData.email.trim();
    const password = formData.password;
    const confirmPassword = formData.confirmPassword;

    if (!nameClean) {
      setError('Please enter your full name.');
      return;
    }

    if (!emailClean) {
      setError('Please enter your email address.');
      return;
    }

    if (!validateEmail(emailClean)) {
      setError('Please enter a valid email address.');
      return;
    }

    if (!password) {
      setError('Please enter a password.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      const res = await register(nameClean, emailClean, password);
      if (res.success) {
        // Redirect to login page with success message
        navigate('/login', {
          state: { message: 'Account created successfully. Please log in.' }
        });
      } else {
        setError(res.error || 'Registration failed. Please try again.');
      }
    } catch (err) {
      setError('Connection error. Please check your network or server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col justify-center items-center p-4 selection:bg-blue-600 selection:text-white">
      <div className="w-full max-w-md rounded-2xl bg-[#0E1626] border border-slate-800 shadow-2xl p-6 sm:p-8 space-y-6">
        
        {/* ScamShield-AI Branding Header */}
        <div className="flex flex-col items-center text-center space-y-2">
          <Link to="/" className="relative flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-lg shadow-blue-500/25">
            <ShieldAlert className="w-6 h-6 text-white" />
          </Link>
          <div>
            <h1 className="text-xl sm:text-2xl font-black tracking-tight text-white">
              ScamShield<span className="text-blue-500">AI</span>
            </h1>
            <h2 className="text-sm font-bold text-slate-300 mt-1">Create your account</h2>
            <p className="text-xs text-slate-400">Enter your details below to register</p>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2.5 animate-in fade-in duration-150">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Signup Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          
          {/* Name Input */}
          <div className="space-y-1">
            <label className="font-semibold text-slate-300">Name</label>
            <div className="relative">
              <User className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="John Doe"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-xs"
              />
            </div>
          </div>

          {/* Email Input */}
          <div className="space-y-1">
            <label className="font-semibold text-slate-300">Email</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="text"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="user@example.com"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-xs"
              />
            </div>
          </div>

          {/* Password Input */}
          <div className="space-y-1">
            <label className="font-semibold text-slate-300">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-xs"
              />
            </div>
          </div>

          {/* Confirm Password Input */}
          <div className="space-y-1">
            <label className="font-semibold text-slate-300">Confirm Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-500" />
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors text-xs"
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 mt-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold shadow-md shadow-blue-600/20 transition-all flex items-center justify-center gap-2 text-xs"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Creating Account...</span>
              </>
            ) : (
              <>
                <span>Create Account</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </form>

        {/* Link to Login */}
        <div className="pt-2 text-center text-xs text-slate-400 border-t border-slate-800/80">
          <span>Already have an account? </span>
          <Link to="/login" className="font-bold text-blue-400 hover:text-blue-300 transition-colors">
            Log in
          </Link>
        </div>

      </div>
    </div>
  );
}
