"""Load model and data settings from the process environment or local .env."""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    openai_base_url: str
    model: str
    openai_api_key: str
    data_base_url: str


def load_config() -> Config:
    """Load settings, with process environment variables taking precedence."""
    load_dotenv(REPOSITORY_ROOT / ".env", override=False)

    names = {
        "OPENAI_BASE_URL": "openai_base_url",
        "MODEL": "model",
        "OPENAI_API_KEY": "openai_api_key",
        "DATA_BASE_URL": "data_base_url",
    }
    values = {field: os.getenv(name, "").strip() for name, field in names.items()}
    missing = [name for name, field in names.items() if not values[field]]
    if missing:
        raise RuntimeError(
            "Missing configuration: " + ", ".join(missing)
            + ". Set them in the process environment or local .env file."
        )

    return Config(
        openai_base_url=values["openai_base_url"].rstrip("/"),
        model=values["model"],
        openai_api_key=values["openai_api_key"],
        data_base_url=values["data_base_url"].rstrip("/"),
    )
