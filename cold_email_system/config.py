"""Configuration for the Anubis AI cold email system."""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SMTPConfig:
    host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port: int = int(os.getenv("SMTP_PORT", "587"))
    username: str = os.getenv("SMTP_USERNAME", "")
    password: str = os.getenv("SMTP_PASSWORD", "")
    use_tls: bool = True


@dataclass
class SenderConfig:
    name: str = os.getenv("SENDER_NAME", "Anubis AI Team")
    email: str = os.getenv("SENDER_EMAIL", "")
    reply_to: Optional[str] = os.getenv("SENDER_REPLY_TO", None)


@dataclass
class CampaignConfig:
    emails_per_hour: int = int(os.getenv("EMAILS_PER_HOUR", "30"))
    delay_between_emails_sec: int = int(os.getenv("DELAY_BETWEEN_EMAILS", "120"))
    follow_up_delay_days: int = int(os.getenv("FOLLOW_UP_DELAY_DAYS", "3"))
    max_follow_ups: int = int(os.getenv("MAX_FOLLOW_UPS", "2"))
    track_opens: bool = False


@dataclass
class AppConfig:
    smtp: SMTPConfig = field(default_factory=SMTPConfig)
    sender: SenderConfig = field(default_factory=SenderConfig)
    campaign: CampaignConfig = field(default_factory=CampaignConfig)
    prospects_csv: str = os.getenv(
        "PROSPECTS_CSV", "cold_email_system/data/prospects.csv"
    )
    campaign_log: str = os.getenv(
        "CAMPAIGN_LOG", "cold_email_system/data/campaign_log.json"
    )
