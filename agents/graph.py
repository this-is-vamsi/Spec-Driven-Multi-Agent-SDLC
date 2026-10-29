"""
Multi-Agent LangGraph Pipeline
================================

Hub-and-Spoke Architecture:

                 ┌──────────────┐
                 │   Planning   │  (Scrum Master)
                 └──────┬───────┘
                        ▼
              ┌──────────────────┐
         ┌───►│  ORCHESTRATOR    │◄───┐
         │    │ (Scrum Master)   │    │
         │    └──┬───┬───┬───┬──┘    │
         │       │   │   │   │       │
         │       ▼   ▼   ▼   ▼       │
         │    DEV TEST DEV  END      │
         │     │   │    OPS          │
         │     │   │     │           │
         └─────┘   └─────┴──────────┘

Every agent reports back to the orchestrator.
The orchestrator has access to all agents and decides
who runs next based on the full state.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.state import AgentState
from agents.scrum_master import planning_node, orchestrator_node
from agents.developer import development_node
from agents.tester import testing_node
from agents.devops import devops_node


def _route_from_orchestrator(state: AgentState) -> str:
    """Conditional edge: read the orchestrator's decision from state."""
    next_agent = state.get("next_agent", "end")
    if next_agent in ("developer", "tester", "devops"):
        return next_agent
    return "end"


def build_pipeline():
    """Construct and compile the multi-agent LangGraph pipeline."""
    workflow = StateGraph(AgentState)

    # ── Register agent nodes ───────────────────────────────────────
    workflow.add_node("planning", planning_node)
    workflow.add_node("orchestrator", orchestrator_node)
    workflow.add_node("developer", development_node)
    workflow.add_node("tester", testing_node)
    workflow.add_node("devops", devops_node)

    # ── Flow ───────────────────────────────────────────────────────
    # 1. Start with planning (Scrum Master)
    workflow.set_entry_point("planning")

    # 2. After planning → orchestrator decides next
    workflow.add_edge("planning", "orchestrator")

    # 3. Orchestrator conditionally routes
    workflow.add_conditional_edges(
        "orchestrator",
        _route_from_orchestrator,
        {
            "developer": "developer",
            "tester": "tester",
            "devops": "devops",
            "end": END,
        },
    )

    # 4. ALL agents report back to orchestrator (true hub-and-spoke)
    workflow.add_edge("developer", "orchestrator")
    workflow.add_edge("tester", "orchestrator")
    workflow.add_edge("devops", "orchestrator")

    # ── Compile with memory checkpointer ──────────────────────────
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def get_graph_image() -> bytes:
    """Render the graph as a PNG image (requires graphviz)."""
    graph = build_pipeline()
    try:
        return graph.get_graph().draw_mermaid_png()
    except Exception:
        return b""


def run_pipeline(spec: dict, guidelines_context: str, project_name: str, db_schema: str = "") -> AgentState:
    """
    Execute the full multi-agent build pipeline.
    The Scrum Master orchestrator routes between agents and handles
    the developer↔tester feedback loop on test failures.

    guidelines_context is kept for backward compat but each agent node
    now retrieves its own relevant guidelines via RAG.

    Returns the final AgentState containing all generated artefacts.
    """
    graph = build_pipeline()

    print("\n" + "="*60)
    print("🚀 PIPELINE STARTED")
    print(f"   Project: {project_name}")
    print(f"   RAG mode: each agent retrieves relevant guidelines")
    print(f"   DB schema: {'provided' if db_schema else 'not provided'}")
    print("="*60)

    initial_state: AgentState = {
        "messages": [],
        "spec": spec,
        "guidelines_context": guidelines_context,
        "db_schema": db_schema,
        "project_name": project_name,
        "planning_output": {},
        "api_code": {},
        "test_code": {},
        "test_results": "",
        "test_passed": False,
        "devops_config": {},
        "pr_result": {},
        "current_phase": "started",
        "next_agent": "",
        "retry_count": 0,
        "max_retries": 3,
        "build_log": ["[Pipeline] Multi-agent build pipeline started."],
    }

    config = {"configurable": {"thread_id": project_name}}

    final_state = graph.invoke(initial_state, config)

    print("\n" + "="*60)
    print("🏁 PIPELINE COMPLETE")
    for entry in final_state.get("build_log", []):
        print(f"   {entry}")
    print("="*60 + "\n")

    return final_state
