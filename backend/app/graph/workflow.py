"""
LangGraph workflow definition for the ScamShield multi-agent pipeline.

Graph structure:
    START → preprocess → threat → language → identity → domain
         → recruitment → risk_manager → report → END
"""

from langgraph.graph import StateGraph, END

from app.graph.state import ScamShieldState
from app.graph.nodes import (
    preprocess_node,
    threat_node,
    language_node,
    identity_node,
    domain_node,
    recruitment_node,
    risk_manager_node,
    report_node,
)


def build_workflow():
    """Build and compile the ScamShield analysis graph."""

    graph = StateGraph(ScamShieldState)

    # Register nodes
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("threat", threat_node)
    graph.add_node("language", language_node)
    graph.add_node("identity", identity_node)
    graph.add_node("domain", domain_node)
    graph.add_node("recruitment", recruitment_node)
    graph.add_node("risk_manager", risk_manager_node)
    graph.add_node("report", report_node)

    # Define edges (sequential pipeline)
    graph.set_entry_point("preprocess")
    graph.add_edge("preprocess", "threat")
    graph.add_edge("threat", "language")
    graph.add_edge("language", "identity")
    graph.add_edge("identity", "domain")
    graph.add_edge("domain", "recruitment")
    graph.add_edge("recruitment", "risk_manager")
    graph.add_edge("risk_manager", "report")
    graph.add_edge("report", END)

    return graph.compile()


# Pre-compiled workflow instance for reuse across requests
scamshield_workflow = build_workflow()
