from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Shared state that flows through the multi-agent LangGraph pipeline."""

    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Confirmed API specification extracted from the spec conversation
    spec: dict

    # Company guidelines context pulled via RAG
    guidelines_context: str

    # Database schema + sample data for code generation
    db_schema: str

    # Project metadata
    project_name: str

    # ── Phase outputs ──────────────────────────────────────────────
    planning_output: dict      # jira_tickets, confluence_doc, flowchart, readme
    api_code: dict             # filename → source code
    test_code: dict            # filename → test source code
    test_results: str          # stdout / summary of test execution
    test_passed: bool          # whether tests passed
    devops_config: dict        # filename → config content
    pr_result: dict            # GitHub PR result from DevOps agent

    # ── Orchestration ──────────────────────────────────────────────
    current_phase: str
    next_agent: str            # scrum master decides who goes next
    retry_count: int           # how many dev→test loops have occurred
    max_retries: int           # cap on fix attempts (default 3)
    build_log: list[str]
