import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldAlert, 
  ChevronDown, 
  LayoutDashboard, 
  User, 
  Globe, 
  Briefcase, 
  UserCheck, 
  MessageSquareWarning, 
  Camera, 
  Sparkles,
  Activity,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { checkBackendHealth } from '../services/api';

export default function Navbar({ 
  activeView, 
  setActiveView, 
  selectedAgent, 
  setSelectedAgent, 
  openProfile,
  onResetToHome
}) {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'online' | 'offline' | 'checking'
  const dropdownRef = useRef(null);

  useEffect(() => {
    async function verifyHealth() {
      const res = await checkBackendHealth();
      setBackendStatus(res.online ? 'online' : 'offline');
    }
    verifyHealth();
    const interval = setInterval(verifyHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const agents = [
    { id: 'all', name: 'All Agents (Full Multi-Agent Pipeline)', icon: Sparkles, color: 'text-indigo-400', desc: 'Runs all 5 specialized agents simultaneously' },
    { id: 'domain', name: 'Domain & URL Analyzer', icon: Globe, color: 'text-blue-400', desc: 'Detects phishing domains, homograph attacks & DNS flags' },
    { id: 'recruitment', name: 'Job & Recruitment Scam Detector', icon: Briefcase, color: 'text-amber-400', desc: 'Identifies task scams, fake HRs & deposit traps' },
    { id: 'identity', name: 'Identity & Brand Impersonation', icon: UserCheck, color: 'text-purple-400', desc: 'Validates official bank & corporate identity' },
    { id: 'language', name: 'Psychological Urgency & Tone', icon: MessageSquareWarning, color: 'text-red-400', desc: 'Flags panic manipulation, fear tactics & threats' },
    { id: 'ocr', name: 'Screenshot & OCR Scanner', icon: Camera, color: 'text-emerald-400', desc: 'Extracts & scans text from WhatsApp/SMS screenshots' },
  ];

  const currentAgent = agents.find(a => a.id === selectedAgent) || agents[0];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#0B0F19]/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand / Logo */}
        <div 
          onClick={onResetToHome}
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
            <ShieldAlert className="w-5 h-5 text-white" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                ScamShield<span className="text-blue-500">AI</span>
              </span>
              <span className="text-[10px] uppercase font-semibold tracking-wider px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400">
                v1.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">Multi-Agent Fraud Defense System</p>
          </div>
        </div>

        {/* Center / Navigation Controls */}
        <div className="flex items-center gap-2 sm:gap-4">
          
          {/* Threat Agents Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium rounded-xl bg-slate-900/90 border border-slate-700/70 hover:border-blue-500/50 text-slate-200 hover:text-white transition-all shadow-sm"
              title="Select specific threat detection agent"
            >
              <currentAgent.icon className={`w-4 h-4 ${currentAgent.color}`} />
              <span className="hidden md:inline font-medium">Agent:</span>
              <span className="font-semibold text-blue-400 max-w-[130px] truncate sm:max-w-none">
                {currentAgent.name.split('(')[0]}
              </span>
              <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
            </button>

            {dropdownOpen && (
              <div className="absolute left-0 sm:right-0 sm:left-auto mt-2 w-80 sm:w-96 rounded-2xl bg-[#0E1626] border border-slate-700/80 shadow-2xl p-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                <div className="px-3 py-2 border-b border-slate-800 text-xs font-semibold text-slate-400 flex items-center justify-between">
                  <span>SPECIALIZED THREAT AGENTS</span>
                  <span className="text-[10px] text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">6 Active Modules</span>
                </div>
                <div className="space-y-1 mt-1">
                  {agents.map((agent) => {
                    const Icon = agent.icon;
                    const isSelected = selectedAgent === agent.id;
                    return (
                      <button
                        key={agent.id}
                        onClick={() => {
                          setSelectedAgent(agent.id);
                          setDropdownOpen(false);
                          if (activeView !== 'scanner') setActiveView('scanner');
                        }}
                        className={`w-full text-left p-2.5 rounded-xl flex items-start gap-3 transition-colors ${
                          isSelected 
                            ? 'bg-blue-600/15 border border-blue-500/30 text-white' 
                            : 'hover:bg-slate-800/60 text-slate-300 hover:text-white'
                        }`}
                      >
                        <div className={`p-2 rounded-lg bg-slate-900/80 border border-slate-800 ${agent.color}`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-xs font-bold truncate">{agent.name}</p>
                            {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />}
                          </div>
                          <p className="text-[11px] text-slate-400 leading-snug mt-0.5">{agent.desc}</p>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Dashboard Button */}
          <button
            onClick={() => setActiveView(activeView === 'dashboard' ? 'scanner' : 'dashboard')}
            className={`flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm font-medium rounded-xl transition-all ${
              activeView === 'dashboard'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                : 'bg-slate-900/80 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700'
            }`}
          >
            <LayoutDashboard className="w-4 h-4" />
            <span className="hidden sm:inline">Dashboard</span>
          </button>

          {/* Profile Button */}
          <button
            onClick={openProfile}
            className="flex items-center gap-2 px-3 py-1.5 sm:px-3.5 sm:py-2 text-xs sm:text-sm font-medium rounded-xl bg-slate-900/80 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-all"
            title="User Profile & Security Settings"
          >
            <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-[10px] font-bold text-white">
              H
            </div>
            <span className="hidden md:inline">Profile</span>
          </button>

        </div>

        {/* Backend Live Indicator */}
        <div className="hidden lg:flex items-center gap-2 pl-3 border-l border-slate-800">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900/80 border border-slate-800 text-[11px]">
            <span className={`w-2 h-2 rounded-full ${
              backendStatus === 'online' 
                ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' 
                : backendStatus === 'checking' 
                ? 'bg-amber-400 animate-pulse' 
                : 'bg-indigo-400'
            }`} />
            <span className="text-slate-400">
              {backendStatus === 'online' ? 'Backend Live' : backendStatus === 'checking' ? 'Connecting...' : 'AI Engine Ready'}
            </span>
          </div>
        </div>

      </div>
    </header>
  );
}
