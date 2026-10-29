import os


def save_artifacts(output_dir: str, artifacts: dict[str, dict[str, str]]):
    """
    Save generated artifacts to the output directory.

    Args:
        output_dir: Root output directory.
        artifacts: Nested dict  {category: {filename: content}}.
    """
    for category, files in artifacts.items():
        category_dir = os.path.join(output_dir, category)
        os.makedirs(category_dir, exist_ok=True)
        for filename, content in files.items():
            # Handle nested paths like ".github/workflows/ci-cd.yml"
            filepath = os.path.join(category_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)


def read_artifact(output_dir: str, category: str, filename: str) -> str:
    """Read a single artifact file."""
    filepath = os.path.join(output_dir, category, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def list_artifacts(output_dir: str) -> dict[str, list[str]]:
    """List all generated artifact files grouped by category."""
    result = {}
    if not os.path.exists(output_dir):
        return result
    for category in os.listdir(output_dir):
        cat_path = os.path.join(output_dir, category)
        if os.path.isdir(cat_path):
            files = []
            for root, _, filenames in os.walk(cat_path):
                for fn in filenames:
                    if fn == ".gitkeep":
                        continue
                    rel = os.path.relpath(os.path.join(root, fn), cat_path)
                    files.append(rel)
            if files:
                result[category] = sorted(files)
    return result
