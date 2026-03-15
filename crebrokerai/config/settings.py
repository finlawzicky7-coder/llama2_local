"""Centralised application settings loaded from environment / .env file."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM ───────────────────────────────────────────────────
    llm_provider: Literal["anthropic", "openai", "groq"] = "anthropic"
    llm_model: str = "claude-sonnet-4-20250514"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    groq_api_key: str = ""

    # ── Web Search ────────────────────────────────────────────
    serper_api_key: str = ""

    # ── SendGrid ──────────────────────────────────────────────
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "broker@yourbrokerage.com"
    sendgrid_from_name: str = "Your Brokerage"

    # ── Twilio ────────────────────────────────────────────────
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""

    # ── Database ──────────────────────────────────────────────
    database_url: str = "sqlite:///./crebrokerai.db"

    # ── Ports ─────────────────────────────────────────────────
    streamlit_port: int = 8501
    api_port: int = 8000

    # ── Paths ─────────────────────────────────────────────────
    data_dir: Path = Path(__file__).resolve().parent.parent / "data"
    export_dir: Path = Path("./exports")

    @property
    def mock_mode(self) -> bool:
        """Return True when no real API keys are configured."""
        return not self.anthropic_api_key and not self.openai_api_key

    def get_llm_config(self) -> dict:
        """Return CrewAI-compatible LLM configuration."""
        if self.llm_provider == "anthropic":
            return {
                "provider": "anthropic",
                "config": {
                    "model": self.llm_model,
                    "api_key": self.anthropic_api_key,
                },
            }
        if self.llm_provider == "openai":
            return {
                "provider": "openai",
                "config": {
                    "model": self.llm_model,
                    "api_key": self.openai_api_key,
                },
            }
        return {
            "provider": "groq",
            "config": {
                "model": self.llm_model,
                "api_key": self.groq_api_key,
            },
        }


settings = Settings()
