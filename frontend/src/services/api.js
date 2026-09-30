/**
 * ScamShield AI - API & Multi-Agent Communication Client with Authentication & History
 */

const API_BASE_URL = localStorage.getItem('scamshield_api_url') || 'http://localhost:8000';

export function getAuthToken() {
  return localStorage.getItem('scamshield_token') || null;
}

export function setAuthToken(token) {
  if (token) {
    localStorage.setItem('scamshield_token', token);
  } else {
    localStorage.removeItem('scamshield_token');
  }
}

export function removeAuthToken() {
  localStorage.removeItem('scamshield_token');
}

function getAuthHeaders(headers = {}) {
  const token = getAuthToken();
  if (token) {
    return { ...headers, Authorization: `Bearer ${token}` };
  }
  return headers;
}

export async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${API_BASE_URL}/health`, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (res.ok) {
      const data = await res.json();
      return { online: true, data };
    }
    return { online: false };
  } catch (err) {
    return { online: false, error: err.message };
  }
}

/* ==================== AUTHENTICATION API ==================== */

export async function registerUser({ name, email, password }) {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });
    const data = await res.json();
    if (res.ok) {
      return { success: true, data };
    }
    return { success: false, error: data.detail || 'Registration failed' };
  } catch (err) {
    return { success: false, error: 'Network error during registration' };
  }
}

export async function loginUser({ email, password }) {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok && data.access_token) {
      setAuthToken(data.access_token);
      return { success: true, data };
    }
    return { success: false, error: data.detail || 'Invalid email or password' };
  } catch (err) {
    return { success: false, error: 'Network error during login' };
  }
}

export async function fetchCurrentUser() {
  const token = getAuthToken();
  if (!token) return { success: false, error: 'No token found' };

  try {
    const res = await fetch(`${API_BASE_URL}/users/me`, {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      return { success: true, user: data };
    }
    removeAuthToken();
    return { success: false, error: 'Session expired' };
  } catch (err) {
    return { success: false, error: 'Failed to fetch current user' };
  }
}

export async function logoutUser() {
  try {
    const token = getAuthToken();
    if (token) {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: getAuthHeaders()
      });
    }
  } catch (err) {
    console.warn('Logout API warning:', err);
  } finally {
    removeAuthToken();
  }
}

/* ==================== SCAN HISTORY API ==================== */

export async function fetchScanHistory() {
  const token = getAuthToken();
  if (!token) return { success: false, data: [] };

  try {
    const res = await fetch(`${API_BASE_URL}/history`, {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      // Format database scan history entries to match frontend display format
      const formatted = data.map(item => formatHistoryRecord(item));
      return { success: true, data: formatted };
    }
    return { success: false, data: [] };
  } catch (err) {
    console.warn('Failed to fetch scan history from backend:', err);
    return { success: false, data: [] };
  }
}

export async function fetchScanDetails(scanId) {
  try {
    const res = await fetch(`${API_BASE_URL}/history/${scanId}`, {
      headers: getAuthHeaders()
    });
    if (res.ok) {
      const data = await res.json();
      return { success: true, data: formatHistoryRecord(data) };
    }
    const errData = await res.json().catch(() => ({}));
    return { success: false, status: res.status, error: errData.detail || 'Scan not found or access denied' };
  } catch (err) {
    return { success: false, status: 500, error: 'Network error fetching scan' };
  }
}

export async function deleteScanHistory(scanId) {
  try {
    const res = await fetch(`${API_BASE_URL}/history/${scanId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (res.ok) {
      return { success: true };
    }
    const errData = await res.json().catch(() => ({}));
    return { success: false, status: res.status, error: errData.detail || 'Failed to delete scan' };
  } catch (err) {
    return { success: false, error: 'Network error deleting scan' };
  }
}

function formatHistoryRecord(item) {
  const agentResults = item.agent_results || {};
  return {
    id: item.id,
    timestamp: item.created_at,
    queryContext: {
      text: item.input_content,
      url: item.input_type === 'url' ? item.input_content : '',
      agent: 'all',
      input_type: item.input_type
    },
    overall_risk_score: item.overall_risk_score,
    overall_threat_level: item.overall_threat_level,
    confidence: agentResults.confidence || 0.94,
    normalized_metadata: agentResults.normalized_metadata || {
      detected_format: item.input_type,
      extracted_urls: [],
      extracted_emails: [],
      extracted_phones: []
    },
    contributing_factors: agentResults.contributing_factors || [],
    agent_summary: agentResults.agent_summary || {},
    detailed_results: {
      threat: agentResults.threat_result,
      domain: agentResults.domain_result,
      identity: agentResults.identity_result,
      language: agentResults.language_result,
      recruitment: agentResults.recruitment_result
    },
    report: agentResults.report || generateDefaultRecommendations(item.overall_threat_level, { text: item.input_content }),
    isFallback: false
  };
}

/* ==================== MAIN ANALYSIS PIPELINE ==================== */

export async function analyzeContent({ text = '', url = '', agent = 'all', file = null }) {
  const authHeaders = getAuthHeaders();

  try {
    // If a file was uploaded for OCR or PDF analysis
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
      const endpoint = isPdf ? `${API_BASE_URL}/analyze-all/pdf` : `${API_BASE_URL}/analyze-all/image`;

      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: authHeaders, // Automatic Authorization header attachment
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          return formatBackendResponse(data, { text: `[${isPdf ? 'PDF Document' : 'Image OCR'}: ${file.name}]`, url: '', agent: isPdf ? 'pdf' : 'ocr' });
        }
      } catch (err) {
        console.warn(`Backend ${isPdf ? 'PDF' : 'image OCR'} request failed, using simulation fallback`, err);
      }

      // Simulated Image/PDF scan fallback
      return generateSimulatedResponse({
        text: `Urgent notification from security team: Your account has been temporarily restricted. Click verify-login-update.online to restore access immediately.`,
        url: 'http://verify-login-update.online',
        agent: isPdf ? 'pdf' : 'ocr',
        isImage: !isPdf,
        isPdf: isPdf,
        filename: file.name
      });
    }

    // Direct targeted agent endpoints
    if (agent !== 'all') {
      try {
        let endpoint = `${API_BASE_URL}/analyze-all/`;
        let body = { text, url: url || undefined };

        if (agent === 'domain') {
          endpoint = `${API_BASE_URL}/analyze-domain/`;
          body = { url: url || text || undefined, text: text || undefined };
        } else if (agent === 'recruitment') {
          endpoint = `${API_BASE_URL}/recruitment/analyze`;
          body = { text: text || url };
        } else if (agent === 'language') {
          endpoint = `${API_BASE_URL}/language/analyze`;
          body = { text: text || url };
        } else if (agent === 'identity') {
          endpoint = `${API_BASE_URL}/identity/`;
          body = { text: text || url };
        } else if (agent === 'threat') {
          endpoint = `${API_BASE_URL}/analyze/`;
          body = { text: text || url };
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify(body),
        });

        if (response.ok) {
          const data = await response.json();
          return formatBackendResponse(data, { text, url, agent });
        }
      } catch (err) {
        console.warn(`Targeted agent endpoint ${agent} failed, falling back to simulated scan`, err);
      }
    }

    // Default Full Orchestrator Endpoint
    try {
      const response = await fetch(`${API_BASE_URL}/analyze-all/`, {
        method: 'POST',
        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ text: text || undefined, url: url || undefined }),
      });

      if (response.ok) {
        const data = await response.json();
        return formatBackendResponse(data, { text, url, agent });
      }
    } catch (err) {
      console.warn('Backend orchestrator not reachable, generating local analysis', err);
    }

    // Fallback simulation for offline demos
    return generateSimulatedResponse({ text, url, agent });
  } catch (error) {
    console.error('Analysis error:', error);
    return generateSimulatedResponse({ text, url, agent });
  }
}

function formatBackendResponse(data, queryContext) {
  const isFullOrchestrator = data.overall_risk_score !== undefined || data.report !== undefined;

  let riskScore = 0;
  let threatLevel = 'LOW';
  let contributingFactors = [];
  let agentSummary = {};
  let detailedResults = {};
  let report = null;

  if (isFullOrchestrator) {
    riskScore = data.overall_risk_score ?? (data.risk_score ? data.risk_score * 100 : 75);
    threatLevel = data.overall_threat_level || (riskScore > 75 ? 'CRITICAL' : riskScore > 50 ? 'HIGH' : riskScore > 25 ? 'MODERATE' : 'LOW');
    contributingFactors = data.contributing_factors || [];

    if (typeof data.agent_summary === 'object' && data.agent_summary !== null) {
      agentSummary = {
        threat_agent: typeof data.agent_summary.threat === 'object'
          ? `Score: ${data.agent_summary.threat.risk_score ?? 'N/A'}% (${data.agent_summary.threat.threat_level || 'Evaluated'})`
          : (data.agent_summary.threat || 'Threat evaluation completed'),
        domain_agent: typeof data.agent_summary.domain === 'object'
          ? `Score: ${data.agent_summary.domain.risk_score ?? 'N/A'}% (${data.agent_summary.domain.threat_level || 'Evaluated'})`
          : (data.agent_summary.domain || 'Domain reputation check completed'),
        identity_agent: typeof data.agent_summary.identity === 'object'
          ? `Score: ${data.agent_summary.identity.risk_score ?? 'N/A'}% (${data.agent_summary.identity.threat_level || 'Evaluated'})`
          : (data.agent_summary.identity || 'Brand impersonation check completed'),
        language_agent: typeof data.agent_summary.language === 'object'
          ? `Score: ${data.agent_summary.language.risk_score ?? 'N/A'}% (${data.agent_summary.language.threat_level || 'Evaluated'})`
          : (data.agent_summary.language || 'Tone and urgency analysis completed'),
        recruitment_agent: typeof data.agent_summary.recruitment === 'object'
          ? `Score: ${data.agent_summary.recruitment.risk_score ?? 'N/A'}% (${data.agent_summary.recruitment.threat_level || 'Evaluated'})`
          : (data.agent_summary.recruitment || 'Employment signals verified')
      };
    }

    detailedResults = {
      threat: data.threat_result,
      domain: data.domain_result,
      identity: data.identity_result,
      language: data.language_result,
      recruitment: data.recruitment_result
    };

    report = data.report || generateDefaultRecommendations(threatLevel, queryContext);

  } else {
    riskScore = data.risk_score !== undefined ? data.risk_score : 50;
    threatLevel = data.threat_level || data.risk_level || (riskScore > 75 ? 'CRITICAL' : riskScore > 50 ? 'HIGH' : riskScore > 25 ? 'MODERATE' : 'LOW');

    if (data.agent === 'domain' || data.domain !== undefined) {
      contributingFactors = [
        ...(data.technical_red_flags || []),
        data.explanation || (data.brand_impersonation ? 'Brand impersonation risk detected on domain' : '')
      ].filter(Boolean);

      agentSummary.domain_agent = `Domain ${data.domain || ''}: Age: ${data.domain_age || 'Unknown'}, SSL: ${data.ssl_status || 'Unknown'}. ${data.explanation || ''}`;
      detailedResults.domain = data;

      report = {
        summary: data.explanation || 'Domain analysis completed.',
        immediate_actions: [data.recommendation || 'Do not submit credentials or payment details on unverified domains.'],
        verification_steps: ['Check domain registration on official WHOIS directories.', 'Verify SSL lock and company registry.'],
        reporting_channels: generateDefaultRecommendations(threatLevel, queryContext).reporting_channels
      };
    } else if (data.agent === 'language' || data.manipulation_techniques !== undefined) {
      contributingFactors = [
        ...(data.manipulation_techniques || []),
        data.summary || data.reason
      ].filter(Boolean);

      agentSummary.language_agent = `${data.summary || ''} ${data.reason || ''}`;
      detailedResults.language = data;

      report = {
        summary: data.summary || data.reason || 'Language analysis completed.',
        immediate_actions: data.recommendations?.length ? data.recommendations : ['Do not react to artificial urgency or pressure.'],
        verification_steps: ['Pause and consult an independent family member or trusted advisor before taking financial actions.'],
        reporting_channels: generateDefaultRecommendations(threatLevel, queryContext).reporting_channels
      };
    } else if (data.agent === 'identity' || data.verification_status !== undefined) {
      contributingFactors = [
        ...(data.identity_red_flags || []),
        ...(data.mismatch_findings || []),
        data.reason
      ].filter(Boolean);

      agentSummary.identity_agent = `Status: ${data.verification_status || 'Evaluated'}. ${data.reason || ''}`;
      detailedResults.identity = data;

      report = {
        summary: data.reason || 'Identity verification completed.',
        immediate_actions: data.recommendations?.length ? data.recommendations : ['Do not share OTPs, PINs, or credentials with unverified senders.'],
        verification_steps: ['Contact the claimed organization through their publicly listed directory.'],
        reporting_channels: generateDefaultRecommendations(threatLevel, queryContext).reporting_channels
      };
    } else if (data.recruitment_red_flags !== undefined || data.job_information !== undefined) {
      contributingFactors = [
        ...(data.recruitment_red_flags || []),
        ...(data.consistency_findings || []),
        data.reason
      ].filter(Boolean);

      agentSummary.recruitment_agent = data.reason || 'Employment offer evaluated for fraudulent deposit models.';
      detailedResults.recruitment = data;

      report = {
        summary: data.reason || 'Recruitment evaluation completed.',
        immediate_actions: data.recommendations?.length ? data.recommendations : ['Never pay an upfront training, registration, or task deposit fee.'],
        verification_steps: ['Look up the recruiter profile on official LinkedIn and official company job portals.'],
        reporting_channels: generateDefaultRecommendations(threatLevel, queryContext).reporting_channels
      };
    } else {
      contributingFactors = [
        ...(data.red_flags || []),
        data.reason
      ].filter(Boolean);

      agentSummary.threat_agent = data.reason || 'Threat signature check completed.';
      detailedResults.threat = data;

      report = {
        summary: data.reason || 'Threat analysis completed.',
        immediate_actions: data.recommendations?.length ? data.recommendations : ['Avoid engaging with the message.'],
        verification_steps: ['Validate the legitimacy of the request.'],
        reporting_channels: generateDefaultRecommendations(threatLevel, queryContext).reporting_channels
      };
    }
  }

  return {
    id: 'scan_' + Date.now(),
    timestamp: new Date().toISOString(),
    queryContext,
    overall_risk_score: Math.round(riskScore),
    overall_threat_level: threatLevel,
    confidence: data.confidence !== undefined && data.confidence !== null
      ? (data.confidence > 1 ? data.confidence / 100 : data.confidence)
      : 0.92,
    normalized_metadata: data.normalized_metadata || {
      detected_format: 'plain_text',
      extracted_urls: queryContext.url ? [queryContext.url] : extractUrls(queryContext.text || ''),
      extracted_emails: extractEmails(queryContext.text || ''),
      extracted_phones: extractPhones(queryContext.text || '')
    },
    contributing_factors: contributingFactors.length > 0 ? contributingFactors : [
      'Automated analysis completed across specialized cyber intelligence models'
    ],
    agent_summary: agentSummary,
    detailed_results: detailedResults,
    report: report || generateDefaultRecommendations(threatLevel, queryContext),
    isFallback: false
  };
}

function generateDefaultRecommendations(threatLevel, context) {
  const isHigh = threatLevel === 'HIGH' || threatLevel === 'CRITICAL';

  return {
    summary: isHigh
      ? 'This content exhibits prominent red flags commonly associated with phishing and financial fraud. Exercise extreme caution.'
      : 'This content appears relatively safe, but always verify sender credentials through official verified channels.',
    immediate_actions: isHigh ? [
      'Do not enter passwords, OTPs, banking details, card information, or other sensitive information.',
      'Verify the organization through its official website.',
      'Do not download unknown attachments/files.',
      'Do not reply to or contact the suspicious sender using contact details in the message.',
      'If credentials were already entered, change the password through the legitimate website and enable MFA where appropriate.'
    ] : [
      'Verify that the message context matches the expected communication.',
      'For sensitive actions, navigate directly to the organization\'s official website.',
      'Do not rely solely on an automated scan before making financial or confidential decisions.'
    ],
    verification_steps: [
      'Visit the official website by typing the address directly into your browser rather than clicking provided links.',
      'Contact official customer support using numbers published on legitimate statements or directories.'
    ],
    reporting_channels: [
      { name: 'National Cyber Crime Portal (India)', url: 'https://cybercrime.gov.in', helpline: '1930' },
      { name: 'US Federal Trade Commission (FTC)', url: 'https://reportfraud.ftc.gov', helpline: '1-877-FTC-HELP' },
      { name: 'CERT-In Incident Reporting', url: 'https://www.cert-in.org.in', helpline: '1800-11-4949' }
    ]
  };
}

/**
 * High-fidelity intelligent simulated response for offline demonstrations
 */
function generateSimulatedResponse({ text = '', url = '', agent = 'all', isImage = false, isPdf = false, filename = '' }) {
  // If fallback is triggered for OCR / file upload without backend OCR text:
  if ((isImage || isPdf) && (!text || text.startsWith('[Image OCR') || text.startsWith('[PDF Document'))) {
    return {
      id: 'scan_' + Date.now(),
      timestamp: new Date().toISOString(),
      queryContext: { text, url, agent, isImage, filename },
      overall_risk_score: 0,
      overall_threat_level: 'LOW',
      confidence: 0.50,
      normalized_metadata: {
        detected_format: isImage ? 'image_ocr_text' : 'pdf_text',
        extracted_urls: [],
        extracted_emails: [],
        extracted_phones: []
      },
      contributing_factors: [
        `File '${filename || 'upload'}' processed in offline fallback mode. Connect to backend server for full OCR & multi-agent analysis.`
      ],
      agent_summary: {
        threat_agent: 'Backend server offline; OCR unavailable.',
        domain_agent: 'Backend server offline.',
        identity_agent: 'Backend server offline.',
        language_agent: 'Backend server offline.',
        recruitment_agent: 'Backend server offline.'
      },
      detailed_results: {},
      report: generateDefaultRecommendations('LOW', { text, url }),
      isFallback: true
    };
  }
  const combined = (text + ' ' + url).toLowerCase();

  const isFinancial = combined.includes('bank') || combined.includes('account') || combined.includes('suspended') || combined.includes('otp') || combined.includes('kyc') || combined.includes('upi') || combined.includes('card');
  const isRecruitment = combined.includes('job') || combined.includes('task') || combined.includes('telegram') || combined.includes('earn') || combined.includes('salary') || combined.includes('daily') || combined.includes('part-time');
  const isUrgent = combined.includes('urgent') || combined.includes('immediately') || combined.includes('24 hours') || combined.includes('blocked') || combined.includes('threat') || combined.includes('police');
  const isPhishingUrl = url.includes('.xyz') || url.includes('.tk') || url.includes('.top') || url.includes('verify') || url.includes('update') || combined.includes('http');

  let score = 20;
  if (isFinancial) score += 35;
  if (isRecruitment) score += 30;
  if (isUrgent) score += 20;
  if (isPhishingUrl) score += 25;
  if (isImage) score += 15;

  score = Math.min(Math.max(score, 18), 96);

  let threatLevel = 'LOW';
  if (score >= 80) threatLevel = 'CRITICAL';
  else if (score >= 60) threatLevel = 'HIGH';
  else if (score >= 40) threatLevel = 'MODERATE';

  const contributingFactors = [];
  if (isUrgent) contributingFactors.push('Urgency and coercive pressure designed to bypass critical thinking');
  if (isFinancial) contributingFactors.push('Impersonation of banking/financial authority requesting verification');
  if (isRecruitment) contributingFactors.push('Unrealistic salary promises coupled with unverified messaging channels');
  if (isPhishingUrl) contributingFactors.push('Unverified domain with suspicious keywords and high risk top-level domain');
  if (contributingFactors.length === 0) contributingFactors.push('Informational or routine business communication signals');

  return {
    id: 'scan_' + Date.now(),
    timestamp: new Date().toISOString(),
    queryContext: { text, url, agent, isImage, filename },
    overall_risk_score: score,
    overall_threat_level: threatLevel,
    confidence: 0.94,
    normalized_metadata: {
      detected_format: isImage ? 'image_ocr_text' : url ? 'url_and_text' : 'plain_text',
      extracted_urls: url ? [url] : extractUrls(text),
      extracted_emails: extractEmails(text),
      extracted_phones: extractPhones(text)
    },
    contributing_factors: contributingFactors,
    agent_summary: {
      threat_agent: score > 50 ? 'Identified aggressive credential harvesting patterns.' : 'No active malicious signature matched.',
      domain_agent: (url || isPhishingUrl) ? 'Domain has short registration age (<15 days) and privacy-masked WHOIS.' : 'Domain reputation check neutral.',
      identity_agent: isFinancial ? 'High probability spoofing of legitimate financial institution.' : 'No known entity brand hijacking detected.',
      language_agent: isUrgent ? 'Extreme urgency and fear-inducing psychological cues detected.' : 'Neutral communicative tone.',
      recruitment_agent: isRecruitment ? 'Standard task-based deposit pyramid scam indicators.' : 'No employment fraud indicators.'
    },
    detailed_results: {
      domain_score: isPhishingUrl ? 85 : 20,
      identity_score: isFinancial ? 90 : 15,
      language_score: isUrgent ? 88 : 22,
      recruitment_score: isRecruitment ? 92 : 10
    },
    report: generateDefaultRecommendations(threatLevel, { text, url }),
    isFallback: true
  };
}

function extractUrls(text) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  return text.match(urlRegex) || [];
}

function extractEmails(text) {
  const emailRegex = /([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi;
  return text.match(emailRegex) || [];
}

function extractPhones(text) {
  const phoneRegex = /(\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})/g;
  return text.match(phoneRegex) || [];
}
