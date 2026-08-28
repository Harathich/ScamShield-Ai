"""Debug: run a single ablation sample with per-step timing to find the hang."""
import time, sys
sys.path.insert(0, '.')

from app.graph.nodes import (
    preprocess_node, threat_node, language_node,
    identity_node, domain_node, recruitment_node
)
from app.agents.risk_manager.agent import RiskManager

# First scam sample from the ablation corpus
text = "URGENT: State Bank of India Alert. Debit card blocked. Verify at https://sbi-card-verify.xyz/login to prevent suspension."

print(f"Testing: {text[:80]}...", flush=True)
state = {"input_text": text}

steps = [
    ("preprocess", preprocess_node),
    ("threat", threat_node),
    ("language", language_node),
    ("identity", identity_node),
    ("domain", domain_node),
    ("recruitment", recruitment_node),
]

for name, fn in steps:
    t0 = time.time()
    print(f"  Starting {name}...", flush=True)
    try:
        state.update(fn(state))
    except Exception as e:
        print(f"  ERROR in {name}: {e}", flush=True)
    elapsed = time.time() - t0
    print(f"  {name}: {elapsed:.1f}s", flush=True)

print("\nNow testing RiskManager...", flush=True)
t0 = time.time()
agent_results = {
    "threat": state.get("threat_result"),
    "language": state.get("language_result"),
    "identity": state.get("identity_result"),
    "domain": state.get("domain_result"),
    "recruitment": state.get("recruitment_result"),
}
rm = RiskManager()
result = rm.evaluate(agent_results)
print(f"  RiskManager: {time.time()-t0:.1f}s", flush=True)
print(f"  Score: {result.get('overall_risk_score')}, Level: {result.get('overall_threat_level')}", flush=True)
print("\nDONE", flush=True)
