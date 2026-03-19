"""Email sender with SMTP support, rate limiting, and dry-run mode."""

import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from .config import AppConfig


class EmailSender:
    """Sends emails via SMTP with built-in rate limiting."""

    def __init__(self, config: AppConfig, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self._connection: Optional[smtplib.SMTP] = None
        self._emails_sent_this_hour = 0
        self._hour_start = time.time()

    def connect(self):
        """Establish SMTP connection."""
        if self.dry_run:
            print("[DRY RUN] Skipping SMTP connection")
            return

        smtp = self.config.smtp
        self._connection = smtplib.SMTP(smtp.host, smtp.port)
        if smtp.use_tls:
            self._connection.starttls()
        self._connection.login(smtp.username, smtp.password)
        print(f"[OK] Connected to {smtp.host}:{smtp.port}")

    def disconnect(self):
        """Close SMTP connection."""
        if self._connection:
            self._connection.quit()
            self._connection = None
            print("[OK] SMTP connection closed")

    def _enforce_rate_limit(self):
        """Wait if we've hit the hourly send limit."""
        now = time.time()
        elapsed = now - self._hour_start

        # Reset counter each hour
        if elapsed >= 3600:
            self._emails_sent_this_hour = 0
            self._hour_start = now
            return

        if self._emails_sent_this_hour >= self.config.campaign.emails_per_hour:
            wait = 3600 - elapsed
            print(f"[RATE LIMIT] Hourly limit reached. Waiting {wait:.0f}s...")
            time.sleep(wait)
            self._emails_sent_this_hour = 0
            self._hour_start = time.time()

    def send(self, to_email: str, subject: str, body: str) -> bool:
        """Send a single email. Returns True on success."""
        self._enforce_rate_limit()

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self.config.sender.name} <{self.config.sender.email}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        if self.config.sender.reply_to:
            msg["Reply-To"] = self.config.sender.reply_to

        # Plain text body
        msg.attach(MIMEText(body, "plain"))

        if self.dry_run:
            print(f"\n[DRY RUN] Would send to: {to_email}")
            print(f"  Subject: {subject}")
            print(f"  Body preview: {body[:120]}...")
            self._emails_sent_this_hour += 1
            return True

        try:
            self._connection.sendmail(self.config.sender.email, to_email, msg.as_string())
            self._emails_sent_this_hour += 1
            print(f"[SENT] {to_email} — {subject}")

            # Delay between individual emails
            delay = self.config.campaign.delay_between_emails_sec
            if delay > 0:
                time.sleep(delay)
            return True
        except smtplib.SMTPException as e:
            print(f"[ERROR] Failed to send to {to_email}: {e}")
            return False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()
