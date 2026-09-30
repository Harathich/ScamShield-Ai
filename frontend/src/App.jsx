import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import confetti from 'canvas-confetti';

import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import PublicLandingPage from './pages/PublicLandingPage';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';

import Navbar from './components/Navbar';
import InputHero from './components/InputHero';
import AnalyzingOverlay from './components/AnalyzingOverlay';
import RiskCard from './components/RiskCard';
import RecommendationsBox from './components/RecommendationsBox';
import HowItWorks from './components/HowItWorks';
import Dashboard from './components/Dashboard';
import ProfileModal from './components/ProfileModal';

import { 
  analyzeContent, 
  fetchScanHistory, 
  deleteScanHistory 
} from './services/api';

import { ShieldCheck, RotateCcw, ArrowLeft } from 'lucide-react';

function ProtectedMainWorkspace({ defaultView = 'scanner', forceProfileOpen = false }) {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [activeView, setActiveView] = useState(defaultView); // 'scanner' | 'dashboard'
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isProfileOpen, setIsProfileOpen] = useState(forceProfileOpen);
  const [scanHistory, setScanHistory] = useState([]);

  const resultsRef = useRef(null);

  // Sync activeView with prop changes
  useEffect(() => {
    setActiveView(defaultView);
  }, [defaultView]);

  // Fetch scan history for authenticated user
  const loadDbHistory = async () => {
    const res = await fetchScanHistory();
    if (res.success && res.data) {
      setScanHistory(res.data);
    }
  };

  useEffect(() => {
    if (user) {
      loadDbHistory();
    }
  }, [user]);

  const handleAnalyze = async (payload) => {
    setIsAnalyzing(true);
    setAnalysisResult(null);

    setTimeout(() => {
      window.scrollTo({ top: 320, behavior: 'smooth' });
    }, 100);

    try {
      const result = await analyzeContent(payload);
      setAnalysisResult(result);
      
      // Refresh scan history from backend DB
      setTimeout(loadDbHistory, 600);

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

  const handleDeleteScan = async (scanId) => {
    if (typeof scanId === 'number') {
      const res = await deleteScanHistory(scanId);
      if (res.success) {
        setScanHistory(prev => prev.filter(s => s.id !== scanId));
      } else {
        alert(res.error || 'Failed to delete scan from backend');
      }
    }
  };

  const handleClearHistory = () => {
    if (window.confirm('Are you sure you want to clear your scan view? Saved entries remain in your secure account database.')) {
      setScanHistory([]);
    }
  };

  const handleResetToHome = () => {
    setActiveView('scanner');
    setSelectedAgent('all');
    setAnalysisResult(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Back button handler using browser history
  const handleGoBack = () => {
    if (analysisResult) {
      setAnalysisResult(null);
    } else if (activeView === 'dashboard') {
      setActiveView('scanner');
    } else {
      navigate(-1);
    }
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
        
        {/* Navigation Breadcrumb / Back button if deep in view */}
        {(analysisResult || activeView === 'dashboard') && (
          <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 pt-4">
            <button
              onClick={handleGoBack}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white text-xs font-semibold transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back</span>
            </button>
          </div>
        )}

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

            {/* Results Section */}
            {analysisResult && !isAnalyzing && (
              <div 
                ref={resultsRef}
                className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-in fade-in slide-in-from-bottom-4 duration-300"
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

                {/* 2-Column Split Containers */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
                  <RiskCard result={analysisResult} />
                  <RecommendationsBox result={analysisResult} />
                </div>
              </div>
            )}

            {/* How It Works */}
            <HowItWorks />
          </div>
        ) : (
          /* Dashboard Analytics View */
          <Dashboard
            scanHistory={scanHistory}
            onSelectScan={handleSelectHistoricalScan}
            onDeleteScan={handleDeleteScan}
            onClearHistory={handleClearHistory}
            onNewScan={() => setActiveView('scanner')}
            user={user}
          />
        )}

      </main>

      {/* Profile & Settings Modal */}
      <ProfileModal
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        user={user}
        onLogout={logout}
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

function HomeRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B0F19] text-white flex flex-col items-center justify-center space-y-4">
        <div className="relative flex items-center justify-center w-12 h-12 rounded-2xl bg-blue-600/20 border border-blue-500/30 text-blue-400">
          <ShieldCheck className="w-6 h-6 animate-pulse" />
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <ProtectedMainWorkspace defaultView="scanner" />;
  }

  return <PublicLandingPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Home & Landing */}
          <Route path="/" element={<HomeRoute />} />

          {/* Public Authentication Pages */}
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/login" element={<LoginPage />} />

          {/* Protected Application Routes */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <ProtectedMainWorkspace defaultView="dashboard" />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/scan" 
            element={
              <ProtectedRoute>
                <ProtectedMainWorkspace defaultView="scanner" />
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/history" 
            element={
              <ProtectedRoute>
                <ProtectedMainWorkspace defaultView="dashboard" />
              </ProtectedRoute>
            } 
          />

          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <ProtectedMainWorkspace defaultView="scanner" forceProfileOpen={true} />
              </ProtectedRoute>
            } 
          />

          {/* Fallback Route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
