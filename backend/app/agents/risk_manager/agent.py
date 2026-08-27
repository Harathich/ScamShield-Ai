"""
Risk Manager — the decision layer of ScamShield AI.

This is NOT an LLM-based agent. It is a deterministic aggregation engine
that combines individual agent findings into a final overall risk assessment.

Scoring strategy:
  1. Weighted average of available agent scores (each agent has a configurable weight).
  2. Critical override: if ANY agent returns CRITICAL, the overall is CRITICAL.
  3. Confidence-adjusted: agents with higher confidence contribute more.
"""


# Agent weights — how much each agent's score contributes to the overall.
AGENT_WEIGHTS = {
    "threat":      0.30,
    "language":    0.20,
    "identity":    0.20,
    "domain":      0.20,
    "recruitment": 0.10,
}


def _score_to_level(score: int) -> str:
    """Convert a numeric risk score to a threat level string."""
    if score >= 76:
        return "CRITICAL"
    elif score >= 51:
        return "HIGH"
    elif score >= 26:
        return "MEDIUM"
    else:
        return "LOW"


class RiskManager:
    """
    Combines individual agent results into an overall risk assessment.
    """

    def evaluate(self, agent_results: dict) -> dict:
        """
        Takes a dict of agent results keyed by agent name:
            {
                "threat": { ... },
                "language": { ... },
                "identity": { ... },
                "domain": { ... },
                "recruitment": { ... },
            }

        Returns:
            {
                "overall_risk_score": int,
                "overall_threat_level": str,
                "contributing_factors": [...],
                "agent_scores": {...},
                "confidence": int,
            }
        """

        agent_scores = {}
        weighted_sum = 0.0
        total_weight = 0.0
        confidences = []
        contributing_factors = []
        has_critical = False

        for agent_name, weight in AGENT_WEIGHTS.items():
            result = agent_results.get(agent_name)

            if not result or not isinstance(result, dict):
                continue

            # Skip agents that were skipped or errored
            if result.get("skipped") or result.get("error"):
                agent_scores[agent_name] = {
                    "risk_score": None,
                    "threat_level": None,
                    "skipped": result.get("skipped", False),
                    "error": result.get("error", None),
                }
                continue

            score = result.get("risk_score")
            if score is None:
                continue

            level = result.get("threat_level", result.get("risk_level", ""))
            if isinstance(level, str):
                level = level.upper()

            # Handle confidence whether 0.0-1.0 or 0-100
            raw_conf = result.get("confidence", 70)
            if isinstance(raw_conf, float) and raw_conf <= 1.0:
                confidence = round(raw_conf * 100)
            else:
                confidence = int(raw_conf)

            agent_scores[agent_name] = {
                "risk_score": score,
                "threat_level": level,
                "skipped": False,
                "error": None,
            }

            # Confidence-adjusted weighting
            adjusted_weight = weight * (confidence / 100.0)
            weighted_sum += score * adjusted_weight
            total_weight += adjusted_weight
            confidences.append(confidence)

            # Check for critical override
            if level == "CRITICAL" or score >= 76:
                has_critical = True

            # Collect contributing factors from high-risk agents
            if score >= 51:
                factor = f"{agent_name.title()} Agent: "
                if agent_name == "threat":
                    factor += result.get("scam_type", "Threat detected")
                elif agent_name == "language":
                    techniques = result.get("manipulation_techniques", [])
                    factor += ", ".join(techniques[:3]) if techniques else "Manipulation detected"
                elif agent_name == "identity":
                    factor += result.get("verification_status", "Identity concern")
                elif agent_name == "domain":
                    factor += f"Domain risk score {score}"
                elif agent_name == "recruitment":
                    red_flags = result.get("recruitment_red_flags", [])
                    factor += ", ".join(red_flags[:2]) if red_flags else result.get("reason", "Recruitment anomalies")
                contributing_factors.append(factor)

        # Calculate overall score
        if total_weight > 0:
            overall_score = round(weighted_sum / total_weight)
        else:
            overall_score = 0

        # Critical override: if any agent flagged CRITICAL, bump overall to at least 76
        if has_critical and overall_score < 76:
            overall_score = max(overall_score, 76)

        # Clamp to 0-100
        overall_score = max(0, min(100, overall_score))

        overall_level = _score_to_level(overall_score)

        # Average confidence across contributing agents
        overall_confidence = round(sum(confidences) / len(confidences)) if confidences else 0

        return {
            "overall_risk_score": overall_score,
            "overall_threat_level": overall_level,
            "contributing_factors": contributing_factors,
            "agent_scores": agent_scores,
            "confidence": overall_confidence,
        }
