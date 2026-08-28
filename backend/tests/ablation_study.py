"""
ScamShield-AI Ablation Study Evaluation Suite.

Systematically measures the performance contribution of each agent and mechanism:
1. Full System (All 5 Agents + Critical Override)
2. Without Domain Agent (No WHOIS / VirusTotal)
3. Without Language Agent (No Psychological NLP)
4. Without Identity Agent (No Brand Verification)
5. Without Critical Override (Pure Average Scoring)

Outputs a clean markdown comparison table for project reports and research papers.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Ensure backend directory is in sys.path regardless of where the script is executed
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.graph.state import ScamShieldState
from app.graph.nodes import (
    preprocess_node, threat_node, language_node,
    identity_node, domain_node, recruitment_node,
    risk_manager_node, report_node
)
from app.agents.risk_manager.agent import RiskManager

# High-Signal Benchmark Corpus
ABLATION_SAMPLES = [
    {"id": "PHISH-01", "text": "URGENT: State Bank of India Alert. Debit card blocked. Verify at https://sbi-card-verify.xyz/login to prevent suspension.", "expected": "SCAM"},
    {"id": "PHISH-02", "text": "Your Netflix membership is on hold due to payment failure. Update credentials at http://netflix-billing-update-security.com", "expected": "SCAM"},
    {"id": "SMISH-01", "text": "Congratulations! You won ₹50,00,000 in Amazon Lucky Draw. Claim in 15 mins: http://win-amazon-cash-now.top/claim", "expected": "SCAM"},
    {"id": "SMISH-02", "text": "MICROSOFT ALERT: Trojan detected on Windows. Financial data leaking. Call Helpdesk immediately at +1-800-555-0199.", "expected": "SCAM"},
    {"id": "JOB-01", "text": "Selected for Data Entry at GlobalTech ($120k/yr, WFH). Transfer refundable registration fee $150 via Zelle.", "expected": "SCAM"},
    {"id": "LEGIT-01", "text": "Your Amazon order #408-1293847 has shipped. Track package at https://www.amazon.com/orders. Thank you.", "expected": "LEGIT"},
    {"id": "LEGIT-02", "text": "Hi Alex, thank you for applying to Stripe. We invite you for a 45-min interview at https://stripe.com/jobs", "expected": "LEGIT"},
    {"id": "LEGIT-03", "text": "GitHub password reset requested. Click here: https://github.com/password_reset?token=ab872f91a", "expected": "LEGIT"},
    {"id": "LEGIT-04", "text": "Hey Rahul, are you free for lunch tomorrow around 1 PM at the cafeteria?", "expected": "LEGIT"},
    {"id": "LEGIT-05", "text": "Mock Review for Capstone Project is scheduled on Saturday. Attendance is mandatory. Scope, VIT-AP University.", "expected": "LEGIT"},
]


def run_pipeline_with_ablation(text: str, ablate: str = "none") -> Dict[str, Any]:
    """Runs pipeline with specific components disabled for ablation study."""
    state: ScamShieldState = {"input_text": text}

    # Step 1: Preprocess
    p_res = preprocess_node(state)
    state.update(p_res)

    # Step 2: Agents (conditionally ablated)
    state.update(threat_node(state))

    if ablate == "no_language":
        state["language_result"] = {"agent": "language", "skipped": True, "risk_score": None}
    else:
        state.update(language_node(state))

    if ablate == "no_identity":
        state["identity_result"] = {"agent": "identity", "skipped": True, "risk_score": None}
    else:
        state.update(identity_node(state))

    if ablate == "no_domain":
        state["domain_result"] = {"agent": "domain", "skipped": True, "risk_score": None}
    else:
        state.update(domain_node(state))

    state.update(recruitment_node(state))

    # Step 3: Risk Manager
    agent_results = {
        "threat": state.get("threat_result"),
        "language": state.get("language_result"),
        "identity": state.get("identity_result"),
        "domain": state.get("domain_result"),
        "recruitment": state.get("recruitment_result"),
    }

    risk_mgr = RiskManager()
    rm_res = risk_mgr.evaluate(agent_results)

    # If ablating Critical Override, compute simple linear average
    if ablate == "no_override":
        valid_scores = [v["risk_score"] for v in rm_res.get("agent_scores", {}).values() if v.get("risk_score") is not None]
        avg_score = round(sum(valid_scores) / len(valid_scores)) if valid_scores else 0
        rm_res["overall_risk_score"] = avg_score
        rm_res["overall_threat_level"] = "CRITICAL" if avg_score >= 76 else ("HIGH" if avg_score >= 51 else ("MEDIUM" if avg_score >= 26 else "LOW"))

    return rm_res


def evaluate_ablation():
    configs = [
        ("Full Multi-Agent System (All Agents)", "none"),
        ("Without Domain Agent (No WHOIS/VT)", "no_domain"),
        ("Without Language Agent (No Urgency NLP)", "no_language"),
        ("Without Identity Agent (No Brand Spoof)", "no_identity"),
        ("Without Critical Override (Pure Average)", "no_override"),
    ]

    print("=" * 75)
    print("  ScamShield-AI Ablation Study: Component Impact Analysis")
    print("=" * 75)

    summary_rows = []

    for name, ablate_key in configs:
        tp = fp = tn = fn = 0
        latencies = []

        for item in ABLATION_SAMPLES:
            start = time.time()
            res = run_pipeline_with_ablation(item["text"], ablate=ablate_key)
            duration = time.time() - start
            latencies.append(duration)

            score = res.get("overall_risk_score", 0)
            level = res.get("overall_threat_level", "LOW")
            expected = item["expected"]
            predicted = "SCAM" if (score >= 35 or level in ("HIGH", "CRITICAL", "MEDIUM")) else "LEGIT"

            if predicted == expected:
                if expected == "SCAM": tp += 1
                else: tn += 1
            else:
                if expected == "SCAM": fn += 1
                else: fp += 1

        total = len(ABLATION_SAMPLES)
        acc = round((tp + tn) / total * 100, 1)
        prec = round(tp / (tp + fp) * 100, 1) if (tp + fp) > 0 else 0.0
        rec = round(tp / (tp + fn) * 100, 1) if (tp + fn) > 0 else 0.0
        f1 = round(2 * (prec * rec) / (prec + rec), 1) if (prec + rec) > 0 else 0.0
        avg_lat = round(sum(latencies) / len(latencies), 2)

        summary_rows.append({
            "configuration": name,
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "avg_latency": avg_lat
        })

        print(f"  {name:<42} | Acc: {acc:>5}% | F1: {f1:>5}% | Prec: {prec:>5}%")

    print("=" * 75)
    print("\n### Formatted Markdown Table for Your Research Paper / Report:\n")
    print("| Configuration | Accuracy (%) | Precision (%) | Recall (%) | F1-Score (%) | Avg Latency (s) |")
    print("|---|:---:|:---:|:---:|:---:|:---:|")
    for r in summary_rows:
        print(f"| **{r['configuration']}** | {r['accuracy']}% | {r['precision']}% | {r['recall']}% | {r['f1_score']}% | {r['avg_latency']}s |")

    # Save to JSON in tests directory and working directory
    out_path = Path(__file__).resolve().parent / "ablation_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary_rows, f, indent=2)

    try:
        with open("ablation_results.json", "w", encoding="utf-8") as f:
            json.dump(summary_rows, f, indent=2)
    except Exception:
        pass


if __name__ == "__main__":
    evaluate_ablation()
