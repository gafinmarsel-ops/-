from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import Client, create_client

st.set_page_config(
    page_title="Student Commute Survey",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COLORS = {
    "plum": "#6D3B72",
    "orange": "#E58A42",
    "ink": "#302A31",
    "paper": "#FBF6EF",
    "card": "#FFFDF9",
}

st.markdown(
    """
    <style>
    .stApp { background: #fbf6ef; color: #302a31; }
    .block-container { max-width: 1120px; padding-top: 2rem; padding-bottom: 3rem; }
    .hero {
        background: linear-gradient(125deg, #45254b 0%, #805087 72%, #b46b61 100%);
        padding: 2rem; border-radius: 22px; color: #fffaf6; margin-bottom: 1.2rem;
    }
    .hero h1 { color: #fffaf6; font-size: 2.25rem; margin: 0 0 .45rem 0; }
    .hero p { color: #f8eaf4; margin: 0; font-size: 1.03rem; }
    div[data-testid="stForm"] {
        background: #fffdf9; border: 1px solid #eadbd0;
        padding: 1.25rem 1.35rem; border-radius: 18px;
    }
    div[data-testid="stMetric"] {
        background: #fffdf9; border: 1px solid #eadbd0;
        padding: 1rem; border-radius: 14px;
    }
    .stButton button[kind="primary"],
    div[data-testid="stFormSubmitButton"] button {
        background: #6d3b72; border-color: #6d3b72; border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
      <h1>🚌 Student Commute Survey</h1>
      <p>Understanding how students travel to campus and what makes a commute better.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.write(
    "This short survey explores students' travel choices, commute times, daily "
    "transport costs, and satisfaction. Participation is voluntary and takes "
    "about 2–3 minutes. Please do not include your name or contact details."
)
st.caption("Student research project · Voluntary participation · No account required")


@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"].rstrip("/")
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


@st.cache_data(ttl=30, show_spinner=False)
def load_stats() -> dict:
    result = get_supabase().rpc("get_survey_stats").execute()
    data = result.data
    if isinstance(data, list):
        data = data[0] if data else {}
    return data if isinstance(data, dict) else {}


try:
    supabase = get_supabase()
    database_ready = True
except Exception:
    supabase = None
    database_ready = False

if database_ready:
    st.success("Database connected. Submitted responses are stored securely.")
else:
    st.warning(
        "The survey database is not configured yet. The form is visible, "
        "but responses cannot be submitted until the app secrets are set."
    )

with st.form("commute_survey"):
    st.subheader("About your commute")
    left, right = st.columns(2)

    with left:
        age = st.number_input("Your age", min_value=14, max_value=80, value=19, step=1)
        study_year = st.selectbox(
            "Your year of study",
            ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5 or above", "Not currently studying"],
        )
        transport = st.radio(
            "How do you usually travel to your place of study?",
            [
                "Bus / trolleybus / tram",
                "Metro",
                "Walking",
                "Private car",
                "Taxi / car sharing",
                "Bicycle / scooter",
                "Other",
            ],
        )
        duration = st.selectbox(
            "How long is your one-way commute?",
            ["Up to 15 minutes", "15–30 minutes", "31–45 minutes", "46–60 minutes", "More than 1 hour"],
        )

    with right:
        daily_cost = st.selectbox(
            "How much do you spend on transport per study day?",
            ["Nothing", "Up to 100 RUB", "101–200 RUB", "201–350 RUB", "More than 350 RUB", "Not sure"],
        )
        satisfaction = st.slider(
            "How satisfied are you with your usual way of travelling?",
            min_value=1,
            max_value=10,
            value=7,
            help="1 = very dissatisfied · 10 = very satisfied",
        )
        lateness = st.selectbox(
            "How often are you late because of your commute?",
            [
                "Never or almost never",
                "A few times per semester",
                "1–3 times per month",
                "About once a week",
                "Several times a week",
            ],
        )
        planning = st.radio(
            "Do you check your route or timetable in advance?",
            ["Always", "Often", "Sometimes", "Rarely", "Never"],
        )

    factors = st.multiselect(
        "What matters most when choosing transport?",
        [
            "Cost",
            "Travel time",
            "Comfort",
            "Nearby stops",
            "Timetable",
            "Weather",
            "Number of transfers",
            "Environmental impact",
            "Safety",
            "Other",
        ],
    )
    improvement = st.text_area(
        "What would improve your commute? (optional)",
        max_chars=500,
        help="Do not include personal or identifying information.",
    )
    submitted = st.form_submit_button(
        "Submit response",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if not database_ready or supabase is None:
        st.error("Your response was not submitted because the database is unavailable.")
    else:
        answer = {
            "age": int(age),
            "study_year": study_year,
            "transport": transport,
            "duration": duration,
            "daily_cost": daily_cost,
            "satisfaction": int(satisfaction),
            "lateness": lateness,
            "route_planning": planning,
            "choice_factors": factors,
            "improvement": improvement.strip(),
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            supabase.table("survey_responses").insert({"answers": answer}).execute()
            load_stats.clear()
            st.success("Thank you! Your response has been recorded.")
        except Exception:
            st.error(
                "We could not save your response. Please try again later. "
                "No response has been added to the results."
            )

st.divider()
st.subheader("Survey overview")
st.caption(
    "Only grouped statistics are displayed. Results are hidden until at least "
    "five responses have been collected."
)

if database_ready:
    try:
        stats = load_stats()
        total = int(stats.get("total") or 0)
        transports = stats.get("transport_counts") or {}
        durations = stats.get("duration_counts") or {}
        factors_data = stats.get("factor_counts") or {}
        average = stats.get("avg_satisfaction")

        metric_a, metric_b, metric_c = st.columns(3)
        metric_a.metric("Responses", total)
        metric_b.metric(
            "Average satisfaction",
            f"{float(average):.1f} / 10" if average is not None else "Not available",
        )
        most_common = max(transports, key=transports.get) if transports else "Not available"
        metric_c.metric("Most common transport", most_common)

        if total < 5:
            st.info(f"More responses are needed before group statistics are displayed ({total}/5 so far).")
        else:
            chart_left, chart_right = st.columns(2)
            with chart_left:
                if transports:
                    transport_df = pd.DataFrame(
                        transports.items(), columns=["Transport", "Responses"]
                    ).sort_values("Responses", ascending=False)
                    fig = px.bar(
                        transport_df,
                        x="Transport",
                        y="Responses",
                        title="How students travel",
                        color_discrete_sequence=[COLORS["plum"]],
                    )
                    fig.update_layout(
                        plot_bgcolor=COLORS["card"],
                        paper_bgcolor=COLORS["card"],
                        font_color=COLORS["ink"],
                        xaxis_title=None,
                        yaxis_title="Responses",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No transport categories are available yet.")

            with chart_right:
                duration_order = [
                    "Up to 15 minutes",
                    "15–30 minutes",
                    "31–45 minutes",
                    "46–60 minutes",
                    "More than 1 hour",
                ]
                duration_df = pd.DataFrame(
                    {
                        "Commute duration": duration_order,
                        "Responses": [int(durations.get(item, 0)) for item in duration_order],
                    }
                )
                fig = px.bar(
                    duration_df,
                    x="Commute duration",
                    y="Responses",
                    title="One-way commute duration",
                    color_discrete_sequence=[COLORS["orange"]],
                )
                fig.update_layout(
                    plot_bgcolor=COLORS["card"],
                    paper_bgcolor=COLORS["card"],
                    font_color=COLORS["ink"],
                    xaxis_title=None,
                    yaxis_title="Responses",
                )
                st.plotly_chart(fig, use_container_width=True)

            if factors_data:
                factors_df = pd.DataFrame(
                    factors_data.items(), columns=["Choice factor", "Responses"]
                ).sort_values("Responses", ascending=False)
                fig = px.bar(
                    factors_df,
                    x="Responses",
                    y="Choice factor",
                    orientation="h",
                    title="Factors influencing transport choice",
                    color_discrete_sequence=[COLORS["plum"]],
                )
                fig.update_layout(
                    plot_bgcolor=COLORS["card"],
                    paper_bgcolor=COLORS["card"],
                    font_color=COLORS["ink"],
                    yaxis={"categoryorder": "total ascending"},
                )
                st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.error(
            "The survey statistics could not be loaded. Check that the Supabase "
            "setup script has been applied."
        )
else:
    st.info("The results dashboard will be available after database setup.")

st.caption("Educational project · Aggregated results only · Built with Streamlit and Supabase")
