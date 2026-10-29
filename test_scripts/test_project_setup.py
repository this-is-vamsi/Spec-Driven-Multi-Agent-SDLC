"""
Test Project Components
========================
Validates that all core project components initialise correctly:
- Settings load from .env
- Database initialises with seed data
- RAG retriever builds FAISS index
- Agent classes instantiate

Usage:
    python -m test_scripts.test_project_setup
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


def test_settings():
    """Test 1: Settings load correctly."""
    print("=" * 60)
    print("TEST 1: Settings")
    print("=" * 60)
    try:
        from config.settings import get_settings
        s = get_settings()
        assert s.OPENAI_API_KEY, "OPENAI_API_KEY not set"
        assert s.OPENAI_MODEL, "OPENAI_MODEL not set"
        print(f"  ✅ PASS — Model: {s.OPENAI_MODEL}, Output: {s.OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"  ❌ FAIL — {e}")
        return False


def test_database():
    """Test 2: Database initialises and has seed data."""
    print("\n" + "=" * 60)
    print("TEST 2: Database")
    print("=" * 60)
    try:
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        info = db.get_table_info()
        for table, meta in info.items():
            print(f"  📊 {table}: {meta['row_count']} rows, {len(meta['columns'])} columns")
        assert info["products"]["row_count"] >= 20, "Expected 20+ products"
        assert info["customers"]["row_count"] >= 10, "Expected 10+ customers"
        assert info["orders"]["row_count"] >= 25, "Expected 25+ orders"

        schema = db.get_schema_summary()
        assert len(schema) > 100, "Schema summary too short"
        print(f"  ✅ PASS — Schema summary: {len(schema)} chars")
        return True
    except Exception as e:
        print(f"  ❌ FAIL — {e}")
        return False


def test_rag_retriever():
    """Test 3: RAG retriever initialises and retrieves content."""
    print("\n" + "=" * 60)
    print("TEST 3: RAG Retriever")
    print("=" * 60)
    try:
        from rag.retriever import get_retriever
        retriever = get_retriever()
        result = retriever.retrieve("API response format standards", top_k=3)
        assert len(result) > 0, "Retriever returned empty result"
        print(f"  ✅ PASS — Retrieved {len(result)} chars for test query")
        return True
    except Exception as e:
        print(f"  ❌ FAIL — {e}")
        return False


def test_agent_instantiation():
    """Test 4: All agent classes instantiate correctly."""
    print("\n" + "=" * 60)
    print("TEST 4: Agent Instantiation")
    print("=" * 60)
    try:
        from config.settings import get_settings
        s = get_settings()

        from agents.ba_agent import BAAgent
        ba = BAAgent(model=s.OPENAI_MODEL, api_key=s.OPENAI_API_KEY)
        print(f"  ✅ BAAgent — OK")

        from agents.scrum_master import ScrumMasterAgent
        sm = ScrumMasterAgent(model=s.OPENAI_MODEL, api_key=s.OPENAI_API_KEY)
        print(f"  ✅ ScrumMasterAgent — OK")

        from agents.developer import DeveloperAgent
        dev = DeveloperAgent(model=s.OPENAI_MODEL, api_key=s.OPENAI_API_KEY)
        print(f"  ✅ DeveloperAgent — OK")

        from agents.tester import TesterAgent
        tester = TesterAgent(model=s.OPENAI_MODEL, api_key=s.OPENAI_API_KEY)
        print(f"  ✅ TesterAgent — OK")

        from agents.devops import DevOpsAgent
        devops = DevOpsAgent(model=s.OPENAI_MODEL, api_key=s.OPENAI_API_KEY)
        print(f"  ✅ DevOpsAgent — OK")

        print(f"  ✅ PASS — All 5 agents instantiated")
        return True
    except Exception as e:
        print(f"  ❌ FAIL — {e}")
        return False


def test_graph_builds():
    """Test 5: LangGraph pipeline compiles."""
    print("\n" + "=" * 60)
    print("TEST 5: LangGraph Pipeline Build")
    print("=" * 60)
    try:
        from agents.graph import build_pipeline
        graph = build_pipeline()
        assert graph is not None
        print(f"  ✅ PASS — Pipeline compiled successfully")
        return True
    except Exception as e:
        print(f"  ❌ FAIL — {e}")
        return False


def main():
    print("\n🧪 AI-SDLC — Project Setup Test Suite")
    print("=" * 60)

    results = {}
    results["settings"] = test_settings()
    results["database"] = test_database()
    results["rag"] = test_rag_retriever()
    results["agents"] = test_agent_instantiation()
    results["graph"] = test_graph_builds()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {name}")
    print(f"\n  Result: {passed}/{total} tests passed")
    print("=" * 60)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
