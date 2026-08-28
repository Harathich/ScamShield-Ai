import React, { useState } from 'react';
import { 
  Lightbulb, 
  ShieldAlert, 
  CheckSquare, 
  PhoneCall, 
  Copy, 
  Check, 
  ExternalLink, 
  Share2, 
  FileText,
  AlertOctagon,
  LifeBuoy
} from 'lucide-react';

export default function RecommendationsBox({ result }) {
  const [activeTab, setActiveTab] = useState('immediate'); // 'immediate' | 'verification' | 'reporting'
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const score = result.overall_risk_score ?? 50;
  const isHighRisk = score >= 50;
  const report = result.report || {};

  const immediateActions = report.immediate_actions || [
    'DO NOT click on any embedded links or download attachments.',
    'DO NOT share One-Time Passwords (OTP), PINs, or banking passwords.',
    'DO NOT send advance security deposits, gift cards, or crypto transfers.',
    'Block and report the sender number/email immediately.'
  ];

  const verificationSteps = report.verification_steps || [
    'Navigate to the organization’s official website manually by typing its URL.',
    'Call the official customer support line listed on your physical card or bank statement.',
    'Verify recruitment claims on the company’s official LinkedIn career page.'
  ];

  const reportingChannels = report.reporting_channels || [
    { name: 'National Cyber Crime Portal (India)', url: 'https://cybercrime.gov.in', helpline: '1930', desc: 'Official portal for reporting online financial scams & phishing.' },
    { name: 'US Federal Trade Commission (FTC)', url: 'https://reportfraud.ftc.gov', helpline: '1-877-FTC-HELP', desc: 'Federal portal for reporting impersonation & fraud.' },
    { name: 'CERT-In National Incident Response', url: 'https://www.cert-in.org.in', helpline: '1800-11-4949', desc: 'National cybersecurity incident coordination center.' }
  ];

  const handleCopyPlan = () => {
    const textToCopy = `🛡️ SCAMSHIELD AI SAFETY RECOMMENDATION
Risk Level: ${result.overall_threat_level || 'EVALUATED'} (${score}% Risk Score)

🚨 IMMEDIATE ACTIONS:
${immediateActions.map(a => `• ${a}`).join('\n')}

🔍 HOW TO VERIFY:
${verificationSteps.map(v => `• ${v}`).join('\n')}

📢 REPORTING HELPLINE:
${reportingChannels.map(r => `• ${r.name}: ${r.helpline} (${r.url})`).join('\n')}
`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-2xl bg-[#0E1626]/95 border border-indigo-500/30 p-5 sm:p-6 shadow-2xl backdrop-blur-xl flex flex-col justify-between h-full">
      
      <div>
        {/* Header with Title and Copy Action */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Lightbulb className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Actionable Safety Guidance</h3>
              <p className="text-[11px] text-slate-400">Prescriptive protection plan tailored to this threat</p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleCopyPlan}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-slate-300 hover:text-white hover:border-indigo-500/40 transition-all shadow-sm"
            title="Copy plan to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-slate-400" />
                <span>Copy Plan</span>
              </>
            )}
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="grid grid-cols-3 gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 my-4">
          <button
            type="button"
            onClick={() => setActiveTab('immediate')}
            className={`py-2 px-1 text-center rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'immediate'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <AlertOctagon className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="truncate">Immediate Steps</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('verification')}
            className={`py-2 px-1 text-center rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'verification'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <CheckSquare className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="truncate">Verification</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('reporting')}
            className={`py-2 px-1 text-center rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
              activeTab === 'reporting'
                ? 'bg-indigo-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <LifeBuoy className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="truncate">Official Help</span>
          </button>
        </div>

        {/* Tab 1: Immediate Steps */}
        {activeTab === 'immediate' && (
          <div className="space-y-3 animate-in fade-in duration-150">
            <div className={`p-3 rounded-xl border text-xs leading-relaxed ${
              isHighRisk ? 'bg-red-500/10 border-red-500/30 text-red-300' : 'bg-blue-500/10 border-blue-500/30 text-blue-300'
            }`}>
              {report.summary || (isHighRisk 
                ? 'High danger detected. Follow these emergency steps immediately to prevent financial loss.' 
                : 'Content is evaluated with low danger, but maintain standard digital hygiene.')}
            </div>

            <div className="space-y-2">
              {immediateActions.map((action, idx) => (
                <div 
                  key={idx} 
                  className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start gap-3 text-xs text-slate-200"
                >
                  <span className="w-5 h-5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 flex items-center justify-center text-[11px] font-bold flex-shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="leading-relaxed">{action}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 2: Verification Steps */}
        {activeTab === 'verification' && (
          <div className="space-y-3 animate-in fade-in duration-150">
            <p className="text-xs text-slate-400">
              Verify if this message is legitimate through these safe, out-of-band methods:
            </p>
            <div className="space-y-2">
              {verificationSteps.map((step, idx) => (
                <div 
                  key={idx} 
                  className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 flex items-start gap-3 text-xs text-slate-200"
                >
                  <CheckSquare className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{step}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Official Cyber Helplines */}
        {activeTab === 'reporting' && (
          <div className="space-y-3 animate-in fade-in duration-150">
            <p className="text-xs text-slate-400">
              If you experienced money loss or suspect fraud, report immediately to official authorities:
            </p>
            <div className="space-y-2.5">
              {reportingChannels.map((chan, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between font-bold text-white">
                    <span>{chan.name}</span>
                    <a
                      href={chan.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 hover:underline flex items-center gap-1 text-[11px]"
                    >
                      <span>Visit Portal</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  <p className="text-slate-400 text-[11px]">{chan.desc}</p>
                  <div className="pt-1 flex items-center gap-2 text-emerald-400 font-mono text-xs font-semibold">
                    <PhoneCall className="w-3.5 h-3.5" />
                    <span>Toll-Free Helpline: {chan.helpline}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>

      {/* Footer Info / Emergency Note */}
      <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
        <span>Always verify with official institutions directly.</span>
        <span className="text-indigo-400 font-semibold">Zero-Trust Verified</span>
      </div>

    </div>
  );
}
