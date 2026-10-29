import json
import re
from langchain_core.output_parsers import JsonOutputParser


def parse_llm_json(raw: str, llm) -> dict:
    """
    Parse JSON from an LLM response with automatic repair on failure.

    1. Strips markdown code fences.
    2. Tries standard json.loads first (fast path).
    3. Falls back to JsonOutputParser.
    4. If both fail, asks the LLM to fix the broken JSON and retries.
    """
    text = raw.strip()

    # Strip markdown code fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)

    # Fast path
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("⚠️  [Parser] Direct JSON parse failed — trying LangChain parser...")

    # Try LangChain parser (handles some edge cases)
    parser = JsonOutputParser()
    try:
        return parser.parse(text)
    except Exception:
        pass

    # Ask the LLM to fix the broken JSON
    print("⚠️  [Parser] LangChain parser also failed — asking LLM to repair JSON...")
    from langchain_core.messages import HumanMessage

    fix_prompt = (
        "The following text was supposed to be valid JSON but is malformed. "
        "Return ONLY the corrected JSON with no explanation or markdown:\n\n"
        + raw
    )
    response = llm.invoke([HumanMessage(content=fix_prompt)])
    fixed = response.content.strip()
    if fixed.startswith("```"):
        fixed = re.sub(r"^```(?:json)?\s*\n?", "", fixed)
        fixed = re.sub(r"\n?```\s*$", "", fixed)
    return json.loads(fixed)
