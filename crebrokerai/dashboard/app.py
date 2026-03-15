"""CREBrokerAI Streamlit Dashboard.

Launch with:  streamlit run crebrokerai/dashboard/app.py
"""

from __future__ import annotations

import json
import datetime as dt
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy.orm import Session

from crebrokerai.config.database import SessionLocal, init_db
from crebrokerai.config.models import Prospect, Property, OutreachLog, CampaignRun
from crebrokerai.data.seed import seed_all
from crebrokerai.crews.campaign.crew import run_mock_campaign
from crebrokerai.utils.export import export_prospects_csv, export_outreach_csv

# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CREBrokerAI — Tenant Prospecting Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialise DB and seed on first load ─────────────────────────────────────

if "db_initialised" not in st.session_state:
    seed_all()
    st.session_state.db_initialised = True


def get_db() -> Session:
    return SessionLocal()


# ── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    .stMetric { background: #f8f9fa; border-radius: 8px; padding: 12px; }
    div[data-testid="stMetricValue"] { font-size: 2rem; }
    .hot-badge { background: #ff4b4b; color: white; padding: 2px 8px;
                 border-radius: 4px; font-weight: bold; }
    .warm-badge { background: #ffa726; color: white; padding: 2px 8px;
                  border-radius: 4px; font-weight: bold; }
    .cold-badge { background: #42a5f5; color: white; padding: 2px 8px;
                  border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image("https://placehold.co/280x60/1a1a2e/e94560?text=CREBrokerAI", width=280)
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "Dashboard Overview",
            "Prospect Pipeline",
            "Lead Scoring",
            "Property Matching",
            "Outreach Campaign",
            "Run Full Campaign",
            "Settings & Export",
        ],
        index=0,
    )

    st.markdown("---")
    st.caption("CREBrokerAI v1.0.0")
    st.caption(f"Session: {dt.datetime.now():%Y-%m-%d %H:%M}")

# ── Helper functions ─────────────────────────────────────────────────────────


def load_prospects(db: Session) -> pd.DataFrame:
    prospects = db.query(Prospect).all()
    if not prospects:
        return pd.DataFrame()
    return pd.DataFrame([{
        "ID": p.id,
        "Company": p.company_name,
        "Industry": p.industry,
        "Employees": p.employee_count,
        "City": p.hq_city,
        "State": p.hq_state,
        "Lease SqFt": p.current_lease_sqft,
        "Lease Expiry": p.lease_expiry,
        "Funding": p.funding_stage,
        "Funding ($M)": p.recent_funding_m,
        "Growth Signal": p.growth_signal,
        "Decision Maker": p.decision_maker_name,
        "Title": p.decision_maker_title,
        "Email": p.decision_maker_email,
        "Score": p.lead_score,
        "Tier": p.lead_tier or "unscored",
    } for p in prospects])


def load_properties(db: Session) -> pd.DataFrame:
    props = db.query(Property).all()
    if not props:
        return pd.DataFrame()
    return pd.DataFrame([{
        "ID": p.id,
        "Building": p.building_name,
        "Address": p.address,
        "City": p.city,
        "State": p.state,
        "Type": p.property_type,
        "Available SqFt": p.available_sqft,
        "Rent $/SF": p.asking_rent_psf,
        "Year Built": p.year_built,
        "Amenities": p.amenities,
        "Broker": p.broker_name,
    } for p in props])


# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

if page == "Dashboard Overview":
    st.title("CREBrokerAI — Dashboard")
    st.markdown("**Your AI-powered commercial real estate tenant prospecting platform.**")

    db = get_db()
    df_prospects = load_prospects(db)
    df_props = load_properties(db)

    # KPI row
    col1, col2, col3, col4, col5 = st.columns(5)
    total = len(df_prospects)
    hot = len(df_prospects[df_prospects["Tier"] == "hot"]) if not df_prospects.empty else 0
    warm = len(df_prospects[df_prospects["Tier"] == "warm"]) if not df_prospects.empty else 0
    props = len(df_props)
    campaigns = db.query(CampaignRun).count()

    col1.metric("Total Prospects", total)
    col2.metric("Hot Leads", hot)
    col3.metric("Warm Leads", warm)
    col4.metric("Properties", props)
    col5.metric("Campaigns", campaigns)

    # Charts
    if not df_prospects.empty:
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("Prospects by Industry")
            industry_counts = df_prospects["Industry"].value_counts().reset_index()
            industry_counts.columns = ["Industry", "Count"]
            fig = px.bar(industry_counts, x="Industry", y="Count",
                         color="Count", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.subheader("Lead Tier Distribution")
            tier_counts = df_prospects["Tier"].value_counts().reset_index()
            tier_counts.columns = ["Tier", "Count"]
            colors = {"hot": "#ff4b4b", "warm": "#ffa726", "cold": "#42a5f5", "unscored": "#9e9e9e"}
            fig = px.pie(tier_counts, values="Count", names="Tier",
                         color="Tier", color_discrete_map=colors)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Prospects by Market")
        market_counts = df_prospects["City"].value_counts().reset_index()
        market_counts.columns = ["City", "Count"]
        fig = px.bar(market_counts, x="City", y="Count", color="City")
        st.plotly_chart(fig, use_container_width=True)

    db.close()


elif page == "Prospect Pipeline":
    st.title("Prospect Pipeline")

    db = get_db()
    df = load_prospects(db)

    if df.empty:
        st.info("No prospects yet. Run a campaign to populate the pipeline.")
    else:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            industry_filter = st.multiselect("Industry", df["Industry"].unique())
        with col2:
            tier_filter = st.multiselect("Tier", df["Tier"].unique())
        with col3:
            city_filter = st.multiselect("City", df["City"].unique())

        filtered = df.copy()
        if industry_filter:
            filtered = filtered[filtered["Industry"].isin(industry_filter)]
        if tier_filter:
            filtered = filtered[filtered["Tier"].isin(tier_filter)]
        if city_filter:
            filtered = filtered[filtered["City"].isin(city_filter)]

        st.dataframe(
            filtered.sort_values("Score", ascending=False, na_position="last"),
            use_container_width=True,
            height=500,
        )

        st.download_button(
            "Download CSV",
            filtered.to_csv(index=False),
            "prospects.csv",
            "text/csv",
        )

    db.close()


elif page == "Lead Scoring":
    st.title("Lead Scoring & Analytics")

    db = get_db()
    df = load_prospects(db)

    if df.empty or df["Score"].isna().all():
        st.info("No scored leads yet. Run a campaign first.")
        if st.button("Run Mock Scoring"):
            with st.spinner("Scoring all prospects..."):
                run_mock_campaign()
            st.rerun()
    else:
        # Score distribution
        st.subheader("Score Distribution")
        fig = px.histogram(df.dropna(subset=["Score"]), x="Score", nbins=20,
                           color="Tier",
                           color_discrete_map={"hot": "#ff4b4b", "warm": "#ffa726",
                                               "cold": "#42a5f5", "unscored": "#9e9e9e"})
        st.plotly_chart(fig, use_container_width=True)

        # Score breakdown table
        st.subheader("Scored Prospects")
        scored = df.dropna(subset=["Score"]).sort_values("Score", ascending=False)
        st.dataframe(
            scored[["Company", "Industry", "City", "Score", "Tier",
                     "Lease Expiry", "Funding ($M)", "Growth Signal"]],
            use_container_width=True,
        )

        # Score vs Funding scatter
        st.subheader("Score vs. Recent Funding")
        fig = px.scatter(scored, x="Funding ($M)", y="Score", color="Tier",
                         size="Employees", hover_name="Company",
                         color_discrete_map={"hot": "#ff4b4b", "warm": "#ffa726",
                                             "cold": "#42a5f5"})
        st.plotly_chart(fig, use_container_width=True)

    db.close()


elif page == "Property Matching":
    st.title("Property Inventory & Matching")

    db = get_db()
    df_props = load_properties(db)
    df_prospects = load_prospects(db)

    if df_props.empty:
        st.info("No properties loaded yet.")
    else:
        st.subheader("Available Properties")
        st.dataframe(df_props, use_container_width=True)

        # Map-like view (rent by city)
        st.subheader("Asking Rent by Market")
        fig = px.bar(df_props, x="City", y="Rent $/SF", color="Type",
                     hover_name="Building", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

        # Quick match
        st.subheader("Quick Property Match")
        if not df_prospects.empty:
            company = st.selectbox("Select Prospect",
                                   df_prospects["Company"].tolist())
            if st.button("Find Matches"):
                from crebrokerai.tools.matching_tool import PropertyMatchingTool

                prospect_row = df_prospects[df_prospects["Company"] == company].iloc[0]
                tool = PropertyMatchingTool()
                result = json.loads(tool._run(json.dumps({
                    "company_name": prospect_row["Company"],
                    "industry": prospect_row["Industry"],
                    "city": prospect_row["City"],
                    "state": prospect_row["State"],
                    "current_lease_sqft": prospect_row["Lease SqFt"],
                    "employee_count": prospect_row["Employees"],
                })))
                for i, m in enumerate(result):
                    with st.expander(
                        f"#{i+1} {m['building_name']} — {m['match_score_pct']}% match"
                    ):
                        st.write(f"**City:** {m['city']}, {m['state']}")
                        st.write(f"**Available:** {m['available_sqft']:,} sqft")
                        st.write(f"**Rent:** ${m['asking_rent_psf']}/SF")
                        st.write(f"**Deal Value:** ${m['potential_deal_value']:,.0f}/yr")
                        st.write("**Reasons:**")
                        for r in m["match_reasons"]:
                            st.write(f"  - {r}")

    db.close()


elif page == "Outreach Campaign":
    st.title("Outreach Campaign Manager")
    st.markdown("""
    > **Compliance Notice:** All emails include CAN-SPAM compliant unsubscribe links
    > and physical addresses. All calls follow TCPA regulations with clear identification
    > and opt-out mechanisms. Human approval is required before sending.
    """)

    db = get_db()
    df = load_prospects(db)

    if df.empty or df["Score"].isna().all():
        st.info("Score prospects first before running outreach.")
    else:
        hot_leads = df[df["Tier"] == "hot"]
        warm_leads = df[df["Tier"] == "warm"]

        col1, col2 = st.columns(2)
        col1.metric("Hot Leads Ready", len(hot_leads))
        col2.metric("Warm Leads Ready", len(warm_leads))

        st.subheader("Outreach Queue")
        outreach_df = pd.concat([hot_leads, warm_leads]).sort_values("Score", ascending=False)
        st.dataframe(
            outreach_df[["Company", "Industry", "Score", "Tier", "Decision Maker", "Email"]],
            use_container_width=True,
        )

        st.subheader("Draft Email Preview")
        if not outreach_df.empty:
            selected = st.selectbox("Preview email for:",
                                    outreach_df["Company"].tolist())
            row = outreach_df[outreach_df["Company"] == selected].iloc[0]
            st.text_area(
                "Subject",
                f"Office space opportunity for {row['Company']} — {row['City']}",
                disabled=True,
            )
            st.text_area(
                "Body",
                f"""Hi {row['Decision Maker']},

I noticed {row['Company']} has been {row['Growth Signal'].lower() if row['Growth Signal'] else 'growing rapidly'}, and your current lease may be coming up for renewal.

I wanted to reach out because we have several properties in {row['City']} that could be a great fit for your team's needs — including modern Class-A space with the amenities growing {row['Industry']} companies love.

Would you be open to a quick 10-minute call this week to discuss your space requirements?

Best regards,
Your CRE Broker

---
To unsubscribe, reply STOP or visit: https://yourbrokerage.com/unsubscribe
CREBrokerAI | 123 Main St, Suite 100, Austin TX 78701
This message is a commercial advertisement.""",
                height=300,
                disabled=True,
            )

            st.warning("**Human Approval Required:** Emails will NOT be sent without your explicit approval.")
            if st.button("Approve & Send (Mock)", type="primary"):
                st.success(f"Mock email sent to {row['Email']} for {row['Company']}")

    db.close()


elif page == "Run Full Campaign":
    st.title("Run Full Campaign")
    st.markdown("Launch the complete AI-powered tenant prospecting pipeline.")

    with st.form("campaign_form"):
        campaign_name = st.text_input("Campaign Name", "My Campaign")
        col1, col2 = st.columns(2)
        with col1:
            markets = st.multiselect(
                "Target Markets",
                ["Austin", "San Diego", "Dallas", "Miami", "Denver",
                 "Phoenix", "Los Angeles", "Pittsburgh", "Portland", "Chicago"],
                default=["Austin", "Miami", "Denver"],
            )
        with col2:
            industries = st.multiselect(
                "Target Industries",
                ["SaaS / Technology", "Biotech / Life Sciences",
                 "Logistics / Supply Chain", "Financial Services",
                 "Healthcare / MedTech", "Advertising / Creative",
                 "Robotics / Manufacturing", "CleanTech / Energy",
                 "Data Analytics / AI", "Legal Tech"],
                default=["SaaS / Technology", "Biotech / Life Sciences",
                          "Financial Services"],
            )

        st.markdown("---")
        st.markdown("**Upload Building List** (optional CSV)")
        uploaded = st.file_uploader("Upload your property list", type=["csv"])

        submitted = st.form_submit_button("Run Campaign", type="primary")

    if submitted:
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(stage: str, pct: int, msg: str):
            progress_bar.progress(pct / 100)
            status_text.markdown(f"**[{stage.upper()}]** {msg}")

        with st.spinner("Running campaign..."):
            result = run_mock_campaign(
                campaign_name=campaign_name,
                target_markets=markets,
                target_industries=industries,
            )

        progress_bar.progress(100)
        status_text.markdown("**Campaign Complete!**")

        st.success(f"Campaign '{campaign_name}' finished successfully!")

        # Results summary
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Prospects Found", result.get("total_prospects", 0))
        col2.metric("Hot Leads", result.get("hot_leads", 0))
        col3.metric("Warm Leads", result.get("warm_leads", 0))
        col4.metric("Properties", result.get("total_properties", 0))

        # Scored prospects
        st.subheader("Scored Prospects")
        scored_df = pd.DataFrame(result.get("scored_prospects", []))
        if not scored_df.empty:
            st.dataframe(scored_df, use_container_width=True)

        # Property matches
        st.subheader("Top Property Matches")
        match_df = pd.DataFrame(result.get("property_matches", []))
        if not match_df.empty:
            st.dataframe(match_df, use_container_width=True)

        st.info(result.get("message", ""))


elif page == "Settings & Export":
    st.title("Settings & Data Export")

    db = get_db()

    st.subheader("Export Data")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Export Prospects CSV"):
            path = export_prospects_csv(db)
            st.success(f"Exported to {path}")
    with col2:
        if st.button("Export Outreach Log CSV"):
            path = export_outreach_csv(db)
            st.success(f"Exported to {path}")

    st.subheader("API Keys Configuration")
    st.markdown("""
    Configure your API keys in the `.env` file at the project root:

    ```
    ANTHROPIC_API_KEY=sk-ant-...
    SERPER_API_KEY=...
    SENDGRID_API_KEY=...
    TWILIO_ACCOUNT_SID=...
    TWILIO_AUTH_TOKEN=...
    ```

    The platform runs in **mock mode** when no keys are configured.
    """)

    from crebrokerai.config.settings import settings

    st.subheader("Current Configuration")
    st.json({
        "LLM Provider": settings.llm_provider,
        "LLM Model": settings.llm_model,
        "Mock Mode": settings.mock_mode,
        "Database": settings.database_url,
        "SendGrid Configured": bool(settings.sendgrid_api_key),
        "Twilio Configured": bool(settings.twilio_account_sid),
        "Serper Configured": bool(settings.serper_api_key),
    })

    st.subheader("Database Stats")
    st.json({
        "Prospects": db.query(Prospect).count(),
        "Properties": db.query(Property).count(),
        "Outreach Logs": db.query(OutreachLog).count(),
        "Campaign Runs": db.query(CampaignRun).count(),
    })

    db.close()
