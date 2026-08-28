# ScamShield-AI: Empirical Benchmark Framework & Methodology

## 1. Modality & Scope
ScamShield-AI evaluates digital communications across multiple threat vectors:
* **Lexical & Network URL Analysis**: Suspicious TLDs, domain registration age, SSL certificate authenticity, and blacklisting telemetry.
* **SMS & Smishing Communications**: Mobile-targeted urgent messages, prize lures, and utility disconnection extortion.
* **Fraudulent Email & Phishing**: Banking KYC notices, fake credential logins, and cross-brand spoofs.
* **Recruitment Fraud**: Advance-fee recruitment scams, unrealistic compensation vs experience anomalies, and unverified communication channels.

---

## 2. Standardized Benchmark Corpora

The evaluation framework sources samples from recognized cybersecurity and machine learning corpora:

| Threat Modality | Primary Dataset Corpora | Characteristics |
|---|---|---|
| **Phishing URLs** | **PhishTank / OpenPhish / ISCXURL2016** | Active real-world phishing URLs, typo-squatted brand lookalikes. |
| **Smishing / SMS Scams** | **UCI SMS Spam Corpus / Smishing Dataset** | Real-world fraudulent mobile SMS with financial and coercion lures. |
| **Email Fraud / Extortion** | **SpamAssassin / Enron Email Corpus** | Classic social engineering, fake security warnings, and credential harvesting. |
| **Recruitment Scams** | **Empirical Recruitment Scam Corpus** | Upfront deposit requests, Telegram/Zelle payment demands, and fake remote offers. |
| **Legitimate Controls** | **Institutional & Transactional Benchmarks** | Legitimate e-commerce shipping notices, corporate job invites, password resets. |

---

## 3. Mathematical Evaluation Metrics

For research paper reporting, metrics are defined as follows:

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

$$\text{Precision} = \frac{TP}{TP + FP}$$

$$\text{Recall (Sensitivity)} = \frac{TP}{TP + FN}$$

$$\text{F1-Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

$$\text{False Positive Rate (FPR)} = \frac{FP}{FP + TN}$$

---

## 4. Running the Benchmark Suite

With the backend running (`uvicorn app.main:app --port 8000`), execute:

```bash
python backend/tests/benchmark_eval.py
```

Results will output directly to the terminal and save a machine-readable report to `backend/tests/benchmark_results.json`.
