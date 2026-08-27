"""
LangGraph workflow definition for the ScamShield multi-agent pipeline.

Graph structure:
    START → threat → language → identity → domain → aggregate → END

Each agent runs sequentially. The domain node auto-skips if no URL
is found. The aggregate node produces the overall risk assessment.

When the Risk Manager agent is built, it will replace the aggregate
node's placeholder scoring logic.
"""

from langgraph.graph import StateGraph, END

from app.graph.state import ScamShieldState
from app.graph.nodes import (
    threat_node,
    language_node,
    identity_node,
    domain_node,
    aggregate_node,
)


def build_workflow():
    """Build and compile the ScamShield analysis graph."""

    graph = StateGraph(ScamShieldState)

    # Register nodes
    graph.add_node("threat", threat_node)
    graph.add_node("language", language_node)
    graph.add_node("identity", identity_node)
    graph.add_node("domain", domain_node)
    graph.add_node("aggregate", aggregate_node)

    # Define edges (sequential pipeline)
    graph.set_entry_point("threat")
    graph.add_edge("threat", "language")
    graph.add_edge("language", "identity")
    graph.add_edge("identity", "domain")
    graph.add_edge("domain", "aggregate")
    graph.add_edge("aggregate", END)

    return graph.compile()


# Pre-compiled workflow instance for reuse across requests
scamshield_workflow = build_workflow()
