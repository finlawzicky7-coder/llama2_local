"""CLI entry point for CREBrokerAI.

Usage:
    crebrokerai run              — Run a mock campaign (no API keys needed)
    crebrokerai run --full       — Run full LLM-powered campaign (needs keys)
    crebrokerai dashboard        — Launch Streamlit dashboard
    crebrokerai api              — Launch FastAPI server
    crebrokerai seed             — Seed the database with mock data
    crebrokerai export           — Export prospects & outreach to CSV
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="crebrokerai",
    help="CREBrokerAI — AI-powered Commercial Real Estate Tenant Prospecting Platform",
    no_args_is_help=True,
)
console = Console()


@app.command()
def run(
    full: bool = typer.Option(False, "--full", "-f", help="Run full LLM campaign (requires API keys)"),
    name: str = typer.Option("CLI Campaign", "--name", "-n", help="Campaign name"),
    markets: Optional[str] = typer.Option(
        "Austin,Miami,Denver", "--markets", "-m",
        help="Comma-separated target markets",
    ),
    industries: Optional[str] = typer.Option(
        "Technology,Biotech,Financial Services", "--industries", "-i",
        help="Comma-separated target industries",
    ),
):
    """Run a tenant prospecting campaign."""
    market_list = [m.strip() for m in markets.split(",")]
    industry_list = [i.strip() for i in industries.split(",")]

    console.print(f"\n[bold blue]CREBrokerAI[/] — Campaign: {name}")
    console.print(f"  Markets: {', '.join(market_list)}")
    console.print(f"  Industries: {', '.join(industry_list)}")
    console.print(f"  Mode: {'Full LLM' if full else 'Mock (no API keys)'}\n")

    if full:
        from crebrokerai.crews.campaign.crew import CampaignCrew

        campaign = CampaignCrew(
            campaign_name=name,
            target_markets=market_list,
            target_industries=industry_list,
        )
        result = campaign.run()
    else:
        from crebrokerai.crews.campaign.crew import run_mock_campaign

        result = run_mock_campaign(
            campaign_name=name,
            target_markets=market_list,
            target_industries=industry_list,
        )

    # Display results
    console.print("\n[bold green]Campaign Results[/]\n")

    table = Table(title="Scored Prospects")
    table.add_column("Company", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Tier", style="bold")

    for p in result.get("scored_prospects", []):
        tier = p.get("lead_tier", "")
        tier_style = {"hot": "red", "warm": "yellow", "cold": "blue"}.get(tier, "white")
        table.add_row(
            p["company_name"],
            str(p["lead_score"]),
            f"[{tier_style}]{tier.upper()}[/{tier_style}]",
        )
    console.print(table)

    if result.get("property_matches"):
        console.print("\n")
        match_table = Table(title="Top Property Matches")
        match_table.add_column("Prospect", style="cyan")
        match_table.add_column("Tier")
        match_table.add_column("Best Match", style="green")
        match_table.add_column("Match %", justify="right")

        for m in result["property_matches"]:
            match_table.add_row(
                m["prospect"], m["tier"].upper(),
                m["top_match"], f"{m['match_score']}%",
            )
        console.print(match_table)

    console.print(f"\n[bold]{result.get('message', 'Done!')}[/]\n")


@app.command()
def dashboard():
    """Launch the Streamlit dashboard."""
    import subprocess
    import sys

    console.print("[bold blue]Launching CREBrokerAI Dashboard...[/]")
    dashboard_path = str(
        __import__("pathlib").Path(__file__).resolve().parent / "dashboard" / "app.py"
    )
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])


@app.command()
def api(
    port: int = typer.Option(8000, "--port", "-p", help="API port"),
):
    """Launch the FastAPI server."""
    import uvicorn

    console.print(f"[bold blue]Starting CREBrokerAI API on port {port}...[/]")
    uvicorn.run("crebrokerai.api.server:app", host="0.0.0.0", port=port, reload=True)


@app.command()
def seed():
    """Seed the database with mock data."""
    from crebrokerai.data.seed import seed_all

    result = seed_all()
    console.print(f"[green]Database seeded:[/] {result}")


@app.command()
def export():
    """Export prospects and outreach data to CSV."""
    from crebrokerai.config.database import SessionLocal
    from crebrokerai.utils.export import export_prospects_csv, export_outreach_csv

    db = SessionLocal()
    try:
        p_path = export_prospects_csv(db)
        o_path = export_outreach_csv(db)
        console.print(f"[green]Prospects exported to:[/] {p_path}")
        console.print(f"[green]Outreach exported to:[/] {o_path}")
    finally:
        db.close()


if __name__ == "__main__":
    app()
