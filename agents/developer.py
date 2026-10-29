import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from agents.prompts import DEVELOPER_PROMPT, DEVELOPER_FIX_PROMPT
from agents.state import AgentState
from utils.parsers import parse_llm_json


class DeveloperAgent:
    """
    Developer Agent — dedicated LangGraph agent with two capabilities:
      1. Generate fresh API code from spec
      2. Fix code based on test failure feedback
    """

    def __init__(self, model: str, api_key: str, temperature: float = 0.2):
        self.llm = ChatOpenAI(model=model, api_key=api_key, temperature=temperature)

    def generate_code(self, spec: dict, planning: dict, guidelines: str) -> dict[str, str]:
        """Return {filename: source_code} for the complete API project."""
        print("\n💻 [Developer] Generating API code from spec...")
        prompt = DEVELOPER_PROMPT.format(
            spec=json.dumps(spec, indent=2),
            planning=json.dumps(planning, indent=2),
            guidelines=guidelines,
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        result = parse_llm_json(response.content, self.llm)
        print(f"✅ [Developer] Code generated — {len(result)} files: {list(result.keys())}")
        return result

    def fix_code(self, api_code: dict, test_results: str, spec: dict, guidelines: str) -> dict[str, str]:
        """Analyse test failures and return corrected code."""
        print("\n🔧 [Developer] Fixing code based on test failures...")
        prompt = DEVELOPER_FIX_PROMPT.format(
            test_results=test_results,
            api_code=json.dumps(api_code, indent=2),
            spec=json.dumps(spec, indent=2),
            guidelines=guidelines,
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        result = parse_llm_json(response.content, self.llm)
        print(f"✅ [Developer] Code fix complete — {len(result)} files regenerated")
        return result


# ── LangGraph node function ───────────────────────────────────────

def development_node(state: AgentState) -> dict:
    """
    LangGraph node — Developer Agent.
    First run: generates code from spec.
    Subsequent runs (after test failure): fixes code using test feedback.
    """
    from config.settings import get_settings
    from rag.retriever import get_developer_retriever

    settings = get_settings()
    agent = DeveloperAgent(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)

    # Developer agent uses its own guideline document
    retriever = get_developer_retriever()
    guidelines = retriever.retrieve(
        f"FastAPI code generation models schemas routes response format database SQLAlchemy {state['spec'].get('project_name', '')}",
        top_k=8,
    )
    print(f"📄 [RAG → Developer Guidelines] Retrieved {len(guidelines)} chars")

    # Append DB schema to guidelines so the developer knows the real tables
    db_schema = state.get("db_schema", "")
    if db_schema:
        guidelines = guidelines + "\n\n" + db_schema

    retry_count = state.get("retry_count", 0)
    existing_code = state.get("api_code", {})
    test_results = state.get("test_results", "")

    # If we have existing code AND test failures → this is a FIX pass
    if existing_code and test_results and not state.get("test_passed", True):
        code = agent.fix_code(
            existing_code,
            test_results,
            state["spec"],
            guidelines,
        )
        log_msg = f"[Developer Agent] Code fix attempt #{retry_count + 1} — {len(code)} files regenerated."
    else:
        code = agent.generate_code(
            state["spec"],
            state.get("planning_output", {}),
            guidelines,
        )
        log_msg = f"[Developer Agent] Initial code generation — {len(code)} files created."

    return {
        "api_code": code,
        "current_phase": "development_complete",
        "build_log": state.get("build_log", []) + [log_msg],
    }
