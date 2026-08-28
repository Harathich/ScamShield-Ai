import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  Lightbulb, 
  HelpCircle, 
  Lock, 
  Sparkles, 
  CheckCircle2, 
  AlertTriangle,
  ArrowRight
} from 'lucide-react';

export default function HowItWorks() {
  const [openFaq, setOpenFaq] = useState(null);

  const steps = [
    {
      num: '01',
      title: 'Paste or Upload Any Suspicious Item',
      desc: 'Copy any strange text message, WhatsApp forward, job offer, or website link. You can even upload a screenshot.',
      icon: '📥',
      badge: 'Step 1'
    },
    {
      num: '02',
      title: '5 AI Guard Agents Analyze It In Seconds',
      desc: 'Our specialized digital detectives check if the website is fake, if a company is being impersonated, and if panic words are used.',
      icon: '🤖',
      badge: 'Step 2'
    },
    {
      num: '03',
      title: 'Get an Instant Risk Score & Clear Advice',
      desc: 'You receive a clear threat rating (Safe or Danger) and simple, jargon-free instructions on what to do (or not do) next.',
      icon: '🛡️',
      badge: 'Step 3'
    }
  ];

  const faqs = [
    {
      q: 'Is my submitted data or screenshot private?',
      a: 'Yes. Content is analyzed securely in real-time and is never sold or used for advertising. You have full control over your local scan history.'
    },
    {
      q: 'What kinds of scams does ScamShield detect?',
      a: 'ScamShield detects Bank KYC & Account Block SMS, Part-Time Telegram Job scams, Fake Courier Delivery links, Investment & Crypto traps, Lottery/Prize claims, and Phishing login pages.'
    },
    {
      q: 'What should I do if a scan reports High Risk?',
      a: 'Stop communicating immediately. Do not click links, do not share OTPs or passwords, and do not send money. Use our direct links to report the message to national cybercrime authorities.'
    }
  ];

  return (
    <section className="w-full max-w-5xl mx-auto my-16 px-4 sm:px-6">
      
      {/* Section Header */}
      <div className="text-center space-y-2 mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold">
          <HelpCircle className="w-3.5 h-3.5" />
          Easy Guide for Everyone
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
          How ScamShield Protects You
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
          No cybersecurity background needed. Here is how our automated safety guard keeps you safe in 3 simple steps.
        </p>
      </div>

      {/* 3 Step Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
        {steps.map((step, idx) => (
          <div 
            key={idx}
            className="rounded-2xl bg-[#0E1626]/80 border border-slate-800 p-6 relative hover:border-blue-500/40 transition-all group hover:scale-[1.02] shadow-xl"
          >
            <div className="flex items-center justify-between mb-4">
              <span className="text-3xl">{step.icon}</span>
              <span className="text-xs font-bold font-mono px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-blue-400">
                {step.badge}
              </span>
            </div>
            <h3 className="text-base font-bold text-white mb-2 group-hover:text-blue-300 transition-colors">
              {step.title}
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              {step.desc}
            </p>
          </div>
        ))}
      </div>

      {/* Frequently Asked Questions */}
      <div className="mt-12 rounded-2xl bg-[#0E1626]/50 border border-slate-800/80 p-6">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-400" />
          <span>Frequently Asked Questions</span>
        </h3>
        <div className="space-y-3">
          {faqs.map((faq, idx) => (
            <div 
              key={idx} 
              className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 text-xs"
            >
              <button
                type="button"
                onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                className="w-full text-left font-semibold text-slate-200 flex items-center justify-between gap-2"
              >
                <span>{faq.q}</span>
                <span className="text-slate-400 text-base">{openFaq === idx ? '−' : '+'}</span>
              </button>
              {openFaq === idx && (
                <p className="mt-2 text-slate-400 leading-relaxed pt-2 border-t border-slate-800 animate-in fade-in duration-150">
                  {faq.a}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

    </section>
  );
}
