import React, { useState } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  ChevronDown,
  Globe,
  UserCheck,
  MessageSquareWarning,
  Briefcase,
  Fingerprint,
  Link as LinkIcon,
  Mail,
  Phone,
  Info
} from 'lucide-react';

export default function RiskCard({ result }) {
  const [showDetails, setShowDetails] = useState(false);

  if (!result) return null;

  const score = result.overall_risk_score ?? 50;
  const threatLevel = result.overall_threat_level || (score >= 76 ? 'CRITICAL' : score >= 51 ? 'HIGH' : score >= 26 ? 'MEDIUM' : 'LOW');

  // Color mappings
  const getTheme = () => {
    switch (threatLevel) {
      case 'CRITICAL':
        return {
          bg: 'bg-red-500/10',
          border: 'border-red-500/40',
          text: 'text-red-400',
          badge: 'bg-red-500 text-white shadow-red-500/30',
          meter: '#EF4444',
          label: 'CRITICAL SCAM RISK',
          desc: 'Severe indicators of fraud or credential harvesting. Do NOT interact.'
        };
      case 'HIGH':
        return {
          bg: 'bg-orange-500/10',
          border: 'border-orange-500/40',
          text: 'text-orange-400',
          badge: 'bg-orange-500 text-white shadow-orange-500/30',
          meter: '#F97316',
          label: 'HIGH THREAT DETECTED',
          desc: 'Multiple malicious characteristics identified across AI agents.'
        };
      case 'MEDIUM':
        return {
          bg: 'bg-amber-500/10',
          border: 'border-amber-500/40',
          text: 'text-amber-400',
          badge: 'bg-amber-500 text-white shadow-amber-500/30',
          meter: '#F59E0B',
          label: 'UNVERIFIED / MEDIUM RISK',
          desc: 'Legitimacy could not be independently verified or suspicious elements exist.'
        };
      case 'LOW':
      default:
        return {
          bg: 'bg-emerald-500/10',
          border: 'border-emerald-500/40',
          text: 'text-emerald-400',
          badge: 'bg-emerald-500 text-white shadow-emerald-500/30',
          meter: '#10B981',
          label: 'LIKELY SAFE / LOW RISK',
          desc: 'No aggressive threat signatures detected in this scan.'
        };
    }
  };

  const theme = getTheme();
  const radius = 62;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={`rounded-2xl bg-[#0E1626]/95 border ${theme.border} p-5 sm:p-6 shadow-2xl backdrop-blur-xl flex flex-col justify-between transition-all h-full`}>

      <div>
        {/* Card Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className={`p-2 rounded-xl ${theme.bg} ${theme.text}`}>
              {score >= 50 ? <ShieldAlert className="w-5 h-5" /> : <ShieldCheck className="w-5 h-5" />}
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Overall Threat Diagnostic</h3>
              <p className="text-[11px] text-slate-400">ScamShield Multi-Agent Synthesis</p>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-wider shadow-lg ${theme.badge}`}>
            {threatLevel}
          </span>
        </div>

        {/* Circular Risk Meter & Summary */}
        <div className="flex flex-col sm:flex-row items-center gap-6 my-6">

          {/* Radial Meter SVG */}
          <div className="relative flex items-center justify-center flex-shrink-0">
            <svg className="w-36 h-36 transform -rotate-90">
              <circle
                cx="72"
                cy="72"
                r={radius}
                stroke="#1E293B"
                strokeWidth="10"
                fill="transparent"
              />
              <circle
                cx="72"
                cy="72"
                r={radius}
                stroke={theme.meter}
                strokeWidth="10"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-3xl font-extrabold text-white tracking-tight">{score}%</span>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Risk Score</span>
            </div>
          </div>

          {/* Quick Threat Evaluation */}
          <div className="space-y-2 text-center sm:text-left flex-1">
            <h4 className={`text-base font-bold ${theme.text}`}>
              {theme.label}
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              {theme.desc}
            </p>
            <div className="pt-1 flex items-center justify-center sm:justify-start gap-3 text-xs text-slate-400">
              <span className="font-mono bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                Confidence: {Math.round((result.confidence || 0.92) * 100)}%
              </span>
              {result.isFallback && (
                <span className="text-[10px] text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded border border-amber-400/20">
                  Local AI Guard
                </span>
              )}
            </div>
          </div>

        </div>

        {/* Contributing Factors / Why Risky Section */}
        {(() => {
          // Determine if we have why_risky or safe_indicators from backend report
          const report = result.report || {};
          const whyRisky = report.why_risky || [];
          const safeIndicators = report.safe_indicators || [];
          const useBackendReasons = whyRisky.length > 0 || safeIndicators.length > 0;

          if (useBackendReasons) {
            if (score >= 50) {
              return (
                <div className="mb-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <h5 className="text-xs font-bold text-red-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>Why This Is Risky</span>
                  </h5>
                  <div className="space-y-1.5">
                    {whyRisky.map((factor, idx) => (
                      <div key={idx} className="p-2 rounded-lg bg-slate-900/80 border border-red-500/20 text-xs text-slate-300 flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 flex-shrink-0" />
                        <span className="leading-snug">{factor}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            } else {
              return (
                <div className="mb-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
                  <h5 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Why This Received A Low-Risk Score</span>
                  </h5>
                  <div className="space-y-1.5">
                    {safeIndicators.length > 0 ? safeIndicators.map((factor, idx) => (
                      <div key={idx} className="p-2 rounded-lg bg-slate-900/80 border border-emerald-500/20 text-xs text-slate-300 flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                        <span className="leading-snug">{factor}</span>
                      </div>
                    )) : (
                      <div className="p-2 rounded-lg bg-slate-900/80 border border-emerald-500/20 text-xs text-slate-300 flex items-start gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 flex-shrink-0" />
                        <span className="leading-snug">No significant phishing indicators detected.</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            }
          }

          // Fallback to old contributing factors if backend doesn't provide why_risky
          if (result.contributing_factors && result.contributing_factors.length > 0) {
            return (
              <div className="mb-4">
                <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                  <span>Key Identified Red Flags</span>
                </h5>
                <div className="space-y-1.5">
                  {result.contributing_factors.map((factor, idx) => (
                    <div key={idx} className="p-2 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 flex-shrink-0" />
                      <span className="leading-snug">{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            );
          }

          return null;
        })()}

        {/* Domain Verification Section */}
        {(() => {
          const domainResult = result.detailed_results?.domain;
          if (!domainResult || domainResult.skipped || !domainResult.domain) return null;

          return (
            <div className="mb-4 p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <h5 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5" />
                <span>Domain Verification</span>
              </h5>

              <div className="grid grid-cols-2 gap-2 text-xs mb-3">
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-500 font-bold uppercase mb-0.5">Domain</div>
                  <div className="text-slate-200 font-mono truncate" title={domainResult.domain}>{domainResult.domain || 'Not available'}</div>
                </div>
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-500 font-bold uppercase mb-0.5">Verification</div>
                  <div className={`font-bold ${domainResult.verification_status === 'VERIFIED' ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {domainResult.verification_status ? domainResult.verification_status.replace('_', ' ') : 'Not available'}
                  </div>
                </div>
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-500 font-bold uppercase mb-0.5">Accessibility</div>
                  <div className={`font-bold ${domainResult.access_status === 'ACCESSIBLE' ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {domainResult.access_status ? domainResult.access_status.replace('_', ' ') : 'Not available'}
                  </div>
                </div>
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-500 font-bold uppercase mb-0.5">SSL Certificate</div>
                  <div className="text-slate-200">{domainResult.ssl_status ? domainResult.ssl_status.replace('_', ' ') : 'Not available'}</div>
                </div>
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-500 font-bold uppercase mb-0.5">Domain Age</div>
                  <div className="text-slate-200">{domainResult.domain_age || 'Not available'}</div>
                </div>
                <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
                  <div className="text-[10px] text-slate-500 font-bold uppercase mb-0.5">HTTPS</div>
                  <div className="text-slate-200">{domainResult.ssl_status === 'VALID' ? 'Enabled' : (domainResult.ssl_status === 'UNAVAILABLE' ? 'Disabled/Unavailable' : 'Not available')}</div>
                </div>
              </div>

              {domainResult.explanation && (
                <div className="text-[11px] text-slate-400 leading-relaxed bg-slate-900/40 p-2 rounded italic border border-slate-800/50">
                  {domainResult.explanation}
                </div>
              )}
            </div>
          );
        })()}

        {/* Extracted Metadata Chips */}
        {result.normalized_metadata && (
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-2 mb-4">
            <div className="flex items-center justify-between text-slate-400 text-[11px] font-semibold uppercase">
              <span>Extracted Forensic Indicators</span>
              <span className="font-mono text-blue-400">{result.normalized_metadata.detected_format}</span>
            </div>
            <div className="flex flex-wrap gap-2 text-[11px]">
              {result.normalized_metadata.extracted_urls?.map((url, i) => (
                <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 font-mono truncate max-w-xs">
                  <LinkIcon className="w-3 h-3" /> {url}
                </span>
              ))}
              {result.normalized_metadata.extracted_emails?.map((email, i) => (
                <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-purple-500/10 border border-purple-500/20 text-purple-400 font-mono truncate max-w-xs">
                  <Mail className="w-3 h-3" /> {email}
                </span>
              ))}
              {result.normalized_metadata.extracted_phones?.map((phone, i) => (
                <span key={i} className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono">
                  <Phone className="w-3 h-3" /> {phone}
                </span>
              ))}
              {!result.normalized_metadata.extracted_urls?.length && !result.normalized_metadata.extracted_emails?.length && !result.normalized_metadata.extracted_phones?.length && (
                <span className="text-slate-500 italic text-[11px]">No external links or contact identifiers extracted</span>
              )}
            </div>
          </div>
        )}

      </div>

      {/* Accordion / Drawer: Detailed Agent Breakdown */}
      <div className="pt-2 border-t border-slate-800">
        <button
          type="button"
          onClick={() => setShowDetails(!showDetails)}
          className="w-full py-2 flex items-center justify-between text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
        >
          <span>{showDetails ? 'Hide Agent-by-Agent Findings' : 'View Detailed Agent-by-Agent Findings'}</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${showDetails ? 'rotate-180' : ''}`} />
        </button>

        {showDetails && (
          <div className="mt-3 space-y-2 pt-2 border-t border-slate-800/80 animate-in fade-in duration-200">

            {/* Domain Agent */}
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 font-bold text-slate-200">
                  <Globe className="w-3.5 h-3.5 text-blue-400" />
                  <span>Domain & URL Agent</span>
                </div>
                {result.detailed_results?.domain && !result.detailed_results.domain.skipped && result.detailed_results.domain.risk_score != null && (
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    result.detailed_results.domain.risk_score >= 76 ? 'bg-red-500/20 text-red-400' :
                    result.detailed_results.domain.risk_score >= 51 ? 'bg-orange-500/20 text-orange-400' :
                    result.detailed_results.domain.risk_score >= 26 ? 'bg-amber-500/20 text-amber-400' :
                    'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {result.detailed_results.domain.risk_score}% · {result.detailed_results.domain.risk_level || result.detailed_results.domain.threat_level || 'N/A'}
                  </span>
                )}
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                {result.agent_summary?.domain_agent || 'Evaluated DNS, registration tenure, SSL cert validity, and typo-squatting risks.'}
              </p>
              {result.detailed_results?.domain?.verification_status && (
                <div className="mt-2 space-y-1">
                  <div className="flex justify-between items-center bg-slate-800/50 px-2 py-1 rounded">
                    <span className="text-[10px] uppercase text-slate-500 font-bold">Verification</span>
                    <span className={`text-[10px] font-bold ${result.detailed_results.domain.verification_status === 'VERIFIED' ? 'text-emerald-400' : result.detailed_results.domain.verification_status === 'PARTIALLY_VERIFIED' ? 'text-blue-400' : 'text-amber-400'}`}>
                      {result.detailed_results.domain.verification_status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="flex justify-between items-center bg-slate-800/50 px-2 py-1 rounded">
                    <span className="text-[10px] uppercase text-slate-500 font-bold">Website Access</span>
                    <span className={`text-[10px] font-bold ${result.detailed_results.domain.access_status === 'ACCESSIBLE' ? 'text-emerald-400' : result.detailed_results.domain.access_status === 'ACCESS_RESTRICTED' ? 'text-amber-400' : 'text-red-400'}`}>
                      {result.detailed_results.domain.access_status ? result.detailed_results.domain.access_status.replace('_', ' ') : 'UNKNOWN'}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Threat Agent */}
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 font-bold text-slate-200">
                  <Fingerprint className="w-3.5 h-3.5 text-red-400" />
                  <span>Threat Detection Agent</span>
                </div>
                {result.detailed_results?.threat && !result.detailed_results.threat.skipped && result.detailed_results.threat.risk_score != null && (
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    result.detailed_results.threat.risk_score >= 76 ? 'bg-red-500/20 text-red-400' :
                    result.detailed_results.threat.risk_score >= 51 ? 'bg-orange-500/20 text-orange-400' :
                    result.detailed_results.threat.risk_score >= 26 ? 'bg-amber-500/20 text-amber-400' :
                    'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {result.detailed_results.threat.risk_score}% · {result.detailed_results.threat.threat_level || 'N/A'}
                  </span>
                )}
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                {result.agent_summary?.threat_agent || 'Threat signature check completed.'}
              </p>
            </div>

            {/* Identity Agent */}
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 font-bold text-slate-200">
                  <UserCheck className="w-3.5 h-3.5 text-purple-400" />
                  <span>Identity & Brand Agent</span>
                </div>
                {result.detailed_results?.identity && !result.detailed_results.identity.skipped && result.detailed_results.identity.risk_score != null && (
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    result.detailed_results.identity.risk_score >= 76 ? 'bg-red-500/20 text-red-400' :
                    result.detailed_results.identity.risk_score >= 51 ? 'bg-orange-500/20 text-orange-400' :
                    result.detailed_results.identity.risk_score >= 26 ? 'bg-amber-500/20 text-amber-400' :
                    'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {result.detailed_results.identity.risk_score}% · {result.detailed_results.identity.threat_level || result.detailed_results.identity.verification_status || 'N/A'}
                  </span>
                )}
                {result.detailed_results?.identity?.skipped && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-700/40 text-slate-500">Skipped</span>
                )}
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                {result.agent_summary?.identity_agent || 'Checked for impersonation of banking authorities, courier services, or corporate brands.'}
              </p>
            </div>

            {/* Language Agent */}
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 font-bold text-slate-200">
                  <MessageSquareWarning className="w-3.5 h-3.5 text-red-400" />
                  <span>Language & Urgency Agent</span>
                </div>
                {result.detailed_results?.language && !result.detailed_results.language.skipped && result.detailed_results.language.risk_score != null && (
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    result.detailed_results.language.risk_score >= 76 ? 'bg-red-500/20 text-red-400' :
                    result.detailed_results.language.risk_score >= 51 ? 'bg-orange-500/20 text-orange-400' :
                    result.detailed_results.language.risk_score >= 26 ? 'bg-amber-500/20 text-amber-400' :
                    'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {result.detailed_results.language.risk_score}% · {result.detailed_results.language.threat_level || 'N/A'}
                  </span>
                )}
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                {result.agent_summary?.language_agent || 'Scanned for psychological coercion, artificial deadlines (e.g. 24hr threat), and fear appeals.'}
              </p>
            </div>

            {/* Recruitment Agent */}
            <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 font-bold text-slate-200">
                  <Briefcase className="w-3.5 h-3.5 text-amber-400" />
                  <span>Recruitment & Job Scam Agent</span>
                </div>
                {result.detailed_results?.recruitment && !result.detailed_results.recruitment.skipped && result.detailed_results.recruitment.risk_score != null && (
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    result.detailed_results.recruitment.risk_score >= 76 ? 'bg-red-500/20 text-red-400' :
                    result.detailed_results.recruitment.risk_score >= 51 ? 'bg-orange-500/20 text-orange-400' :
                    result.detailed_results.recruitment.risk_score >= 26 ? 'bg-amber-500/20 text-amber-400' :
                    'bg-emerald-500/20 text-emerald-400'
                  }`}>
                    {result.detailed_results.recruitment.risk_score}% · {result.detailed_results.recruitment.threat_level || result.detailed_results.recruitment.risk_level || 'N/A'}
                  </span>
                )}
                {result.detailed_results?.recruitment?.skipped && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-700/40 text-slate-500">Skipped</span>
                )}
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed">
                {result.agent_summary?.recruitment_agent || 'Analyzed task-based pay models, unauthorized Telegram recruiters, and deposit demands.'}
              </p>
            </div>

          </div>
        )}
      </div>

    </div>
  );
}
