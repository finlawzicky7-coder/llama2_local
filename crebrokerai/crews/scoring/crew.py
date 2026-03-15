"""Predictive Lead Scoring Crew.

Scores prospects 1-100 and assigns hot/warm/cold tiers.
"""

from __future__ import annotations

from pathlib import Path

from crewai import Agent, Crew, Process, Task

from crebrokerai.tools.scoring_tool import LeadScoringTool
from crebrokerai.utils.logging import get_logger

log = get_logger("crews.scoring")

YAML_DIR = Path(__file__).resolve().parent


def _load_yaml(name: str) -> dict:
    import yaml

    return yaml.safe_load((YAML_DIR / name).read_text())


class ScoringCrew:
    """Two-agent crew: market analyst + lead scorer."""

    def __init__(self, prospect_data: str, target_markets: list[str]):
        self.prospect_data = prospect_data
        self.target_markets = target_markets
        self.agents_cfg = _load_yaml("agents.yaml")
        self.tasks_cfg = _load_yaml("tasks.yaml")

    def build_crew(self) -> Crew:
        a_cfg = self.agents_cfg
        t_cfg = self.tasks_cfg

        market_analyst = Agent(
            role=a_cfg["market_analyst"]["role"],
            goal=a_cfg["market_analyst"]["goal"],
            backstory=a_cfg["market_analyst"]["backstory"],
            verbose=True,
        )

        lead_scorer = Agent(
            role=a_cfg["lead_scorer"]["role"],
            goal=a_cfg["lead_scorer"]["goal"],
            backstory=a_cfg["lead_scorer"]["backstory"],
            tools=[LeadScoringTool()],
            verbose=True,
        )

        markets_str = ", ".join(self.target_markets)

        market_task = Task(
            description=t_cfg["analyze_market_conditions"]["description"].format(
                target_markets=markets_str
            ),
            expected_output=t_cfg["analyze_market_conditions"]["expected_output"],
            agent=market_analyst,
        )

        scoring_task = Task(
            description=t_cfg["score_leads"]["description"],
            expected_output=t_cfg["score_leads"]["expected_output"],
            agent=lead_scorer,
            context=[market_task],
        )

        return Crew(
            agents=[market_analyst, lead_scorer],
            tasks=[market_task, scoring_task],
            process=Process.sequential,
            verbose=True,
        )

    def run(self) -> str:
        log.info("Starting Scoring Crew")
        crew = self.build_crew()
        result = crew.kickoff()
        log.info("Scoring Crew completed")
        return str(result)
