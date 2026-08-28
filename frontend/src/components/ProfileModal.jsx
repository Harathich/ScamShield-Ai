import React, { useState } from 'react';
import { 
  User, 
  X, 
  ShieldCheck, 
  Server, 
  Save, 
  Bell, 
  Key, 
  Trash2, 
  Check, 
  HardDrive,
  Lock
} from 'lucide-react';

export default function ProfileModal({ isOpen, onClose, onClearAllData }) {
  const [apiUrl, setApiUrl] = useState(
    localStorage.getItem('scamshield_api_url') || 'http://localhost:8000'
  );
  const [enableAlerts, setEnableAlerts] = useState(true);
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const handleSaveSettings = (e) => {
    e.preventDefault();
    localStorage.setItem('scamshield_api_url', apiUrl.trim());
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div 
        className="w-full max-w-lg rounded-2xl bg-[#0E1626] border border-slate-700/80 shadow-2xl p-6 relative overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Security Profile & Settings</h2>
              <p className="text-xs text-slate-400">Manage protection tier & backend connection</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Profile Card */}
        <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 my-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-full bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 font-bold">
              H
            </div>
            <div>
              <h3 className="text-sm font-bold text-white">Harathi (Admin User)</h3>
              <p className="text-xs text-slate-400">harathi@scamshield.ai</p>
            </div>
          </div>
          <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            Active Pro Guard
          </span>
        </div>

        {/* Settings Form */}
        <form onSubmit={handleSaveSettings} className="space-y-4 text-xs">
          
          {/* Backend API URL */}
          <div className="space-y-1.5">
            <label className="font-semibold text-slate-300 flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5 text-blue-400" />
              <span>FastAPI Backend Server Endpoint</span>
            </label>
            <input
              type="text"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://localhost:8000"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white font-mono text-xs focus:outline-none focus:border-blue-500"
            />
            <p className="text-[11px] text-slate-500">
              ScamShield AI connects to this API endpoint to execute multi-agent workflows.
            </p>
          </div>

          {/* Real-time Scam Alerts */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <div className="space-y-0.5">
              <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                <Bell className="w-3.5 h-3.5 text-amber-400" />
                <span>High-Risk Scam Audio Alerts</span>
              </span>
              <p className="text-[11px] text-slate-500">Play alert sound when Critical risk (&gt;75%) is detected</p>
            </div>
            <input
              type="checkbox"
              checked={enableAlerts}
              onChange={(e) => setEnableAlerts(e.target.checked)}
              className="w-4 h-4 rounded text-blue-600 focus:ring-0 cursor-pointer"
            />
          </div>

          {/* Privacy & Storage */}
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                <HardDrive className="w-3.5 h-3.5 text-purple-400" />
                <span>Local Privacy & Storage</span>
              </span>
              <span className="text-[11px] text-slate-400">Zero Cloud Retention</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              All scans and OCR data are stored exclusively in your browser’s local storage.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold shadow-lg shadow-blue-500/20 transition-all flex items-center gap-1.5"
            >
              {saved ? (
                <>
                  <Check className="w-4 h-4 text-emerald-300" />
                  <span>Saved!</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Changes</span>
                </>
              )}
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
