import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from agents.prompts import BA_CONVERSATION_SYSTEM, BA_SPEC_EXTRACTION_PROMPT
from utils.parsers import parse_llm_json


class BAAgent:
    """
    Business Analyst Agent — dedicated agent for:
      1. Querying the database to understand available data
      2. Interactive spec-driven conversation with the user
      3. Extracting a structured JSON specification from the conversation
    """

    def __init__(self, model: str, api_key: str, temperature: float = 0.3):
        self.llm = ChatOpenAI(model=model, api_key=api_key, temperature=temperature)

    # ── Spec Conversation ──────────────────────────────────────────

    def conduct_conversation(
        self,
        user_message: str,
        chat_history: list[dict],
        guidelines_context: str,
        db_schema: str = "",
    ) -> str:
        """Return the next assistant message in the spec conversation."""
        print(f"\n🧑‍💼 [BA Agent] Processing user message ({len(user_message)} chars)")
        system = BA_CONVERSATION_SYSTEM.format(
            guidelines_context=guidelines_context,
            db_schema=db_schema,
        )
        messages = [SystemMessage(content=system)]

        for msg in chat_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=user_message))

        response = self.llm.invoke(messages)
        print(f"✅ [BA Agent] Response generated ({len(response.content)} chars)")
        return response.content

    # ── Spec Extraction ────────────────────────────────────────────

    def extract_spec(self, chat_history: list[dict], guidelines_context: str) -> dict:
        """Parse the conversation into a structured JSON specification."""
        print("\n🔍 [BA Agent] Extracting structured specification from conversation...")
        conversation_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in chat_history
        )
        prompt = BA_SPEC_EXTRACTION_PROMPT.format(
            conversation=conversation_text,
            guidelines=guidelines_context,
        )
        response = self.llm.invoke([HumanMessage(content=prompt)])
        result = parse_llm_json(response.content, self.llm)
        print(f"✅ [BA Agent] Spec extracted — {len(result)} top-level keys: {list(result.keys())}")
        return result
