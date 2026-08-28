import React, { useState } from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  TrendingUp, 
  Clock, 
  Search, 
  Trash2, 
  ExternalLink, 
  AlertTriangle,
  FileSpreadsheet,
  RefreshCw,
  Sparkles
} from 'lucide-react';

export default function Dashboard({ 
  scanHistory, 
  onSelectScan, 
  onClearHistory, 
  onNewScan 
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState('ALL'); // 'ALL' | 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW'

  // Statistics calculation
  const totalScans = scanHistory.length;
  const criticalCount = scanHistory.filter(s => s.overall_threat_level === 'CRITICAL' || s.overall_threat_level === 'HIGH').length;
  const safeCount = scanHistory.filter(s => s.overall_threat_level === 'LOW').length;
  const avgRisk = totalScans > 0 
    ? Math.round(scanHistory.reduce((acc, s) => acc + (s.overall_risk_score || 0), 0) / totalScans) 
    : 0;

  const filteredHistory = scanHistory.filter(scan => {
    const matchesLevel = filterLevel === 'ALL' || scan.overall_threat_level === filterLevel;
    const query = (scan.queryContext?.text || '' + scan.queryContext?.url || '').toLowerCase();
    const matchesSearch = !searchTerm || query.includes(searchTerm.toLowerCase());
    return matchesLevel && matchesSearch;
  });

  return (
    <section className="w-full max-w-6xl mx-auto py-8 px-4 sm:px-6 space-y-8 animate-in fade-in duration-200">
      
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            Security Intelligence Center
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-1">
            Threat & Scan Analytics Dashboard
          </h1>
          <p className="text-xs sm:text-sm text-slate-400">
            Real-time telemetry and history of all content analyzed by ScamShield AI.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onNewScan}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs sm:text-sm shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>New Risk Scan</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total Scans */}
        <div className="p-5 rounded-2xl bg-[#0E1626]/90 border border-slate-800 shadow-xl space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>TOTAL ANALYZED</span>
            <Clock className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">{totalScans}</p>
          <p className="text-[11px] text-slate-500">Live & simulated scam scans</p>
        </div>

        {/* High Risk Detected */}
        <div className="p-5 rounded-2xl bg-[#0E1626]/90 border border-red-500/20 shadow-xl space-y-2">
          <div className="flex items-center justify-between text-red-400 text-xs font-semibold">
            <span>THREATS IDENTIFIED</span>
            <ShieldAlert className="w-4 h-4 text-red-400" />
          </div>
          <p className="text-3xl font-extrabold text-red-400">{criticalCount}</p>
          <p className="text-[11px] text-slate-500">Phishing, Impersonation & Traps</p>
        </div>

        {/* Safe Messages */}
        <div className="p-5 rounded-2xl bg-[#0E1626]/90 border border-emerald-500/20 shadow-xl space-y-2">
          <div className="flex items-center justify-between text-emerald-400 text-xs font-semibold">
            <span>VERIFIED SAFE</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold text-emerald-400">{safeCount}</p>
          <p className="text-[11px] text-slate-500">Authentic or clean content</p>
        </div>

        {/* Average Risk */}
        <div className="p-5 rounded-2xl bg-[#0E1626]/90 border border-slate-800 shadow-xl space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>AVERAGE THREAT SCORE</span>
            <TrendingUp className="w-4 h-4 text-purple-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">{avgRisk}%</p>
          <p className="text-[11px] text-slate-500">Weighted multi-agent score</p>
        </div>

      </div>

      {/* History Table Container */}
      <div className="rounded-2xl bg-[#0E1626]/90 border border-slate-800 shadow-2xl p-5 sm:p-6 space-y-4">
        
        {/* Table Controls */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search scan keywords, URLs or text..."
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Level Filter and Clear History */}
          <div className="flex items-center gap-2 overflow-x-auto">
            <select
              value={filterLevel}
              onChange={(e) => setFilterLevel(e.target.value)}
              className="px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 font-semibold focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Severity Levels</option>
              <option value="CRITICAL">Critical Danger</option>
              <option value="HIGH">High Risk</option>
              <option value="MODERATE">Moderate / Caution</option>
              <option value="LOW">Low / Safe</option>
            </select>

            {scanHistory.length > 0 && (
              <button
                type="button"
                onClick={onClearHistory}
                className="px-3 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 text-xs font-semibold transition-colors flex items-center gap-1.5"
                title="Clear local scan records"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Clear History</span>
              </button>
            )}
          </div>

        </div>

        {/* History Rows */}
        {filteredHistory.length === 0 ? (
          <div className="py-12 text-center text-slate-500 space-y-2">
            <ShieldCheck className="w-10 h-10 mx-auto text-slate-600" />
            <p className="text-sm font-medium">No scan history matches your filter.</p>
            <p className="text-xs">Run a new scan from the homepage to populate threat logs.</p>
          </div>
        ) : (
          <div className="space-y-2.5">
            {filteredHistory.map((scan) => {
              const score = scan.overall_risk_score ?? 50;
              const level = scan.overall_threat_level || 'EVALUATED';
              const query = scan.queryContext?.text || scan.queryContext?.url || 'Scanned Content';
              const timeStr = new Date(scan.timestamp).toLocaleString();

              const getBadgeColor = () => {
                if (score >= 75) return 'bg-red-500/15 text-red-400 border-red-500/30';
                if (score >= 50) return 'bg-orange-500/15 text-orange-400 border-orange-500/30';
                if (score >= 25) return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
                return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
              };

              return (
                <div
                  key={scan.id}
                  onClick={() => onSelectScan(scan)}
                  className="p-3.5 sm:p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-blue-500/40 hover:bg-slate-900 transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 group"
                >
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className={`p-2 rounded-lg border text-xs font-mono font-extrabold flex-shrink-0 ${getBadgeColor()}`}>
                      {score}%
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs sm:text-sm font-semibold text-slate-200 truncate group-hover:text-blue-400 transition-colors">
                        {query}
                      </p>
                      <div className="flex items-center gap-3 mt-1 text-[11px] text-slate-400">
                        <span>{timeStr}</span>
                        <span>•</span>
                        <span className="font-mono uppercase text-blue-400 text-[10px]">
                          Agent: {scan.queryContext?.agent || 'All'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 justify-between sm:justify-end">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase border tracking-wider ${getBadgeColor()}`}>
                      {level}
                    </span>
                    <span className="text-xs font-semibold text-blue-400 group-hover:underline flex items-center gap-1">
                      <span>Inspect</span>
                      <ExternalLink className="w-3 h-3" />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

      </div>

    </section>
  );
}
