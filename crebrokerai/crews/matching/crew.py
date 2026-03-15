"""Property Matching & Marketing Crew.

Matches prospects to available properties and generates marketing collateral.
"""

from __future__ import annotations

import json
from pathlib import Path

from crewai import Agent, Crew, Process, Task

from crebrokerai.tools.matching_tool import PropertyMatchingTool
from crebrokerai.utils.logging import get_logger

log = get_logger("crews.matching")

YAML_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load_yaml(name: str) -> dict:
    import yaml

    return yaml.safe_load((YAML_DIR / name).read_text())


class MatchingCrew:
    """Two-agent crew: property matcher + marketing creator."""

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

        matcher = Agent(
            role=a_cfg["property_matcher"]["role"],
            goal=a_cfg["property_matcher"]["goal"],
            backstory=a_cfg["property_matcher"]["backstory"],
            tools=[PropertyMatchingTool()],
            verbose=True,
        )

        marketer = Agent(
            role=a_cfg["marketing_creator"]["role"],
            goal=a_cfg["marketing_creator"]["goal"],
            backstory=a_cfg["marketing_creator"]["backstory"],
            verbose=True,
        )

        match_task = Task(
            description=t_cfg["match_properties"]["description"].format(
                prospect_data=self.prospect_data[:2000],
                property_data=self.property_data[:2000],
            ),
            expected_output=t_cfg["match_properties"]["expected_output"],
            agent=matcher,
        )

        marketing_task = Task(
            description=t_cfg["create_marketing_materials"]["description"].format(
                match_results="(from previous task)",
                property_data=self.property_data[:2000],
                prospect_data=self.prospect_data[:2000],
            ),
            expected_output=t_cfg["create_marketing_materials"]["expected_output"],
            agent=marketer,
            context=[match_task],
        )

        return Crew(
            agents=[matcher, marketer],
            tasks=[match_task, marketing_task],
            process=Process.sequential,
            verbose=True,
        )

    def run(self) -> str:
        log.info("Starting Matching Crew")
        crew = self.build_crew()
        result = crew.kickoff()
        log.info("Matching Crew completed")
        return str(result)
