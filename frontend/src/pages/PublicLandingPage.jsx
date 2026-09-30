import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Globe, 
  Briefcase, 
  UserCheck, 
  MessageSquareWarning, 
  Camera, 
  ArrowRight,
  Sparkles,
  Lock,
  Database,
  Search
} from 'lucide-react';

export default function PublicLandingPage() {
  const agents = [
    { name: 'Threat Analysis Agent', icon: ShieldAlert, color: 'text-indigo-400', desc: 'Detects phishing signatures, deceptive patterns, and financial traps.' },
    { name: 'Domain Intelligence Agent', icon: Globe, color: 'text-blue-400', desc: 'Analyzes WHOIS, SSL certificates, homograph attacks, and TLD reputation.' },
    { name: 'Language & Urgency Agent', icon: MessageSquareWarning, color: 'text-red-400', desc: 'Flags panic manipulation, coercion tactics, and artificial urgency.' },
    { name: 'Identity & Brand Agent', icon: UserCheck, color: 'text-purple-400', desc: 'Verifies official corporate identities and prevents brand impersonation.' },
    { name: 'Recruitment Scam Agent', icon: Briefcase, color: 'text-amber-400', desc: 'Identifies fake job offers, task scams, and advance deposit schemes.' },
    { name: 'Screenshot OCR Scanner', icon: Camera, color: 'text-emerald-400', desc: 'Extracts and scans text directly from WhatsApp and SMS screenshots.' },
  ];

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col justify-between selection:bg-blue-600 selection:text-white">
      
      {/* Public Header Navbar */}
      <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-[#0B0F19]/90 backdrop-blur-md">
        <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-extrabold text-lg tracking-tight text-white">
                ScamShield<span className="text-blue-500">AI</span>
              </span>
              <p className="text-[11px] text-slate-400 hidden sm:block">Autonomous Fraud Defense</p>
            </div>
          </Link>

          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="px-4 py-2 text-xs sm:text-sm font-semibold rounded-xl bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 transition-all"
            >
              Log In
            </Link>
            <Link
              to="/signup"
              className="px-4 py-2 text-xs sm:text-sm font-bold rounded-xl bg-blue-600 hover:bg-blue-500 text-white shadow-md shadow-blue-600/20 transition-all flex items-center gap-1.5"
            >
              <span>Sign Up</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 text-center space-y-8">
          
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
            <Sparkles className="w-4 h-4" />
            <span>Autonomous Multi-Agent Cyber Fraud Defense</span>
          </div>

          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white max-w-4xl mx-auto leading-tight">
            Protect Yourself from Phishing, Impersonation & Digital Fraud
          </h1>

          <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
            ScamShield AI orchestrates 5 specialized AI intelligence agents to evaluate suspicious messages, phishing URLs, recruitment scams, and screenshot evidence in real time.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              to="/signup"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-lg shadow-blue-600/30 transition-all flex items-center justify-center gap-2"
            >
              <span>Create Free Account</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/login"
              className="w-full sm:w-auto px-6 py-3.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white font-semibold text-sm transition-all text-center"
            >
              Log In to Workspace
            </Link>
          </div>

          {/* Feature Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 pt-16 text-left">
            {agents.map((agent, i) => {
              const Icon = agent.icon;
              return (
                <div 
                  key={i} 
                  className="p-6 rounded-2xl bg-[#0E1626] border border-slate-800/90 hover:border-blue-500/30 transition-all space-y-3"
                >
                  <div className={`p-3 w-fit rounded-xl bg-slate-900 border border-slate-800 ${agent.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-white">{agent.name}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{agent.desc}</p>
                </div>
              );
            })}
          </div>

        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#070A12] py-8 px-4 text-center text-xs text-slate-400 space-y-2">
        <div className="flex items-center justify-center gap-2 font-bold text-slate-200">
          <ShieldCheck className="w-4 h-4 text-blue-500" />
          <span>ScamShield AI • Multi-Agent Threat Defense</span>
        </div>
        <p className="text-slate-400 max-w-lg mx-auto leading-relaxed text-[11px]">
          Always verify banking and job claims directly with official institutions. ScamShield provides automated heuristic intelligence to prevent digital fraud.
        </p>
      </footer>

    </div>
  );
}
