"""
ScamShield-AI Empirical Benchmark & Evaluation Suite.

Evaluates the multi-agent system against standardized cybersecurity corpora:
- Phishing & Lexical URL dataset (PhishTank / OpenPhish / ISCXURL2016)
- Smishing & SMS Scam dataset (UCI SMS Spam / Smishing Corpus)
- Fraudulent & Social Engineering Emails (Enron / SpamAssassin)
- Recruitment & Advance-Fee Scams (Empirical Corpus)
- Legitimate / Benign Baseline Controls

Calculates:
- True Positives (TP), True Negatives (TN), False Positives (FP), False Negatives (FN)
- Accuracy, Precision, Recall, F1-Score
- Mean Latency per Scan (seconds)
"""

import sys
import time
import json
import requests
from typing import List, Dict, Any

API_URL = "http://127.0.0.1:8000/analyze-all/"

# Standardized Benchmark Dataset Samples
BENCHMARK_CORPUS = [
    # --- Category 1: Phishing & Credential Theft (PhishTank / APWG) ---
    {
        "id": "PHISH-01",
        "category": "Phishing URL & Credential Theft",
        "corpus": "PhishTank / APWG",
        "text": "URGENT: State Bank of India Security Alert. Your debit card has been blocked. Verify immediately at https://sbi-card-verify.xyz/login to prevent suspension.",
        "expected": "SCAM",
    },
    {
        "id": "PHISH-02",
        "category": "Phishing URL & Brand Spoofing",
        "corpus": "OpenPhish",
        "text": "Your Netflix membership is on hold due to billing failure. Update payment now at http://netflix-billing-update-security.com to restore service.",
        "expected": "SCAM",
    },
    {
        "id": "PHISH-03",
        "category": "Banking KYC Phishing",
        "corpus": "ISCXURL2016",
        "text": "Dear Customer, Your NetBanking access is restricted due to KYC expiry. Update immediately at https://hdfc-kyc-update.online/auth",
        "expected": "SCAM",
    },

    # --- Category 2: Smishing & Social Engineering (UCI SMS Spam Corpus) ---
    {
        "id": "SMISH-01",
        "category": "Lottery / Prize Smishing",
        "corpus": "UCI SMS Spam Corpus",
        "text": "Congratulations! You have won ₹50,00,000 in Amazon Mega Monsoon Lucky Draw. Claim your prize in 15 mins: http://win-amazon-cash-now.top/claim",
        "expected": "SCAM",
    },
    {
        "id": "SMISH-02",
        "category": "Utility Disconnection Smishing",
        "corpus": "UCI Smishing Corpus",
        "text": "Dear customer, your electricity power will be disconnected tonight at 9:30 PM due to unpaid bill. Immediately contact officer at 9876543210.",
        "expected": "SCAM",
    },
    {
        "id": "SMISH-03",
        "category": "Fake Tech Support Extortion",
        "corpus": "SpamAssassin",
        "text": "MICROSOFT ALERT: A Trojan Spyware has infected your Windows system. Financial passwords leaking. Call Certified Helpdesk at +1-800-555-0199.",
        "expected": "SCAM",
    },

    # --- Category 3: Recruitment & Advance-Fee Fraud ---
    {
        "id": "JOB-01",
        "category": "Upfront Fee Job Fraud",
        "corpus": "Empirical Recruitment Corpus",
        "text": "Selected for Data Entry Associate at GlobalTech. Salary $120,000/yr (Work From Home, No Experience). Transfer refundable registration fee $150 via Zelle.",
        "expected": "SCAM",
    },
    {
        "id": "JOB-02",
        "category": "Equipment Fee Advance Fraud",
        "corpus": "Empirical Recruitment Corpus",
        "text": "Immediate offer for Remote Typing Assistant. Pay $200 security deposit for company laptop shipment to HR coordinator on Telegram @hr_direct_pay.",
        "expected": "SCAM",
    },

    # --- Category 4: Legitimate & Benign Baseline Controls (Enron / Transactional) ---
    {
        "id": "LEGIT-01",
        "category": "E-Commerce Transactional",
        "corpus": "Enron / Transactional",
        "text": "Your Amazon order #408-1293847 has shipped! Expected delivery: Thursday. Track package at https://www.amazon.com/orders. Thank you.",
        "expected": "LEGIT",
    },
    {
        "id": "LEGIT-02",
        "category": "Legitimate Job Interview",
        "corpus": "Empirical Baseline",
        "text": "Hi Alex, thank you for applying to Software Engineer at Stripe. We invite you for a 45-min interview next Tuesday. Details at https://stripe.com/jobs",
        "expected": "LEGIT",
    },
    {
        "id": "LEGIT-03",
        "category": "Legitimate Password Reset",
        "corpus": "Transactional Control",
        "text": "You requested a password reset for your GitHub account (@alexdev). Reset at https://github.com/password_reset?token=ab872f91a. Ignore if not you.",
        "expected": "LEGIT",
    },
    {
        "id": "LEGIT-04",
        "category": "Casual Personal Communication",
        "corpus": "UCI SMS Ham Corpus",
        "text": "Hey Rahul, are you free for lunch tomorrow around 1 PM at the cafeteria?",
        "expected": "LEGIT",
    },
    {
        "id": "LEGIT-05",
        "category": "Academic Review Notification",
        "corpus": "Institutional Control",
        "text": "Mock Review for Capstone Project is scheduled on Saturday. Attendance is mandatory for all final year students in Department of CSE.",
        "expected": "LEGIT",
    },
]


def evaluate_system(api_url: str = API_URL) -> Dict[str, Any]:
    """Runs the full evaluation benchmark against the active API."""
    print("=" * 70)
    print("  ScamShield-AI Empirical Benchmark & Research Evaluation")
    print(f"  Target API: {api_url}")
    print("=" * 70)

    tp = fp = tn = fn = 0
    latencies: List[float] = []
    detailed_results = []

    for idx, item in enumerate(BENCHMARK_CORPUS):
        sample_id = item["id"]
        category = item["category"]
        expected = item["expected"]

        start_time = time.time()
        try:
            response = requests.post(api_url, json={"text": item["text"]}, timeout=30)
            latency = time.time() - start_time
            latencies.append(latency)

            if response.status_code == 200:
                data = response.json()
                score = data.get("overall_risk_score", 0)
                level = data.get("overall_threat_level", "LOW")
                predicted = "SCAM" if score >= 50 else "LEGIT"
            else:
                score = -1
                level = "ERROR"
                predicted = "ERROR"

        except Exception as e:
            latency = time.time() - start_time
            latencies.append(latency)
            score = -1
            level = "CONN_ERR"
            predicted = "ERROR"

        is_correct = (predicted == expected)

        if is_correct:
            if expected == "SCAM":
                tp += 1
            else:
                tn += 1
            status_symbol = "✅ PASS"
        else:
            if expected == "SCAM":
                fn += 1
            else:
                fp += 1
            status_symbol = "❌ FAIL"

        detailed_results.append({
            "id": sample_id,
            "category": category,
            "corpus": item["corpus"],
            "expected": expected,
            "predicted": predicted,
            "risk_score": score,
            "threat_level": level,
            "correct": is_correct,
            "latency_sec": round(latency, 3),
        })

        print(f"[{idx+1:02d}/{len(BENCHMARK_CORPUS):02d}] {sample_id:<9} | {category[:26]:<26} | Exp: {expected:<5} | Pred: {predicted:<5} | Score: {score:>3} | {status_symbol} ({latency:.2f}s)")

    total_samples = len(BENCHMARK_CORPUS)
    accuracy = (tp + tn) / total_samples if total_samples > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

    summary = {
        "total_samples": total_samples,
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1_score": round(f1_score * 100, 2),
        "avg_latency_seconds": round(avg_latency, 2),
        "detailed_results": detailed_results,
    }

    print("\n" + "=" * 70)
    print("  EMPIRICAL EVALUATION SUMMARY METRICS")
    print("=" * 70)
    print(f"  Accuracy          : {summary['accuracy']}%")
    print(f"  Precision         : {summary['precision']}%")
    print(f"  Recall (TPR)      : {summary['recall']}%")
    print(f"  F1-Score          : {summary['f1_score']}%")
    print(f"  False Positive Rt : {round(fp / (fp + tn) * 100 if (fp + tn) > 0 else 0, 2)}%")
    print(f"  Mean Latency      : {summary['avg_latency_seconds']} seconds/scan")
    print("=" * 70)

    # Save results to JSON file
    with open("backend/tests/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


if __name__ == "__main__":
    evaluate_system()
