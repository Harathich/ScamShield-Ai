import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
import Navbar from './components/Navbar';
import InputHero from './components/InputHero';
import AnalyzingOverlay from './components/AnalyzingOverlay';
import RiskCard from './components/RiskCard';
import RecommendationsBox from './components/RecommendationsBox';
import HowItWorks from './components/HowItWorks';
import Dashboard from './components/Dashboard';
import ProfileModal from './components/ProfileModal';
import { analyzeContent } from './services/api';
import { ShieldCheck, RotateCcw } from 'lucide-react';

export default function App() {
  const [activeView, setActiveView] = useState('scanner'); // 'scanner' | 'dashboard'
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  
  // Persisted Scan History
  const [scanHistory, setScanHistory] = useState(() => {
    try {
      const saved = localStorage.getItem('scamshield_scan_history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const resultsRef = useRef(null);

  useEffect(() => {
    try {
      localStorage.setItem('scamshield_scan_history', JSON.stringify(scanHistory));
    } catch (e) {
      console.error('Failed to save history', e);
    }
  }, [scanHistory]);

  const handleAnalyze = async (payload) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);

    // Scroll slightly down to keep analyzing overlay visible
    setTimeout(() => {
      window.scrollTo({ top: 320, behavior: 'smooth' });
    }, 100);

    try {
      const result = await analyzeContent(payload);
      setAnalysisResult(result);
      
      // Add to history
      setScanHistory((prev) => [result, ...prev.slice(0, 49)]);

      // Confetti for safe items
      if (result.overall_risk_score <= 30) {
        confetti({
          particleCount: 70,
          spread: 60,
          origin: { y: 0.6 }
        });
      }

      // Smooth scroll to results
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 300);

    } catch (error) {
      console.error('Scan execution error:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSelectHistoricalScan = (scan) => {
    setAnalysisResult(scan);
    setActiveView('scanner');
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear all local scan logs?')) {
      setScanHistory([]);
      localStorage.removeItem('scamshield_scan_history');
    }
  };

  const handleResetToHome = () => {
    setActiveView('scanner');
    setSelectedAgent('all');
    setAnalysisResult(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col justify-between selection:bg-blue-600 selection:text-white">
      
      {/* Navigation Header */}
      <Navbar
        activeView={activeView}
        setActiveView={setActiveView}
        selectedAgent={selectedAgent}
        setSelectedAgent={setSelectedAgent}
        openProfile={() => setIsProfileOpen(true)}
        onResetToHome={handleResetToHome}
      />

      {/* Main Content Body */}
      <main className="flex-1">
        
        {activeView === 'scanner' ? (
          <div>
            {/* Center Hero & Multi-Mode Input */}
            <InputHero
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
              selectedAgent={selectedAgent}
              setSelectedAgent={setSelectedAgent}
            />

            {/* Analyzing Progress Visualizer */}
            {isAnalyzing && (
              <AnalyzingOverlay selectedAgent={selectedAgent} />
            )}

            {/* Results Section: 2 Split Dedicated Containers */}
            {analysisResult && !isAnalyzing && (
              <div 
                ref={resultsRef}
                className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-in fade-in slide-in-from-bottom-4 duration-300"
              >
                {/* Results Section Title Bar */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-6 mb-6 border-b border-slate-800">
                  <div>
                    <h2 className="text-xl sm:text-2xl font-black text-white flex items-center gap-2">
                      <span>Analysis Results</span>
                      <span className="text-xs font-mono font-normal text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-full border border-blue-500/20">
                        Scan ID: {analysisResult.id}
                      </span>
                    </h2>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Evaluated on {new Date(analysisResult.timestamp).toLocaleTimeString()} using ScamShield Autonomous Pipeline
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setAnalysisResult(null);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    className="self-start sm:self-auto px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 text-xs font-semibold text-slate-300 hover:text-white transition-all flex items-center gap-1.5"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                    <span>Run Another Scan</span>
                  </button>
                </div>

                {/* 2-Column Split Containers: Risk Score (Left) vs Recommendations (Right) */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
                  
                  {/* Container 1: Risk Assessment & Signals */}
                  <RiskCard result={analysisResult} />

                  {/* Container 2: Actionable Recommendations Box */}
                  <RecommendationsBox result={analysisResult} />

                </div>
              </div>
            )}

            {/* How It Works (For Non-Tech Users) */}
            <HowItWorks />
          </div>
        ) : (
          /* Dashboard Analytics View */
          <Dashboard
            scanHistory={scanHistory}
            onSelectScan={handleSelectHistoricalScan}
            onClearHistory={handleClearHistory}
            onNewScan={() => setActiveView('scanner')}
          />
        )}

      </main>

      {/* Profile & Settings Modal */}
      <ProfileModal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        onClearAllData={handleClearHistory}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#070A12] py-8 px-4 text-center text-xs text-slate-400 space-y-2">
        <div className="flex items-center justify-center gap-2 font-bold text-slate-200">
          <ShieldCheck className="w-4 h-4 text-blue-500" />
          <span>ScamShield AI • Autonomous Multi-Agent Threat Defense</span>
        </div>
        <p className="text-slate-400 max-w-lg mx-auto leading-relaxed text-[11px]">
          Always verify banking, job, and financial claims directly with official institutions. ScamShield provides automated heuristic intelligence to prevent fraud.
        </p>
      </footer>

    </div>
  );
}
