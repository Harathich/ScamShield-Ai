import React, { useState, useRef, useEffect } from 'react';
import {
  ShieldCheck,
  Search,
  Globe,
  MessageSquare,
  Briefcase,
  Upload,
  Image as ImageIcon,
  FileText,
  X,
  Sparkles,
  CornerDownLeft,
  AlertCircle,
  Copy
} from 'lucide-react';

export default function InputHero({
  onAnalyze,
  isAnalyzing,
  selectedAgent,
  setSelectedAgent
}) {
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'url' | 'job' | 'image'
  const [inputText, setInputText] = useState('');
  const [inputUrl, setInputUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const samplePresets = [
    {
      label: '🏦 Bank Suspension SMS',
      tab: 'text',
      agent: 'identity',
      text: 'ALERT: Your HDFC Bank account ending 4821 is temporarily blocked due to missing PAN verification. Click http://hdfc-kyc-update.online/verify within 12 hours or account will be suspended.'
    },
    {
      label: '💼 Telegram Part-Time Job',
      tab: 'job',
      agent: 'recruitment',
      text: 'Hello dear! We have an online part-time job evaluating YouTube videos and Google reviews. Earn $150 to $500 daily. Paid daily via USDT or Bank transfer. No experience needed. Contact HR on Telegram @task_earn_daily.'
    },
    {
      label: '🔗 Phishing Domain URL',
      tab: 'url',
      agent: 'domain',
      url: 'https://secure-login-paypal-security-verification.xyz/auth/login'
    },
    {
      label: '🎁 Lottery / Prize Urgency',
      tab: 'text',
      agent: 'language',
      text: 'CONGRATULATIONS! Your mobile number won 2nd prize in the Global WhatsApp Annual Draw ($250,000 USD). Claim your reward code #WA-9921 immediately by paying processing clearance fee of $45.'
    }
  ];

  const handleApplyPreset = (preset) => {
    setActiveTab(preset.tab);
    if (preset.agent) setSelectedAgent(preset.agent);
    if (preset.text) setInputText(preset.text);
    if (preset.url) setInputUrl(preset.url);
    if (preset.tab !== 'image') {
      setSelectedFile(null);
      setPreviewUrl(null);
    }
  };

  const handleFileChange = (file) => {
    if (!file) return;
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (!file.type.startsWith('image/') && !isPdf) {
      alert('Please upload a valid image (PNG, JPG, WEBP) or PDF document.');
      return;
    }
    setSelectedFile(file);
    if (!isPdf) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null); // No standard image preview for PDF
    }
    setActiveTab(isPdf ? 'pdf' : 'image');
  };


  const handlePaste = (e) => {
    if (activeTab === 'image' || activeTab === 'pdf') {
      const items = e.clipboardData?.items;
      if (!items) return;
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf(activeTab === 'image' ? 'image' : 'pdf') !== -1) {
          const file = items[i].getAsFile();
          if (file) {
            handleFileChange(file);
            e.preventDefault();
            break;
          }
        }
      }
    }
  };

  useEffect(() => {
    window.addEventListener('paste', handlePaste);
    return () => {
      window.removeEventListener('paste', handlePaste);
    };
  }, [activeTab]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (isAnalyzing) return;

    if ((activeTab === 'image' || activeTab === 'pdf') && selectedFile) {
      onAnalyze({ file: selectedFile, agent: activeTab === 'image' ? 'ocr' : 'pdf' });
      return;
    }

    if (activeTab === 'url') {
      if (!inputUrl.trim()) return;
      onAnalyze({ url: inputUrl.trim(), text: '', agent: selectedAgent });
      return;
    }

    if (activeTab === 'job' || activeTab === 'text') {
      if (!inputText.trim()) return;
      onAnalyze({ text: inputText.trim(), url: '', agent: selectedAgent });
      return;
    }

  };

  const clearInput = () => {
    setInputText('');
    setInputUrl('');
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  return (
    <section className="relative w-full max-w-4xl mx-auto pt-8 pb-10 px-4 sm:px-6">

      {/* Decorative background glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Hero Header */}
      <div className="text-center relative z-10 space-y-3 mb-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wide">
          <Sparkles className="w-3.5 h-3.5" />
          Autonomous Multi-Agent AI Guard
        </div>
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
          Protect Yourself from Scams <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
            Before You Click or Pay
          </span>
        </h1>
        <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Paste any suspicious message, job proposal, phishing website, or upload a screenshot.
          Our 5 AI agents dissect the threat in seconds.
        </p>
      </div>

      {/* Center Input Card */}
      <div className="relative z-10 rounded-2xl bg-[#0E1626]/90 border border-slate-700/80 shadow-2xl p-4 sm:p-6 backdrop-blur-xl">

        {/* Mode Selector Tabs */}
        <div className="flex items-center gap-1.5 sm:gap-2 p-1.5 rounded-xl bg-slate-900/90 border border-slate-800 mb-4 overflow-x-auto">
          <button
            type="button"
            onClick={() => setActiveTab('text')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === 'text'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Message / Email</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('url')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === 'url'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Globe className="w-4 h-4" />
            <span>Website Link (URL)</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('job')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === 'job'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <Briefcase className="w-4 h-4" />
            <span>Job / Task Offer</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('image')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === 'image'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <ImageIcon className="w-4 h-4" />
            <span>Screenshot (OCR)</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('pdf')}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all whitespace-nowrap ${
              activeTab === 'pdf'
                ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>PDF Document</span>
          </button>
        </div>

        {/* Input Forms */}
        <form onSubmit={handleSubmit} className="space-y-4">

          {/* 1. URL Direct Input Mode */}
          {activeTab === 'url' && (
            <div className="space-y-3">
              <div className="relative flex items-center">
                <Globe className="absolute left-4 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  value={inputUrl}
                  onChange={(e) => setInputUrl(e.target.value)}
                  placeholder="https://suspicious-website-example.com/login"
                  className="w-full pl-12 pr-10 py-3.5 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all font-mono"
                  autoFocus
                />
                {inputUrl && (
                  <button
                    type="button"
                    onClick={() => setInputUrl('')}
                    className="absolute right-3 p-1 rounded-md text-slate-400 hover:text-white"
                  >
                    <X className="w-4 h-4" />
                  </button>
                )}
              </div>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Optional: Paste accompanying message context, SMS or email text that came with the link..."
                rows={2}
                className="w-full px-4 py-3 rounded-xl bg-slate-900/60 border border-slate-800 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-blue-500/60 transition-all resize-none"
              />
            </div>
          )}

          {/* 2. Text / Message / Job Modes */}
          {(activeTab === 'text' || activeTab === 'job') && (
            <div className="relative">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={
                  activeTab === 'job'
                    ? "Paste job offer, Telegram/WhatsApp recruiter message, promised salary, daily tasks, or contract details..."
                    : "Paste suspicious SMS, WhatsApp message, email body, urgency warning, or payment request here..."
                }
                rows={4}
                className="w-full p-4 rounded-xl bg-slate-900/90 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all resize-none leading-relaxed"
                autoFocus
              />
              {inputText && (
                <button
                  type="button"
                  onClick={() => setInputText('')}
                  className="absolute top-3 right-3 p-1.5 rounded-lg bg-slate-800/80 text-slate-400 hover:text-white"
                  title="Clear input"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
              <div className="flex justify-between items-center px-1 mt-1 text-[11px] text-slate-500">
                <span>Supports natural language, code, obfuscated phone numbers & hidden URLs</span>
                <span>{inputText.length} chars</span>
              </div>
            </div>
          )}

          {/* 3. Image OCR / PDF Upload Mode */}
          {(activeTab === 'image' || activeTab === 'pdf') && (
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onPaste={handlePaste}
              tabIndex={0}
              onClick={() => !(previewUrl || (activeTab === 'pdf' && selectedFile)) && fileInputRef.current?.click()}
              className={`relative rounded-xl border-2 border-dashed p-6 text-center cursor-pointer transition-all ${
                dragActive
                  ? 'border-blue-500 bg-blue-500/10'
                  : (previewUrl || (activeTab === 'pdf' && selectedFile))
                  ? 'border-slate-700 bg-slate-900/90 cursor-default'
                  : 'border-slate-700 hover:border-slate-500 bg-slate-900/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept={activeTab === 'image' ? "image/png, image/jpeg, image/webp" : "application/pdf"}
                onChange={(e) => e.target.files && handleFileChange(e.target.files[0])}
                className="hidden"
              />

              {previewUrl || (activeTab === 'pdf' && selectedFile) ? (
                <div className="flex flex-col sm:flex-row items-center gap-4 text-left">
                  <div className="relative w-28 h-28 rounded-lg overflow-hidden border border-slate-700 flex-shrink-0 bg-black flex items-center justify-center">
                    {previewUrl ? (
                      <img src={previewUrl} alt="Upload preview" className="w-full h-full object-cover" />
                    ) : (
                      <FileText className="w-12 h-12 text-blue-400" />
                    )}
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-white truncate max-w-[200px] sm:max-w-xs">
                        {selectedFile?.name}
                      </span>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedFile(null);
                          setPreviewUrl(null);
                        }}
                        className="p-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20"
                        title="Remove file"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-xs text-slate-400">
                      Size: {(selectedFile?.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                    <p className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      {activeTab === 'pdf' ? "Ready for PDF Text Extraction & AI Scan" : "Ready for Optical Character Recognition (OCR) & AI Scan"}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-2 py-4">
                  <div className="mx-auto w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div className="text-sm font-medium text-slate-200">
                    {activeTab === 'pdf' ? "Paste, or drag & drop PDF document here" : "Paste, or drag & drop WhatsApp, SMS, or Email screenshot"}
                  </div>
                  <p className="text-xs text-slate-500">
                    {activeTab === 'pdf' ? "Supports PDF (Up to 10MB)" : "Supports PNG, JPG, WEBP (Up to 10MB)"}
                  </p>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      fileInputRef.current?.click();
                    }}
                    className="mt-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-blue-400 border border-slate-700"
                  >
                    Browse Local File
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Action Row */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">

            {/* Active Agent Badge */}
            <div className="text-xs text-slate-400 flex items-center gap-1.5 w-full sm:w-auto">
              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
              <span>Target:</span>
              <span className="font-semibold text-slate-200 uppercase tracking-wider text-[11px]">
                {selectedAgent === 'all' ? 'All 5 Specialized Agents' : selectedAgent + ' Agent'}
              </span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isAnalyzing || ((activeTab === 'image' || activeTab === 'pdf') ? !selectedFile : !inputText.trim() && !inputUrl.trim())}
              className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold text-sm text-white flex items-center justify-center gap-2.5 transition-all shadow-xl ${
                isAnalyzing
                  ? 'bg-blue-600/70 cursor-not-allowed opacity-90'
                  : ((activeTab === 'image' || activeTab === 'pdf') ? selectedFile : inputText.trim() || inputUrl.trim())
                  ? 'bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 hover:from-blue-500 hover:to-indigo-500 shadow-blue-500/25 hover:shadow-blue-500/40 hover:scale-[1.02] active:scale-[0.98]'
                  : 'bg-slate-800 text-slate-500 border border-slate-700/50 cursor-not-allowed'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Scanning Threat Vectors...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Analyze Risk</span>
                  <CornerDownLeft className="w-3.5 h-3.5 opacity-60 hidden sm:inline" />
                </>
              )}
            </button>

          </div>

        </form>

      </div>

      {/* Preset Example Quick Pills */}
      <div className="mt-5 relative z-10">
        <p className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
          <span>Or test with real-world scam patterns:</span>
        </p>
        <div className="flex flex-wrap gap-2">
          {samplePresets.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplyPreset(preset)}
              className="px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-blue-500/40 hover:bg-blue-900/20 text-slate-300 hover:text-white text-xs font-medium transition-all shadow-sm flex items-center gap-1.5"
            >
              <span>{preset.label}</span>
            </button>
          ))}
        </div>
      </div>

    </section>
  );
}
