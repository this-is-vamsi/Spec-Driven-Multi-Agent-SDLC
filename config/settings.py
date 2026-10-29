import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_REPO_OWNER: str = os.getenv("GITHUB_REPO_OWNER", "")
    GITHUB_REPO_NAME: str = os.getenv("GITHUB_REPO_NAME", "")
    GITHUB_BASE_BRANCH: str = os.getenv("GITHUB_BASE_BRANCH", "main")

    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")

    APP_NAME: str = os.getenv("APP_NAME", "AI-SDLC Accelerator")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")
    GUIDELINES_PATH: str = os.getenv("GUIDELINES_PATH", "guideline.txt")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "database/sdlc.db")


def get_settings() -> Settings:
    return Settings()
