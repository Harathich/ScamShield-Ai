import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Globe, 
  UserCheck, 
  MessageSquareWarning, 
  Briefcase, 
  CheckCircle2, 
  Loader2 
} from 'lucide-react';

export default function AnalyzingOverlay({ selectedAgent }) {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { label: 'Normalizing Content & Extracting URLs/Emails', icon: Shield, agent: 'preprocessor' },
    { label: 'Domain Agent: Verifying Domain Age, SSL & Typo-Squatting', icon: Globe, agent: 'domain' },
    { label: 'Identity Agent: Detecting Brand Impersonation & Spoofing', icon: UserCheck, agent: 'identity' },
    { label: 'Language Agent: Analyzing Fear, Urgency & Pressure Tactics', icon: MessageSquareWarning, agent: 'language' },
    { label: 'Recruitment Agent: Checking Work-From-Home & Task Traps', icon: Briefcase, agent: 'recruitment' },
    { label: 'Risk Manager: Calculating Unified Multi-Agent Threat Score', icon: Shield, agent: 'orchestrator' },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 450);
    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <div className="w-full max-w-4xl mx-auto my-6 px-4">
      <div className="rounded-2xl bg-[#0E1626]/95 border border-blue-500/30 p-6 shadow-2xl backdrop-blur-xl relative overflow-hidden">
        
        {/* Glow accent */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 animate-pulse" />

        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
              <Loader2 className="w-5 h-5 animate-spin" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Multi-Agent AI Pipeline In Progress</h3>
              <p className="text-xs text-slate-400">Correlating threat vectors across 5 specialized defense agents</p>
            </div>
          </div>
          <span className="text-xs font-mono text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-full border border-blue-500/20">
            {Math.round(((currentStep + 1) / steps.length) * 100)}%
          </span>
        </div>

        {/* Step Items */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-5">
          {steps.map((step, idx) => {
            const Icon = step.icon;
            const isDone = idx < currentStep;
            const isCurrent = idx === currentStep;

            return (
              <div
                key={idx}
                className={`p-3 rounded-xl flex items-center gap-3 border transition-all ${
                  isCurrent
                    ? 'bg-blue-600/15 border-blue-500/40 text-white shadow-lg shadow-blue-500/10 scale-[1.01]'
                    : isDone
                    ? 'bg-slate-900/60 border-slate-800 text-slate-300'
                    : 'bg-slate-900/30 border-slate-800/40 text-slate-500 opacity-60'
                }`}
              >
                <div className={`p-1.5 rounded-lg ${
                  isCurrent 
                    ? 'bg-blue-500 text-white animate-pulse' 
                    : isDone 
                    ? 'bg-emerald-500/20 text-emerald-400' 
                    : 'bg-slate-800 text-slate-500'
                }`}>
                  {isDone ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 animate-spin text-white" />
                  ) : (
                    <Icon className="w-4 h-4" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium truncate">{step.label}</p>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
}
