"""
AI-SDLC Accelerator — Streamlit Application
=============================================
Spec-driven API development powered by multi-agent LangGraph pipeline.
"""

import streamlit as st
import json
import os
import time

# ── Page config (must be first Streamlit call) ────────────────────
st.set_page_config(
    page_title="AI-SDLC Accelerator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Global ──────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Header ──────────────────────────────────────────────────── */
.main-header {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.08);
}
.main-header h1 {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.3rem 0;
}
.main-header p {
    color: rgba(255,255,255,0.65);
    font-size: 0.95rem;
    margin: 0;
}

/* ── Metric cards ────────────────────────────────────────────── */
.metric-card {
    background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3d 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    text-align: center;
}
.metric-card h3 {
    color: rgba(255,255,255,0.5);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 0 0 0.5rem 0;
    font-weight: 600;
}
.metric-card .value {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
}

/* ── Phase badge ─────────────────────────────────────────────── */
.phase-badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.phase-complete  { background: #00c853; color: #fff; }
.phase-running   { background: #ff9800; color: #fff; }
.phase-pending   { background: rgba(255,255,255,0.12); color: rgba(255,255,255,0.45); }

/* ── Build log ───────────────────────────────────────────────── */
.build-log {
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.82rem;
    line-height: 1.7;
    color: #c9d1d9;
    max-height: 320px;
    overflow-y: auto;
}
.build-log .log-line {
    padding: 2px 0;
}
.build-log .log-success { color: #3fb950; }
.build-log .log-info    { color: #58a6ff; }
.build-log .log-warn    { color: #d29922; }

/* ── File tree ───────────────────────────────────────────────── */
.file-tree {
    background: #161b22;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.9;
    color: #8b949e;
}
.file-tree .folder { color: #58a6ff; font-weight: 600; }
.file-tree .file   { color: #c9d1d9; }

/* ── Sidebar ─────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #1a1a2e 100%);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #ffffff;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li {
    color: rgba(255,255,255,0.7);
}

/* ── Tabs ────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 500;
}

/* ── Code block improvements ─────────────────────────────────── */
.stCodeBlock {
    border-radius: 10px !important;
}

/* ── Chat styling ────────────────────────────────────────────── */
.stChatMessage {
    border-radius: 14px;
}

/* ── Buttons ─────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    padding: 0.55rem 1.6rem;
    transition: all 0.2s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

/* ── Divider ─────────────────────────────────────────────────── */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    margin: 1.5rem 0;
}
</style>
""",
    unsafe_allow_html=True,
)


# ── Session state initialisation ──────────────────────────────────

def init_session_state():
    defaults = {
        "chat_history": [],
        "spec_confirmed": False,
        "extracted_spec": None,
        "build_started": False,
        "build_complete": False,
        "build_result": None,
        "build_log": [],
        "retriever_ready": False,
        "guideline_retriever": None,
        "scrum_master": None,
        "artifacts_saved": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ── Helper loaders (cached) ──────────────────────────────────────

@st.cache_resource(show_spinner=False)
def load_retriever(api_key: str, guidelines_path: str):
    from rag.retriever import GuidelineRetriever

    retriever = GuidelineRetriever(guidelines_path=guidelines_path, api_key=api_key)
    retriever.initialize()
    return retriever


@st.cache_resource(show_spinner=False)
def load_ba_agent(model: str, api_key: str):
    from agents.ba_agent import BAAgent

    return BAAgent(model=model, api_key=api_key)


@st.cache_resource(show_spinner=False)
def load_database(db_path: str):
    from database.db_manager import DatabaseManager

    return DatabaseManager(db_path=db_path)


# ── Sidebar ───────────────────────────────────────────────────────

# Load all config from .env
from config.settings import get_settings as _get_settings
_settings = _get_settings()
api_key = _settings.OPENAI_API_KEY
model = _settings.OPENAI_MODEL
guidelines_path = _settings.GUIDELINES_PATH
db_path = _settings.DATABASE_PATH
output_dir = _settings.OUTPUT_DIR
gh_token = _settings.GITHUB_TOKEN
gh_owner = _settings.GITHUB_REPO_OWNER
gh_repo = _settings.GITHUB_REPO_NAME

with st.sidebar:
    st.markdown("# ⚡ AI-SDLC")
    st.markdown("##### Spec-Driven API Accelerator")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Agent Flow Diagram ──
    st.markdown("### 🔀 Agent Flow")
    st.markdown(
        """
<div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px; padding: 1rem; font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem; line-height: 1.6; color: rgba(255,255,255,0.8);">
<div style="text-align:center; margin-bottom:0.5rem; font-weight:700; color:#00c853;">▶ START</div>
<div style="text-align:center;">│</div>
<div style="text-align:center; background:#0d47a1; padding:4px 10px; border-radius:8px; display:inline-block; margin:2px auto; width:85%;">
🧑‍💼 <b>BA Agent</b><br/><span style="font-size:0.6rem; color:#aaa;">Queries DB → Spec Chat → Extract Spec</span>
</div>
<div style="text-align:center;">│</div>
<div style="text-align:center; background:#1a237e; padding:4px 10px; border-radius:8px; display:inline-block; margin:2px auto; width:85%;">
📋 <b>Scrum Master</b><br/><span style="font-size:0.6rem; color:#aaa;">Planning · Jira · Confluence · README</span>
</div>
<div style="text-align:center;">│</div>
<div style="text-align:center; background:#ff6f00; padding:4px 10px; border-radius:8px; display:inline-block; margin:2px auto; width:85%;">
🎯 <b>ORCHESTRATOR</b><br/><span style="font-size:0.6rem; color:#ddd;">Scrum Master routes agents</span>
</div>
<div style="text-align:center;">┌────┼────┐</div>
<div style="display:flex; justify-content:space-around; margin:4px 0;">
<div style="background:#1b5e20; padding:3px 6px; border-radius:6px; text-align:center; width:30%;">
💻<br/><b style="font-size:0.6rem;">Developer</b>
</div>
<div style="background:#b71c1c; padding:3px 6px; border-radius:6px; text-align:center; width:30%;">
🧪<br/><b style="font-size:0.6rem;">Tester</b>
</div>
<div style="background:#4a148c; padding:3px 6px; border-radius:6px; text-align:center; width:30%;">
🔧<br/><b style="font-size:0.6rem;">DevOps</b>
</div>
</div>
<div style="text-align:center;">└────┼────┘</div>
<div style="text-align:center; font-size:0.6rem; color:#d29922;">↻ Dev↔Test fix loop (up to 3×)</div>
<div style="text-align:center;">│</div>
<div style="text-align:center; font-weight:700; color:#00c853;">✅ END</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Pipeline Status ──
    st.markdown("### 📊 Pipeline Status")
    if st.session_state.build_complete:
        phases = ["Planning", "Development", "Testing", "DevOps"]
        for p in phases:
            st.markdown(f'<span class="phase-badge phase-complete">✔ {p}</span>', unsafe_allow_html=True)
        retry = st.session_state.build_result.get("retry_count", 0)
        if retry > 0:
            st.caption(f"Dev↔Test fix loops: {retry}")
        if st.session_state.get("pr_url"):
            st.markdown(f"🔗 [Pull Request]({st.session_state['pr_url']})")
    elif st.session_state.build_started:
        st.info("🔄 Build in progress…")
    else:
        st.caption("Pipeline idle — start a spec conversation.")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Config Summary ──
    st.markdown("### ⚙ Configuration")
    st.caption(f"**Model:** {model}")
    st.caption(f"**Guidelines:** {guidelines_path}")
    st.caption(f"**GitHub:** {gh_owner}/{gh_repo}" if gh_owner and gh_repo else "**GitHub:** Not configured")
    st.caption("_All settings loaded from `.env`_")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Reset ──
    if st.button("🔄 Reset Project", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ── Header ────────────────────────────────────────────────────────

st.markdown(
    """
<div class="main-header">
    <h1>⚡ AI-SDLC Accelerator</h1>
    <p>From business requirement to production-ready API stubs — powered by multi-agent spec-driven development.</p>
</div>
""",
    unsafe_allow_html=True,
)


# ── Tabs ──────────────────────────────────────────────────────────

tab_chat, tab_plan, tab_code, tab_tests, tab_devops, tab_dash = st.tabs(
    ["💬 Spec Chat", "📋 Planning", "💻 API Code", "🧪 Tests", "🔧 DevOps", "📊 Dashboard"]
)

# =====================================================================
# TAB 1 — Spec-Driven Conversation
# =====================================================================
with tab_chat:
    if not api_key:
        st.warning("Set your **OPENAI_API_KEY** in the `.env` file to begin.")
        st.stop()

    # Lazy-load components
    retriever = load_retriever(api_key, guidelines_path)
    ba_agent = load_ba_agent(model, api_key)
    db = load_database(db_path)

    st.markdown("### 💬 Spec-Driven Conversation")
    st.caption(
        "Describe the API you need. The **BA Agent** will query the database, understand your "
        "business requirements, and help you build a complete specification."
    )

    # Render history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

    # Chat input
    if not st.session_state.spec_confirmed:
        if prompt := st.chat_input("Describe your API requirements…"):
            # Show user message immediately
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            # Get guidelines context via RAG
            context = retriever.retrieve(prompt)

            # Get DB schema so BA can reference available data
            db_schema = db.get_schema_summary()

            # Agent response
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("BA Agent is analysing…"):
                    response = ba_agent.conduct_conversation(
                        prompt,
                        st.session_state.chat_history[:-1],  # exclude the just-added user msg
                        context,
                        db_schema=db_schema,
                    )
                st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()

        # Confirm & Build button
        if len(st.session_state.chat_history) >= 4:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            col_l, col_mid, col_r = st.columns([1, 2, 1])
            with col_mid:
                if st.button("✅  Confirm Specification & Start Build", use_container_width=True, type="primary"):
                    with st.spinner("BA Agent extracting structured specification…"):
                        # RAG: retrieve relevant guidelines for spec extraction
                        conversation_text = " ".join(m["content"] for m in st.session_state.chat_history)
                        spec_guidelines = retriever.retrieve(conversation_text, top_k=8)
                        spec = ba_agent.extract_spec(st.session_state.chat_history, spec_guidelines)
                        st.session_state.extracted_spec = spec
                        st.session_state.spec_confirmed = True
                    st.rerun()
    else:
        st.success("Specification confirmed. Scroll to the **Dashboard** tab to monitor the build.")

    # ── Auto-trigger build ────────────────────────────────────────
    if st.session_state.spec_confirmed and not st.session_state.build_started:
        st.session_state.build_started = True

        with st.status("🚀 Running build pipeline…", expanded=True) as status:
            st.write("**Phase 1/4** — Planning (Jira · Confluence · Flowchart)")
            from agents.graph import run_pipeline

            project_name = st.session_state.extracted_spec.get("project_name", "api-project")

            # RAG: retrieve broad guidelines for pipeline init (each node does its own RAG too)
            pipeline_guidelines = retriever.retrieve(
                f"API development guidelines standards {project_name}", top_k=6
            )

            # Pass DB schema so agents can reference real tables
            db_schema = db.get_schema_summary()

            result = run_pipeline(
                spec=st.session_state.extracted_spec,
                guidelines_context=pipeline_guidelines,
                project_name=project_name,
                db_schema=db_schema,
            )

            st.session_state.build_result = result
            st.session_state.build_log = result.get("build_log", [])
            st.session_state.build_complete = True
            st.session_state.artifacts_saved = True

            # PR result comes from DevOps agent
            pr_result = result.get("pr_result", {})
            if pr_result.get("success"):
                st.session_state["pr_url"] = pr_result["pr_url"]
                st.write(f"✅ PR created: {pr_result['pr_url']}")
            elif pr_result.get("error"):
                st.session_state["pr_error"] = pr_result["error"]
                st.write(f"⚠️ PR creation failed: {pr_result['error']}")

            status.update(label="✅ Build pipeline complete!", state="complete")

        st.rerun()

# =====================================================================
# TAB 2 — Planning
# =====================================================================
with tab_plan:
    st.markdown("### 📋 Planning Artefacts")
    if not st.session_state.build_complete:
        st.info("Complete the spec conversation and confirm to generate planning documents.")
    else:
        planning = st.session_state.build_result.get("planning_output", {})

        plan_tabs = st.tabs(["🎫 Jira Tickets", "📄 Confluence Doc", "📐 Flowchart", "📖 README"])

        with plan_tabs[0]:
            st.markdown("#### Jira-Style Tickets")
            st.markdown(planning.get("jira_tickets", "*Not generated.*"))

        with plan_tabs[1]:
            st.markdown("#### Technical Design Document")
            st.markdown(planning.get("confluence_doc", "*Not generated.*"))

        with plan_tabs[2]:
            st.markdown("#### Architecture Flowchart")
            flowchart = planning.get("flowchart", "")
            if flowchart:
                st.markdown(flowchart)
            else:
                st.caption("No flowchart generated.")

        with plan_tabs[3]:
            st.markdown("#### Project README")
            st.markdown(planning.get("readme", "*Not generated.*"))

# =====================================================================
# TAB 3 — API Code
# =====================================================================
with tab_code:
    st.markdown("### 💻 Generated API Code")
    if not st.session_state.build_complete:
        st.info("Complete the spec conversation and confirm to generate API code.")
    else:
        api_code = st.session_state.build_result.get("api_code", {})
        if not api_code:
            st.warning("No API code was generated.")
        else:
            # File selector
            filenames = sorted(api_code.keys())
            col_select, col_info = st.columns([3, 1])
            with col_select:
                selected_file = st.selectbox("Select file", filenames, label_visibility="collapsed")
            with col_info:
                st.caption(f"{len(filenames)} files generated")

            if selected_file:
                ext = selected_file.rsplit(".", 1)[-1] if "." in selected_file else "text"
                lang_map = {"py": "python", "txt": "text", "yml": "yaml", "yaml": "yaml", "toml": "toml", "cfg": "ini", "md": "markdown"}
                lang = lang_map.get(ext, ext)
                st.code(api_code[selected_file], language=lang, line_numbers=True)

# =====================================================================
# TAB 4 — Tests
# =====================================================================
with tab_tests:
    st.markdown("### 🧪 Test Suite")
    if not st.session_state.build_complete:
        st.info("Complete the spec conversation and confirm to generate tests.")
    else:
        test_code = st.session_state.build_result.get("test_code", {})
        test_results = st.session_state.build_result.get("test_results", "")

        if not test_code:
            st.warning("No test code was generated.")
        else:
            test_tabs = st.tabs(["📝 Test Code", "▶ Test Results"])

            with test_tabs[0]:
                test_files = sorted(test_code.keys())
                selected_test = st.selectbox("Select test file", test_files, label_visibility="collapsed")
                if selected_test:
                    st.code(test_code[selected_test], language="python", line_numbers=True)

            with test_tabs[1]:
                st.markdown("#### Execution Output")
                test_passed = st.session_state.build_result.get("test_passed", None)
                if test_passed is True:
                    st.success("Tests PASSED ✅")
                elif test_passed is False and test_results:
                    st.error("Tests FAILED ❌")
                if test_results:
                    st.code(test_results, language="text")
                else:
                    st.caption("No test results available yet.")

                retry_info = st.session_state.build_result.get("retry_count", 0)
                max_r = st.session_state.build_result.get("max_retries", 3)
                if retry_info > 0:
                    st.caption(f"Developer↔Tester fix loops: {retry_info}/{max_r}")

                if st.button("▶ Run Tests Now", type="primary"):
                    with st.spinner("Executing tests…"):
                        from agents.tester import TesterAgent

                        run_output, run_passed = TesterAgent.run_tests(output_dir)
                        st.session_state.build_result["test_results"] = run_output
                        st.session_state.build_result["test_passed"] = run_passed
                    if run_passed:
                        st.success("Tests PASSED ✅")
                    else:
                        st.error("Tests FAILED ❌")
                    st.code(run_output, language="text")

# =====================================================================
# TAB 5 — DevOps
# =====================================================================
with tab_devops:
    st.markdown("### 🔧 DevOps Configuration")
    if not st.session_state.build_complete:
        st.info("Complete the spec conversation and confirm to generate DevOps configs.")
    else:
        devops = st.session_state.build_result.get("devops_config", {})
        if not devops:
            st.warning("No DevOps configurations were generated.")
        else:
            devops_files = sorted(devops.keys())
            col_sel, col_count = st.columns([3, 1])
            with col_sel:
                selected_devops = st.selectbox("Select config", devops_files, label_visibility="collapsed")
            with col_count:
                st.caption(f"{len(devops_files)} configs generated")

            if selected_devops:
                ext = selected_devops.rsplit(".", 1)[-1] if "." in selected_devops else "text"
                lang_map = {"yml": "yaml", "yaml": "yaml", "Dockerfile": "dockerfile", "dockerignore": "text"}
                lang = lang_map.get(ext, "yaml")
                if "Dockerfile" in selected_devops:
                    lang = "dockerfile"
                st.code(devops[selected_devops], language=lang, line_numbers=True)

        # ── GitHub PR ─────────────────────────────────────────────
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 🔗 GitHub Pull Request")

        # Show auto-PR result if it already ran
        if st.session_state.get("pr_url"):
            st.success(f"✅ PR automatically created: {st.session_state['pr_url']}")
        elif st.session_state.get("pr_error"):
            st.error(f"Auto-PR failed: {st.session_state['pr_error']}")
            st.caption("You can retry manually below.")

        if not gh_token or not gh_owner or not gh_repo:
            st.caption("Add GitHub credentials in `.env` to enable automatic PR creation.")
        elif not st.session_state.get("pr_url"):
            # Manual retry button (only if auto-PR didn't succeed)
            pr_title = st.text_input(
                "PR Title",
                value=f"feat: {st.session_state.extracted_spec.get('project_name', 'new-api')} — AI-generated API stub",
            )
            if st.button("🚀 Create Pull Request", type="primary"):
                with st.spinner("Pushing branch and creating PR…"):
                    from utils.git_utils import init_local_repo, create_branch_and_commit, push_and_create_pr

                    project_dir = os.path.join(output_dir)
                    branch = f"feature/{st.session_state.extracted_spec.get('project_name', 'api')}-stub"
                    init_local_repo(project_dir)
                    create_branch_and_commit(project_dir, branch, pr_title)
                    pr_result = push_and_create_pr(
                        project_dir, branch, pr_title,
                        f"Auto-generated by AI-SDLC Accelerator\n\n**Spec:**\n```json\n{json.dumps(st.session_state.extracted_spec, indent=2)}\n```",
                        gh_token, gh_owner, gh_repo,
                    )
                if pr_result.get("success"):
                    st.session_state["pr_url"] = pr_result["pr_url"]
                    st.success(f"PR created: {pr_result['pr_url']}")
                else:
                    st.error(f"PR creation failed: {pr_result.get('error', 'Unknown error')}")

# =====================================================================
# TAB 6 — Dashboard
# =====================================================================
with tab_dash:
    st.markdown("### 📊 Project Dashboard")

    if st.session_state.build_complete:
        result = st.session_state.build_result

        # ── Metric row ──
        m1, m2, m3, m4, m5 = st.columns(5)
        api_count = len(result.get("api_code", {}))
        test_count = len(result.get("test_code", {}))
        devops_count = len(result.get("devops_config", {}))
        plan_count = sum(1 for v in result.get("planning_output", {}).values() if v)
        fix_loops = result.get("retry_count", 0)
        for col, label, val in [
            (m1, "API FILES", api_count),
            (m2, "TEST FILES", test_count),
            (m3, "DEVOPS CONFIGS", devops_count),
            (m4, "PLANNING DOCS", plan_count),
            (m5, "FIX LOOPS", fix_loops),
        ]:
            col.markdown(
                f'<div class="metric-card"><h3>{label}</h3><div class="value">{val}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        # ── LangGraph Agent Topology ──
        with st.expander("🔀 LangGraph Multi-Agent Architecture", expanded=True):
            mermaid_chart = """
```mermaid
graph TD
    START([🚀 Start]) --> BA[🧑‍💼 BA Agent<br/><i>Queries DB · Spec Chat · Extract Spec</i>]
    BA --> PLAN[📋 Planning<br/><i>Scrum Master Agent</i>]
    PLAN --> ORCH{🎯 ORCHESTRATOR<br/><i>Scrum Master Agent</i>}

    ORCH -->|route| DEV[💻 Developer Agent]
    ORCH -->|route| TEST[🧪 Tester Agent]
    ORCH -->|route| DEVOPS[🔧 DevOps Agent]
    ORCH -->|done| DONE([✅ End])

    DEV -->|report back| ORCH
    TEST -->|report back| ORCH
    DEVOPS -->|report back| ORCH

    TEST -.-|"❌ fail → fix"| DEV

    style START fill:#00c853,stroke:#00c853,color:#fff
    style BA fill:#0d47a1,stroke:#1565c0,color:#fff
    style PLAN fill:#1a237e,stroke:#3949ab,color:#fff
    style ORCH fill:#ff6f00,stroke:#ffa000,color:#fff
    style DEV fill:#1b5e20,stroke:#43a047,color:#fff
    style TEST fill:#b71c1c,stroke:#e53935,color:#fff
    style DEVOPS fill:#4a148c,stroke:#7b1fa2,color:#fff
    style DONE fill:#00c853,stroke:#00c853,color:#fff
```
"""
            st.markdown(mermaid_chart)
            st.caption(
                "The **BA Agent** gathers requirements and produces a spec. "
                "The **Scrum Master** plans and orchestrates — after each agent completes, "
                "it decides the next step. If tests fail, the Developer Agent is called again "
                f"to fix the code (up to {result.get('max_retries', 3)} retries)."
            )

        # ── LangGraph PNG (if graphviz available) ──
        with st.expander("📸 LangGraph Compiled Graph (PNG)", expanded=False):
            try:
                from agents.graph import get_graph_image

                png = get_graph_image()
                if png:
                    st.image(png, caption="Auto-rendered by LangGraph", use_container_width=True)
                else:
                    st.caption("Install `pygraphviz` or `grandalf` for auto-rendered PNG.")
            except Exception as e:
                st.caption(f"Graph rendering unavailable: {e}")

        # ── Spec Summary ──
        with st.expander("📐 Confirmed Specification", expanded=False):
            st.json(st.session_state.extracted_spec)

        # ── File Tree ──
        with st.expander("📂 Generated File Tree", expanded=True):
            from utils.file_utils import list_artifacts

            tree = list_artifacts(output_dir)
            tree_lines = []
            for cat, files in sorted(tree.items()):
                tree_lines.append(f'<span class="folder">📁 {cat}/</span>')
                for f in files:
                    tree_lines.append(f'&nbsp;&nbsp;&nbsp;&nbsp;<span class="file">📄 {f}</span>')
            if tree_lines:
                st.markdown(
                    f'<div class="file-tree">{"<br>".join(tree_lines)}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No artefacts saved yet.")

        # ── Build Log ──
        with st.expander("📜 Build Log (Agent Trace)", expanded=True):
            log_lines = st.session_state.build_log or result.get("build_log", [])
            if log_lines:
                html_lines = []
                for line in log_lines:
                    if "scrum master" in line.lower():
                        css_class = "log-warn"
                    elif "completed" in line.lower() or "passed" in line.lower():
                        css_class = "log-success"
                    elif "failed" in line.lower():
                        css_class = "log-warn"
                    else:
                        css_class = "log-info"
                    html_lines.append(f'<div class="log-line {css_class}">▸ {line}</div>')
                st.markdown(f'<div class="build-log">{"".join(html_lines)}</div>', unsafe_allow_html=True)
            else:
                st.caption("No logs yet.")

        # ── Database Info ──
        with st.expander("🗄 Database Schema (SQLite)", expanded=False):
            db_inst = load_database(db_path)
            table_info = db_inst.get_table_info()
            for table_name, info in table_info.items():
                st.markdown(f"**`{table_name}`** — {info['row_count']} rows")
                col_data = [{"Column": c["name"], "Type": c["type"], "PK": "✔" if c["pk"] else "", "NOT NULL": "✔" if c["notnull"] else ""} for c in info["columns"]]
                st.dataframe(col_data, use_container_width=True, hide_index=True)

    elif st.session_state.build_started:
        st.info("🔄 Build pipeline is running…")
    else:
        # Show the graph even before build starts
        st.markdown("#### 🔀 Multi-Agent Architecture")
        mermaid_idle = """
```mermaid
graph TD
    START([🚀 Start]) --> BA[🧑‍💼 BA Agent<br/><i>Queries DB · Spec Chat · Extract Spec</i>]
    BA --> PLAN[📋 Planning<br/><i>Scrum Master Agent</i>]
    PLAN --> ORCH{🎯 ORCHESTRATOR<br/><i>Scrum Master Agent</i>}

    ORCH -->|route| DEV[💻 Developer Agent]
    ORCH -->|route| TEST[🧪 Tester Agent]
    ORCH -->|route| DEVOPS[🔧 DevOps Agent]
    ORCH -->|done| DONE([✅ End])

    DEV -->|report back| ORCH
    TEST -->|report back| ORCH
    DEVOPS -->|report back| ORCH

    TEST -.-|fail → fix| DEV

    style START fill:#555,stroke:#777,color:#fff
    style BA fill:#0d47a1,stroke:#1565c0,color:#aaa
    style PLAN fill:#333,stroke:#555,color:#aaa
    style ORCH fill:#444,stroke:#666,color:#ddd
    style DEV fill:#333,stroke:#555,color:#aaa
    style TEST fill:#333,stroke:#555,color:#aaa
    style DEVOPS fill:#333,stroke:#555,color:#aaa
    style DONE fill:#555,stroke:#777,color:#fff
```
"""
        st.markdown(mermaid_idle)
        st.markdown(
            """
        <div style="text-align:center; padding: 2rem;">
            <p style="color: rgba(255,255,255,0.3);">
            Complete the spec conversation in the <strong>Spec Chat</strong> tab to activate the pipeline.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ── Footer ────────────────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.caption("AI-SDLC Accelerator · Multi-Agent Spec-Driven Development · LangGraph + RAG Pipeline")
