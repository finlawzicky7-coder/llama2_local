"""AI-Powered Outbound Outreach & Qualification Crew.

Drafts personalised emails, prepares call scripts, and coordinates
multi-channel outreach with CAN-SPAM / TCPA compliance.
"""

from __future__ import annotations

import json
from pathlib import Path

from crewai import Agent, Crew, Process, Task

from crebrokerai.tools.email_tool import SendGridEmailTool
from crebrokerai.tools.voice_tool import TwilioVoiceCallTool
from crebrokerai.utils.logging import get_logger

log = get_logger("crews.outreach")

YAML_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load_yaml(name: str) -> dict:
    import yaml

    return yaml.safe_load((YAML_DIR / name).read_text())


class OutreachCrew:
    """Three-agent crew: copywriter + call qualifier + coordinator."""

    def __init__(self, prospect_data: str, property_data: str | None = None):
        self.prospect_data = prospect_data
        if property_data:
            self.property_data = property_data
        else:
            self.property_data = (DATA_DIR / "mock_properties.json").read_text()
        self.agents_cfg = _load_yaml("agents.yaml")
        self.tasks_cfg = _load_yaml("tasks.yaml")

    def build_crew(self) -> Crew:
        a_cfg = self.agents_cfg
        t_cfg = self.tasks_cfg

        copywriter = Agent(
            role=a_cfg["email_copywriter"]["role"],
            goal=a_cfg["email_copywriter"]["goal"],
            backstory=a_cfg["email_copywriter"]["backstory"],
            tools=[SendGridEmailTool()],
            verbose=True,
        )

        caller = Agent(
            role=a_cfg["call_qualifier"]["role"],
            goal=a_cfg["call_qualifier"]["goal"],
            backstory=a_cfg["call_qualifier"]["backstory"],
            tools=[TwilioVoiceCallTool()],
            verbose=True,
        )

        coordinator = Agent(
            role=a_cfg["outreach_coordinator"]["role"],
            goal=a_cfg["outreach_coordinator"]["goal"],
            backstory=a_cfg["outreach_coordinator"]["backstory"],
            verbose=True,
        )

        email_task = Task(
            description=t_cfg["draft_outreach_emails"]["description"].format(
                prospect_data=self.prospect_data[:2000],
                property_data=self.property_data[:2000],
            ),
            expected_output=t_cfg["draft_outreach_emails"]["expected_output"],
            agent=copywriter,
        )

        call_task = Task(
            description=t_cfg["prepare_call_scripts"]["description"].format(
                prospect_data=self.prospect_data[:2000],
            ),
            expected_output=t_cfg["prepare_call_scripts"]["expected_output"],
            agent=caller,
        )

        coord_task = Task(
            description=t_cfg["coordinate_outreach"]["description"].format(
                email_drafts="(from email task)",
                call_scripts="(from call task)",
            ),
            expected_output=t_cfg["coordinate_outreach"]["expected_output"],
            agent=coordinator,
            context=[email_task, call_task],
        )

        return Crew(
            agents=[copywriter, caller, coordinator],
            tasks=[email_task, call_task, coord_task],
            process=Process.sequential,
            verbose=True,
        )

    def run(self) -> str:
        log.info("Starting Outreach Crew")
        crew = self.build_crew()
        result = crew.kickoff()
        log.info("Outreach Crew completed")
        return str(result)
