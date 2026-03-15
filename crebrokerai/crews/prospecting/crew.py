"""Tenant Prospecting & Research Crew.

Discovers companies with expiring leases and growth signals, then builds
rich prospect profiles ready for scoring and outreach.
"""

from __future__ import annotations

import json
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.tools import BaseTool

from crebrokerai.config.settings import settings
from crebrokerai.tools.cre_data import CRELeaseSearchTool, CRECompanyResearchTool
from crebrokerai.utils.logging import get_logger

log = get_logger("crews.prospecting")

YAML_DIR = Path(__file__).resolve().parent


def _load_yaml(name: str) -> dict:
    import yaml

    return yaml.safe_load((YAML_DIR / name).read_text())


class ProspectingCrew:
    """Orchestrates the three-agent prospecting pipeline."""

    def __init__(self, target_markets: list[str], target_industries: list[str]):
        self.target_markets = target_markets
        self.target_industries = target_industries
        self.agents_cfg = _load_yaml("agents.yaml")
        self.tasks_cfg = _load_yaml("tasks.yaml")

    def _make_agent(self, key: str, tools: list[BaseTool] | None = None) -> Agent:
        cfg = self.agents_cfg[key]
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            tools=tools or [],
            verbose=True,
        )

    def build_crew(self) -> Crew:
        # ── Agents ───────────────────────────────────────────
        lease_scanner = self._make_agent("lease_scanner", [CRELeaseSearchTool()])
        growth_analyst = self._make_agent("growth_signal_analyst", [CRECompanyResearchTool()])
        profiler = self._make_agent(
            "prospect_profiler", [CRECompanyResearchTool()]
        )

        markets_str = ", ".join(self.target_markets)
        industries_str = ", ".join(self.target_industries)

        # ── Tasks ────────────────────────────────────────────
        t_cfg = self.tasks_cfg

        scan_task = Task(
            description=t_cfg["scan_lease_expirations"]["description"].format(
                target_markets=markets_str, target_industries=industries_str
            ),
            expected_output=t_cfg["scan_lease_expirations"]["expected_output"],
            agent=lease_scanner,
        )

        growth_task = Task(
            description=t_cfg["analyze_growth_signals"]["description"],
            expected_output=t_cfg["analyze_growth_signals"]["expected_output"],
            agent=growth_analyst,
            context=[scan_task],
        )

        profile_task = Task(
            description=t_cfg["build_prospect_profiles"]["description"],
            expected_output=t_cfg["build_prospect_profiles"]["expected_output"],
            agent=profiler,
            context=[growth_task],
        )

        crew = Crew(
            agents=[lease_scanner, growth_analyst, profiler],
            tasks=[scan_task, growth_task, profile_task],
            process=Process.sequential,
            verbose=True,
        )
        return crew

    def run(self) -> str:
        log.info("Starting Prospecting Crew — markets=%s, industries=%s",
                 self.target_markets, self.target_industries)
        crew = self.build_crew()
        result = crew.kickoff()
        log.info("Prospecting Crew completed")
        return str(result)
