"""
Deterministic Report Generator for ScamShield AI.

Synthesizes structured analytical results from all specialized agents
and the Risk Manager into a clear, user-friendly security report.

Runs 100% in Python with ZERO LLM API calls, saving tokens and executing in < 1ms.
"""

from typing import Dict, Any, List


class ReportGenerator:
    """
    Combines multi-agent findings into a plain-language user security report.
    """

    def generate(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize analysis findings into a structured report.
        """
        risk_mgr = analysis_data.get("risk_manager_result") or {}
        overall_score = risk_mgr.get("overall_risk_score", 0)
        overall_level = risk_mgr.get("overall_threat_level", "LOW")
        contributing_factors = risk_mgr.get("contributing_factors", [])

        threat = analysis_data.get("threat_result") or {}
        language = analysis_data.get("language_result") or {}
        identity = analysis_data.get("identity_result") or {}
        domain = analysis_data.get("domain_result") or {}
        recruitment = analysis_data.get("recruitment_result") or {}

        # 1. Determine Title & Verdict
        title, verdict = self._build_title_and_verdict(
            overall_score, overall_level, threat, language, identity, domain, recruitment
        )

        # 2. Extract Why Risky bullets
        why_risky = self._extract_why_risky(
            threat, language, identity, domain, recruitment, contributing_factors
        )

        # 3. Build Agent Highlights
        agent_highlights = self._build_agent_highlights(
            threat, language, identity, domain, recruitment
        )

        # 4. Synthesize Recommendations
        recommendations = self._synthesize_recommendations(
            overall_level, threat, language, identity, domain, recruitment
        )

        # 5. Extract Safe Indicators
        safe_indicators = self._extract_safe_indicators(
            overall_score, threat, language, identity, domain, recruitment
        )

        # 6. Build Narrative Summary
        summary = self._build_summary(
            overall_level, overall_score, verdict, why_risky, safe_indicators
        )

        return {
            "agent": "report_generator",
            "title": title,
            "overall_risk_score": overall_score,
            "overall_threat_level": overall_level,
            "verdict": verdict,
            "summary": summary,
            "why_risky": why_risky,
            "agent_highlights": agent_highlights,
            "recommendations": recommendations,
            "immediate_actions": recommendations,
            "safe_indicators": safe_indicators,
        }

    def _build_title_and_verdict(self, score, level, threat, language, identity, domain, recruitment):
        scam_type = threat.get("scam_type") or ""
        rec_legit = recruitment.get("recruitment_legitimacy") or ""
        id_status = identity.get("verification_status") or ""

        if level == "CRITICAL":
            if rec_legit == "SCAM":
                return "High-Risk Recruitment Scam Warning", "This message is a fraudulent job or recruitment scam demanding money or sensitive details."
            if id_status == "IMPERSONATION":
                return "Critical Brand Impersonation Phishing", "This message is an active impersonation attack mimicking an official organization."
            if "Phishing" in scam_type or domain.get("brand_impersonation"):
                return "Critical Phishing Threat Detected", "This communication is a dangerous phishing attempt designed to steal credentials or financial assets."
            return "Critical Security Threat Detected", "This message exhibits severe characteristics of digital fraud or cyber attack."

        elif level == "HIGH":
            if rec_legit == "SCAM" or recruitment.get("risk_score", 0) >= 50:
                return "Suspicious Job Offer Warning", "This employment opportunity displays multiple red flags typical of recruitment fraud."
            if "Phishing" in scam_type:
                return "Phishing Attempt Detected", "This message is very likely a phishing communication seeking unauthorized action."
            if language.get("risk_score", 0) >= 60:
                return "Social Engineering & Manipulation Warning", "This message employs aggressive psychological manipulation to pressure you into acting."
            return "High-Risk Communication Detected", "Multiple security agents identified significant risk indicators in this communication."

        elif level == "MEDIUM":
            return "Suspicious Communication — Caution Advised", "This message contains anomalies or unverified elements that require caution before interacting."

        else:  # LOW
            if domain.get("ssl_status") == "Valid" and not domain.get("brand_impersonation"):
                return "Low-Risk Verified Communication", "This communication appears legitimate with no significant scam or phishing indicators."
            return "Low-Risk Communication", "No significant technical threats or manipulation patterns were identified in this message."

    def _extract_why_risky(self, threat, language, identity, domain, recruitment, contributing_factors) -> List[str]:
        reasons = []

        # From Threat Agent
        for rf in threat.get("red_flags", [])[:2]:
            reasons.append(f"Threat Flag: {rf}.")

        # From Recruitment Agent
        for rf in recruitment.get("recruitment_red_flags", [])[:2]:
            reasons.append(f"Recruitment Risk: {rf}.")
        for cf in recruitment.get("consistency_findings", [])[:1]:
            if isinstance(cf, dict) and "finding" in cf:
                reasons.append(f"Job Inconsistency: {cf['finding']}.")

        # From Domain Agent
        if domain.get("brand_impersonation"):
            reasons.append("The referenced domain appears to be spoofing a recognized brand name.")
        if domain.get("ssl_status") == "Invalid":
            reasons.append("The website link lacks a valid SSL security certificate.")
        for trf in domain.get("technical_red_flags", [])[:2]:
            reasons.append(f"Domain Risk: {trf}.")

        # From Identity Agent
        for mf in identity.get("mismatch_findings", [])[:2]:
            if isinstance(mf, dict) and "finding" in mf:
                reasons.append(f"Identity Mismatch: {mf['finding']}.")
        for irf in identity.get("identity_red_flags", [])[:1]:
            reasons.append(f"Identity Risk: {irf}.")

        # From Language Agent
        techniques = language.get("manipulation_techniques", [])
        if techniques:
            reasons.append(f"Psychological Tactics: Employs {', '.join(techniques[:3])} to induce rushed compliance.")

        # Fallback to contributing factors if list is empty
        if not reasons:
            for factor in contributing_factors[:3]:
                reasons.append(factor)

        return reasons[:5]

    def _build_agent_highlights(self, threat, language, identity, domain, recruitment) -> List[str]:
        highlights = []

        if not threat.get("skipped") and not threat.get("error"):
            scam = threat.get("scam_type", "General")
            score = threat.get("risk_score", 0)
            highlights.append(f"Threat Agent: Assigned score {score}/100 ({threat.get('threat_level', 'LOW')}) - {scam}.")

        if not language.get("skipped") and not language.get("error"):
            techs = language.get("manipulation_techniques", [])
            tech_str = f"detected {', '.join(techs[:2])}" if techs else "no manipulation"
            highlights.append(f"Language Agent: {tech_str.capitalize()} ({language.get('threat_level', 'LOW')}).")

        if not identity.get("skipped") and not identity.get("error"):
            status = identity.get("verification_status", "INCONCLUSIVE")
            highlights.append(f"Identity Agent: Verification status is {status}.")

        if not domain.get("skipped") and not domain.get("error"):
            dom_name = domain.get("domain", "website")
            ssl = domain.get("ssl_status", "Unknown")
            highlights.append(f"Domain Agent: Inspected '{dom_name}' (SSL: {ssl}, Risk: {domain.get('risk_level', 'LOW')}).")

        if not recruitment.get("skipped") and not recruitment.get("error"):
            legit = recruitment.get("recruitment_legitimacy", "INCONCLUSIVE")
            if legit != "INCONCLUSIVE" or recruitment.get("risk_score", 0) > 20:
                highlights.append(f"Recruitment Agent: Classified opportunity as {legit}.")

        return highlights

    def _synthesize_recommendations(self, level, threat, language, identity, domain, recruitment) -> List[str]:
        recs = []

        # Collect direct agent recommendations
        for ag in [threat, recruitment, identity, language]:
            for r in ag.get("recommendations", []):
                if r and r not in recs and len(recs) < 4:
                    recs.append(r)

        # Domain agent uses singular 'recommendation'
        dom_rec = domain.get("recommendation")
        if dom_rec and dom_rec not in recs and len(recs) < 5:
            recs.append(dom_rec)

        # Baseline safety recommendations
        if level in ("CRITICAL", "HIGH"):
            if "Do not click any embedded links or download attachments." not in recs:
                recs.insert(0, "Do not click any embedded links or download attachments.")
            if "Never share passwords, OTPs, or transfer registration/processing fees." not in recs:
                recs.append("Never share passwords, OTPs, or transfer registration/processing fees.")
            if "Verify the sender through trusted, official telephone or website channels." not in recs:
                recs.append("Verify the sender through trusted, official telephone or website channels.")
        else:
            if not recs:
                recs = [
                    "Exercise standard digital hygiene before clicking unexpected links.",
                    "Verify the sender email domain matches official public channels.",
                    "Report any unexpected requests for personal or financial credentials."
                ]

        return recs[:5]

    def _extract_safe_indicators(self, overall_score, threat, language, identity, domain, recruitment) -> List[str]:
        safe = []

        if not domain.get("skipped") and domain.get("ssl_status") == "Valid":
            safe.append(f"The link points to a domain ({domain.get('domain')}) with a valid SSL certificate.")
        if not domain.get("skipped") and not domain.get("brand_impersonation"):
            safe.append("No domain brand impersonation was detected.")

        if not language.get("skipped") and not language.get("manipulation_techniques"):
            safe.append("No psychological pressure, fear, or urgency manipulation detected.")

        if identity.get("verification_status") == "VERIFIED":
            safe.append("Sender identity matches verified official organizational records.")

        if overall_score < 25 and not safe:
            safe.append("No malicious URLs, credential harvesting, or payment requests were found.")

        return safe

    def _build_summary(self, level, score, verdict, why_risky, safe_indicators) -> str:
        if level in ("CRITICAL", "HIGH"):
            risks_summary = " ".join(why_risky[:2]) if why_risky else "Multiple high-risk markers were detected."
            return f"{verdict} The automated security pipeline assigned an overall risk score of {score}/100 ({level}). {risks_summary} Immediate caution is advised."
        elif level == "MEDIUM":
            return f"{verdict} The analysis evaluated an overall risk score of {score}/100. While no critical exploit was confirmed, several suspicious characteristics or missing identity proofs warrant verification before taking action."
        else:
            safes_summary = " ".join(safe_indicators[:2]) if safe_indicators else "Standard communication patterns observed."
            return f"{verdict} The overall risk score is {score}/100 ({level}). {safes_summary}"
