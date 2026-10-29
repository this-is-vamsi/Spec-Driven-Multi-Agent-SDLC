import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from agents.prompts import TESTER_PROMPT
from agents.state import AgentState
from utils.parsers import parse_llm_json


class TesterAgent:
    """
    Tester Agent — dedicated LangGraph agent:
      1. Generates local unit tests for business-logic functions
      2. Executes tests via pytest and reports pass/fail status
    """

    def __init__(self, model: str, api_key: str, temperature: float = 0.2):
        self.llm = ChatOpenAI(model=model, api_key=api_key, temperature=temperature)

    def generate_tests(self, api_code: dict, spec: dict, guidelines: str) -> dict[str, str]:
        """Return {filename: test_source} for the complete test suite."""
        print("\n🧪 [Tester] Generating local unit tests (function-level, no API server)...")
        prompt = TESTER_PROMPT.format(
            api_code=json.dumps(api_code, indent=2),
            spec=json.dumps(spec, indent=2),
            guidelines=guidelines,
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        result = parse_llm_json(response.content, self.llm)
        print(f"✅ [Tester] Tests generated — {len(result)} test files: {list(result.keys())}")
        return result

    @staticmethod
    def run_tests(output_dir: str) -> tuple[str, bool]:
        """
        Execute the generated unit tests via pytest.
        Tests run locally — no server needed.
        Returns (output_text, passed_bool).
        """
        import subprocess
        import os

        tests_dir = os.path.abspath(os.path.join(output_dir, "tests"))
        api_dir = os.path.abspath(os.path.join(output_dir, "api"))

        if not os.path.isdir(tests_dir):
            return "No tests directory found — skipping execution.", False

        run_cwd = os.path.abspath(output_dir)

        env = os.environ.copy()
        existing = env.get("PYTHONPATH", "")
        # tests_dir on PYTHONPATH so `from conftest import X` works
        # api_dir and run_cwd included for backward compatibility
        paths = os.pathsep.join(filter(None, [tests_dir, api_dir, run_cwd, existing]))
        env["PYTHONPATH"] = paths

        try:
            print("🏃 [Tester] Running local unit tests (no server required)...")
            result = subprocess.run(
                ["python", "-m", "pytest", tests_dir, "-v", "--tb=short", "-x"],
                capture_output=True,
                text=True,
                cwd=run_cwd,
                env=env,
                timeout=60,
            )
            output = (result.stdout + "\n" + result.stderr).strip()
            passed = result.returncode == 0
            if not output:
                output = "Tests executed — no output captured."
            return output, passed
        except FileNotFoundError:
            return "pytest not found — install it to run tests.", False
        except subprocess.TimeoutExpired:
            return "Test execution timed out after 60 seconds.", False
        except Exception as e:
            return f"Test execution error: {e}", False


# ── LangGraph node function ───────────────────────────────────────

def testing_node(state: AgentState) -> dict:
    """
    LangGraph node — Tester Agent.
    Generates tests, saves them, executes them, and reports pass/fail.
    """
    from config.settings import get_settings
    from utils.file_utils import save_artifacts
    from rag.retriever import get_tester_retriever

    settings = get_settings()
    agent = TesterAgent(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY)
    output_dir = settings.OUTPUT_DIR

    # Tester agent uses its own guideline document
    retriever = get_tester_retriever()
    guidelines = retriever.retrieve(
        f"pytest test cases API validation error handling fixtures conftest {state['spec'].get('project_name', '')}",
        top_k=8,
    )
    print(f"📄 [RAG → Tester Guidelines] Retrieved {len(guidelines)} chars")

    test_code = agent.generate_tests(
        state.get("api_code", {}),
        state["spec"],
        guidelines,
    )

    # Strip "tests/" prefix from keys to avoid nested tests/tests/ directory
    cleaned_tests = {}
    for k, v in test_code.items():
        clean_key = k.replace("tests/", "").replace("tests\\", "") if k.startswith("tests") else k
        cleaned_tests[clean_key] = v
    test_code = cleaned_tests

    # Save api code + tests so we can execute them
    save_artifacts(output_dir, {"api": state.get("api_code", {}), "tests": test_code})

    # Execute tests
    print("\n🏃 [Tester] Executing tests via pytest...")
    test_output, passed = TesterAgent.run_tests(output_dir)

    status = "PASSED ✅" if passed else "FAILED ❌"
    print(f"{'✅' if passed else '❌'} [Tester] Test execution: {status}")
    retry_count = state.get("retry_count", 0)
    new_retry = retry_count if passed else retry_count + 1

    return {
        "test_code": test_code,
        "test_results": test_output,
        "test_passed": passed,
        "retry_count": new_retry,
        "current_phase": "testing_complete",
        "build_log": state.get("build_log", [])
        + [
            f"[Tester Agent] {len(test_code)} test files generated.",
            f"[Tester Agent] Test execution: {status}",
            f"[Tester Agent] Retry count: {new_retry}/{state.get('max_retries', 3)}",
        ],
    }
