import time, sys
sys.path.insert(0, '.')

from app.graph.nodes import (
    preprocess_node, threat_node, language_node,
    identity_node, domain_node, recruitment_node
)
from app.agents.risk_manager.agent import RiskManager

text = "URGENT: State Bank of India Alert. Debit card blocked. Verify at https://sbi-card-verify.xyz/login to prevent suspension."
state = {"input_text": text}

t0 = time.time()
state.update(preprocess_node(state))
t1 = time.time()
print(f"Preprocess: {t1-t0:.2f}s")

state.update(threat_node(state))
t2 = time.time()
print(f"Threat: {t2-t1:.2f}s  score={state.get('threat_result',{}).get('risk_score')}")

state.update(language_node(state))
t3 = time.time()
print(f"Language: {t3-t2:.2f}s  score={state.get('language_result',{}).get('risk_score')}")

state.update(identity_node(state))
t4 = time.time()
print(f"Identity: {t4-t3:.2f}s  score={state.get('identity_result',{}).get('risk_score')}")

state.update(domain_node(state))
t5 = time.time()
print(f"Domain: {t5-t4:.2f}s  score={state.get('domain_result',{}).get('risk_score')}")

state.update(recruitment_node(state))
t6 = time.time()
print(f"Recruitment: {t6-t5:.2f}s  score={state.get('recruitment_result',{}).get('risk_score')}")

agent_results = {
    "threat": state.get("threat_result"),
    "language": state.get("language_result"),
    "identity": state.get("identity_result"),
    "domain": state.get("domain_result"),
    "recruitment": state.get("recruitment_result"),
}
risk_mgr = RiskManager()
rm_res = risk_mgr.evaluate(agent_results)
total = time.time() - t0
print(f"\nTotal pipeline: {total:.1f}s")
print(f"Overall Score: {rm_res.get('overall_risk_score')}")
print(f"Overall Level: {rm_res.get('overall_threat_level')}")
