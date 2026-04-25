"""Runtime settings, loaded from env via pydantic-settings.

Every setting has a default safe enough for a local test environment so
the test suite can `import app.main` without requiring real creds.
"""

from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_base_url: str = "http://localhost:8000"
    log_level: str = "INFO"

    database_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None

    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_voice_webhook_path: str = "/voice/incoming"
    twilio_sms_webhook_path: str = "/sms/incoming"
    twilio_messaging_service_sid: Optional[str] = None

    llm_provider: str = "fake"  # fake | http
    llm_model: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None

    stripe_secret_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    stripe_price_tier1: Optional[str] = None
    stripe_price_tier2: Optional[str] = None
    stripe_price_tier3: Optional[str] = None
    stripe_meter_booked_job: Optional[str] = None

    google_oauth_client_id: Optional[str] = None
    google_oauth_client_secret: Optional[str] = None
    google_oauth_redirect_uri: Optional[str] = None

    resend_api_key: Optional[str] = None
    resend_from: str = "ringback@example.test"

    skip_twilio_signature: bool = False  # tests only


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings_for_test() -> None:
    global _settings
    _settings = None
