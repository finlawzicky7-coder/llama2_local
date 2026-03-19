"""Campaign orchestrator — tracks state and runs multi-stage email sequences."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .config import AppConfig
from .prospects import Prospect, load_prospects, filter_prospects
from .sender import EmailSender
from .templates.email_templates import STAGE_SEQUENCE, render_template


class CampaignLog:
    """Persistent log of all emails sent, stored as JSON."""

    def __init__(self, log_path: str):
        self.log_path = log_path
        self.entries: List[Dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.log_path):
            with open(self.log_path, "r") as f:
                self.entries = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, "w") as f:
            json.dump(self.entries, f, indent=2, default=str)

    def record(self, email: str, stage: int, template_key: str, success: bool):
        self.entries.append(
            {
                "email": email,
                "stage": stage,
                "template": template_key,
                "success": success,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.save()

    def get_stage(self, email: str) -> int:
        """Return the current stage for a prospect (0 = never contacted)."""
        stages = [e["stage"] for e in self.entries if e["email"] == email and e["success"]]
        return max(stages) if stages else 0

    def last_sent(self, email: str) -> Optional[datetime]:
        """Return the datetime of the last successful send to this email."""
        timestamps = [
            e["timestamp"]
            for e in self.entries
            if e["email"] == email and e["success"]
        ]
        if not timestamps:
            return None
        return datetime.fromisoformat(max(timestamps))

    def contacted_emails(self) -> set:
        """Return set of all emails that have been contacted at least once."""
        return {e["email"] for e in self.entries if e["success"]}

    def summary(self) -> Dict:
        """Return campaign statistics."""
        total = len(self.entries)
        successful = sum(1 for e in self.entries if e["success"])
        unique = len(self.contacted_emails())
        by_stage = {}
        for e in self.entries:
            key = e["template"]
            by_stage[key] = by_stage.get(key, 0) + 1
        return {
            "total_sent": total,
            "successful": successful,
            "failed": total - successful,
            "unique_prospects": unique,
            "by_template": by_stage,
        }


class Campaign:
    """Runs a multi-stage cold email campaign."""

    def __init__(self, config: AppConfig, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.log = CampaignLog(config.campaign_log)

    def run_initial_outreach(
        self,
        template_key: str = "initial_intro",
        industry: Optional[str] = None,
        limit: Optional[int] = None,
    ):
        """Send first-touch emails to new prospects."""
        prospects = load_prospects(self.config.prospects_csv)
        already_contacted = self.log.contacted_emails()
        prospects = filter_prospects(
            prospects, industry=industry, exclude_emails=already_contacted
        )

        if limit:
            prospects = prospects[:limit]

        if not prospects:
            print("[INFO] No new prospects to contact.")
            return

        print(f"[CAMPAIGN] Sending initial outreach to {len(prospects)} prospects...")

        with EmailSender(self.config, dry_run=self.dry_run) as sender:
            for prospect in prospects:
                rendered = render_template(
                    template_key,
                    first_name=prospect.first_name,
                    company=prospect.company,
                    industry=prospect.industry,
                    pain_point=prospect.pain_point,
                    sender_name=self.config.sender.name,
                )
                success = sender.send(prospect.email, rendered["subject"], rendered["body"])
                self.log.record(prospect.email, 1, template_key, success)

        print("[CAMPAIGN] Initial outreach complete.")

    def run_follow_ups(self):
        """Send follow-up emails to prospects who haven't responded."""
        prospects = load_prospects(self.config.prospects_csv)
        now = datetime.utcnow()
        delay = timedelta(days=self.config.campaign.follow_up_delay_days)

        follow_up_queue = []
        for prospect in prospects:
            current_stage = self.log.get_stage(prospect.email)
            if current_stage == 0 or current_stage >= len(STAGE_SEQUENCE):
                continue  # Not contacted yet, or campaign complete

            last = self.log.last_sent(prospect.email)
            if last and (now - last) < delay:
                continue  # Too soon for follow-up

            next_stage = current_stage + 1
            if next_stage > len(STAGE_SEQUENCE):
                continue

            template_key = STAGE_SEQUENCE[next_stage - 1]
            follow_up_queue.append((prospect, next_stage, template_key))

        if not follow_up_queue:
            print("[INFO] No follow-ups due at this time.")
            return

        print(f"[CAMPAIGN] Sending {len(follow_up_queue)} follow-ups...")

        with EmailSender(self.config, dry_run=self.dry_run) as sender:
            for prospect, stage, template_key in follow_up_queue:
                rendered = render_template(
                    template_key,
                    first_name=prospect.first_name,
                    company=prospect.company,
                    industry=prospect.industry,
                    pain_point=prospect.pain_point,
                    sender_name=self.config.sender.name,
                )
                success = sender.send(prospect.email, rendered["subject"], rendered["body"])
                self.log.record(prospect.email, stage, template_key, success)

        print("[CAMPAIGN] Follow-ups complete.")

    def show_status(self):
        """Print campaign status summary."""
        stats = self.log.summary()
        print("\n═══ Anubis AI Campaign Status ═══")
        print(f"  Total emails sent:  {stats['total_sent']}")
        print(f"  Successful:         {stats['successful']}")
        print(f"  Failed:             {stats['failed']}")
        print(f"  Unique prospects:   {stats['unique_prospects']}")
        print(f"  By template:")
        for tpl, count in stats.get("by_template", {}).items():
            print(f"    {tpl}: {count}")
        print("═════════════════════════════════\n")
