import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from agents.prompts import (
    PLANNING_PROMPT,
    ORCHESTRATOR_PROMPT,
)
from agents.state import AgentState
from utils.parsers import parse_llm_json


class ScrumMasterAgent:
    """
    Scrum Master Agent — two roles:
      1. Planning phase of the build pipeline  (planning_node)
      2. Orchestrator — decides which agent runs next (orchestrator_node)

    Note: The BA Agent now handles spec conversation and extraction.
    """

    def __init__(self, model: str, api_key: str, temperature: float = 0.3):
        self.llm = ChatOpenAI(model=model, api_key=api_key, temperature=temperature)

    # ── Planning ───────────────────────────────────────────────────

    def generate_planning(self, spec: dict, guidelines: str) -> dict:
        """Generate planning artefacts (Jira, Confluence, flowchart, README)."""
        print("\n📋 [Scrum Master] Generating planning artefacts (Jira, Confluence, Flowchart, README)...")
        prompt = PLANNING_PROMPT.format(
            spec=json.dumps(spec, indent=2),
            guidelines=guidelines,
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        result = parse_llm_json(response.content, self.llm)
        print(f"✅ [Scrum Master] Planning complete — artefacts: {list(result.keys())}")
        return result

    # ── Orchestration Decision ─────────────────────────────────────

    def decide_next(self, state: AgentState) -> str:
        """Use LLM to decide which agent should run next based on full state awareness."""
        print(f"\n🧠 [Orchestrator] Evaluating state — phase={state.get('current_phase')}, "
              f"has_code={bool(state.get('api_code'))}, has_tests={bool(state.get('test_code'))}, "
              f"test_passed={state.get('test_passed')}, has_devops={bool(state.get('devops_config'))}, "
              f"retries={state.get('retry_count', 0)}/{state.get('max_retries', 3)}")
        recent_log = state.get("build_log", [])[-5:]
        prompt = ORCHESTRATOR_PROMPT.format(
            current_phase=state.get("current_phase", "unknown"),
            has_api_code=bool(state.get("api_code")),
            has_test_code=bool(state.get("test_code")),
            test_passed=state.get("test_passed", False),
            has_devops=bool(state.get("devops_config")),
            retry_count=state.get("retry_count", 0),
            max_retries=state.get("max_retries", 3),
            recent_log="\n".join(f"  - {l}" for l in recent_log) if recent_log else "  (none)",
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        decision = response.content.strip().lower()
        # Normalise to valid choices
        for valid in ("developer", "tester", "devops", "end"):
            if valid in decision:
                print(f"➡️  [Orchestrator] Decision: {valid.upper()}")
                return valid
        print("➡️  [Orchestrator] Decision: END (default)")
        return "end"


# ── LangGraph node functions ─────────────────────────────────────

def planning_node(state: AgentState) -> dict:
    """LangGraph node — Scrum Master produces planning artefacts."""
    from config.settings import get_settings
    from rag.retriever import get_retriever

    settings = get_settings()
    agent = ScrumMasterAgent(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)

    # Spec-chat retriever (main guideline.txt) for planning context
    retriever = get_retriever()
    guidelines = retriever.retrieve(
        f"project planning API design architecture data models endpoints {state['spec'].get('project_name', '')}",
        top_k=8,
    )
    print(f"📄 [RAG → Spec Guidelines] Retrieved {len(guidelines)} chars for planning")

    planning = agent.generate_planning(state["spec"], guidelines)

    return {
        "planning_output": planning,
        "current_phase": "planning_complete",
        "build_log": state.get("build_log", [])
        + ["[Scrum Master] Planning phase completed — Jira tickets, Confluence doc, flowchart, and README generated."],
    }


def orchestrator_node(state: AgentState) -> dict:
    """LangGraph node — Scrum Master decides which agent runs next."""
    from config.settings import get_settings

    settings = get_settings()
    agent = ScrumMasterAgent(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    decision = agent.decide_next(state)

    return {
        "next_agent": decision,
        "build_log": state.get("build_log", [])
        + [f"[Scrum Master] Orchestrator decided next agent → {decision}"],
    }
