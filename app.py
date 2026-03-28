from __future__ import annotations

import math

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="ClearPath Money", layout="wide")


def currency(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.0%}"


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(value, high))


def months_to_goal(goal_amount: float, current_saved: float, monthly_savings: float) -> int | None:
    remaining = max(goal_amount - current_saved, 0)
    if remaining == 0:
        return 0
    if monthly_savings <= 0:
        return None
    return math.ceil(remaining / monthly_savings)


def financial_health_score(
    housing_ratio: float,
    savings_ratio: float,
    debt_ratio: float,
    emergency_months: float,
    surplus_ratio: float,
) -> int:
    score = 0.0
    score += clamp(1 - abs(housing_ratio - 0.28) / 0.28) * 25
    score += clamp(savings_ratio / 0.2) * 25
    score += clamp(1 - debt_ratio / 0.25) * 20
    score += clamp(emergency_months / 6) * 20
    score += clamp((surplus_ratio + 0.1) / 0.2) * 10
    return round(score)


def score_label(score: int) -> str:
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Stable"
    if score >= 40:
        return "Needs Attention"
    return "Reset Mode"


def action_plan(
    housing_ratio: float,
    essentials_ratio: float,
    savings_ratio: float,
    debt_ratio: float,
    surplus: float,
    emergency_months: float,
) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []

    if surplus < 0:
        items.append(
            (
                "Fix the monthly shortfall first",
                "Your plan is spending more than it brings in. Reduce a few large expenses or temporarily lower savings targets before taking on new goals.",
            )
        )
    if housing_ratio > 0.3:
        items.append(
            (
                "Housing is eating a big share",
                "Try to keep housing close to 30% of take-home pay when possible. If that is not realistic, protect the rest of your budget by tightening other fixed costs.",
            )
        )
    if essentials_ratio > 0.65:
        items.append(
            (
                "Essentials are too heavy",
                "Core bills are crowding out flexibility. Review insurance, groceries, transportation, subscriptions, and recurring autopay items.",
            )
        )
    if savings_ratio < 0.15:
        items.append(
            (
                "Increase automatic savings gradually",
                "A 1% to 3% increase in automatic saving is often easier to keep than a major cut all at once.",
            )
        )
    if debt_ratio > 0.2:
        items.append(
            (
                "Debt deserves focused attention",
                "Keep every minimum current, then send extra cash to one target balance at a time so progress compounds.",
            )
        )
    if emergency_months < 3:
        items.append(
            (
                "Emergency fund needs more cushion",
                "Build toward one month of essentials first, then three months. That creates real breathing room when life gets expensive.",
            )
        )

    if not items:
        items.append(
            (
                "You have a healthy base",
                "You have room to direct more money toward investing, retirement, and a meaningful life goal without losing stability.",
            )
        )

    return items[:4]


st.markdown(
    """
    <style>
    :root {
        --bg: #0f172a;
        --bg-accent: #111827;
        --panel: rgba(17, 24, 39, 0.82);
        --panel-strong: rgba(15, 23, 42, 0.96);
        --border: rgba(148, 163, 184, 0.18);
        --text: #e5e7eb;
        --muted: #9aa5b1;
        --accent: #2dd4bf;
        --accent-2: #f59e0b;
        --hero-a: #0b1220;
        --hero-b: #134e4a;
        --shadow: 0 18px 42px rgba(0, 0, 0, 0.28);
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(15, 118, 110, 0.08), transparent 30%),
            radial-gradient(circle at top right, rgba(217, 119, 6, 0.08), transparent 26%),
            linear-gradient(180deg, var(--bg) 0%, var(--bg-accent) 100%);
        color: var(--text);
    }
    .block-container {
        max-width: 1180px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    [data-testid="stSidebar"] {
        background: var(--panel-strong);
        border-right: 1px solid var(--border);
    }
    h1, h2, h3, p, label, div {
        color: var(--text);
    }
    [data-baseweb="tab-list"] {
        gap: 0.4rem;
        margin-bottom: 0.8rem;
    }
    [data-baseweb="tab"] {
        border-radius: 999px;
        background: rgba(255,255,255,0.18);
        padding: 0.35rem 0.85rem;
    }
    .hero {
        background: linear-gradient(135deg, var(--hero-a), var(--hero-b));
        color: white;
        border-radius: 24px;
        padding: 1.5rem 1.6rem;
        box-shadow: var(--shadow);
        margin-bottom: 0.9rem;
    }
    .hero h1, .hero p {
        color: white;
    }
    .metric-card {
        background: var(--panel-strong);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 0.95rem 1rem;
        box-shadow: var(--shadow);
    }
    .insight-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.65rem;
    }
    .small-note {
        color: var(--muted);
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.title("Inputs")
    monthly_income = st.number_input("Monthly take-home income", min_value=0.0, value=4200.0, step=100.0)

    st.subheader("Core spending")
    housing = st.number_input("Housing", min_value=0.0, value=1450.0, step=50.0)
    utilities = st.number_input("Utilities", min_value=0.0, value=250.0, step=25.0)
    groceries = st.number_input("Groceries", min_value=0.0, value=450.0, step=25.0)
    transportation = st.number_input("Transportation", min_value=0.0, value=260.0, step=25.0)
    insurance = st.number_input("Insurance", min_value=0.0, value=180.0, step=20.0)

    st.subheader("Flexible spending")
    lifestyle = st.number_input("Lifestyle and fun", min_value=0.0, value=420.0, step=25.0)
    debt_payments = st.number_input("Debt payments", min_value=0.0, value=300.0, step=25.0)
    monthly_savings = st.number_input("Savings or investing", min_value=0.0, value=500.0, step=25.0)

    st.subheader("Goals")
    current_emergency_fund = st.number_input("Current emergency fund", min_value=0.0, value=1200.0, step=100.0)
    emergency_goal_months = st.slider("Emergency fund target in months", min_value=1, max_value=12, value=3)
    savings_goal_name = st.text_input("Next savings goal", value="Travel fund")
    savings_goal_amount = st.number_input("Goal amount", min_value=0.0, value=3000.0, step=100.0)
    current_goal_progress = st.number_input("Already saved toward goal", min_value=0.0, value=600.0, step=50.0)


essential_expenses = housing + utilities + groceries + transportation + insurance
needs_total = essential_expenses + debt_payments
planned_outflow = needs_total + lifestyle + monthly_savings
surplus = monthly_income - planned_outflow

housing_ratio = housing / monthly_income if monthly_income else 0.0
essentials_ratio = essential_expenses / monthly_income if monthly_income else 0.0
savings_ratio = monthly_savings / monthly_income if monthly_income else 0.0
debt_ratio = debt_payments / monthly_income if monthly_income else 0.0
surplus_ratio = surplus / monthly_income if monthly_income else 0.0

recommended_emergency_goal = essential_expenses * emergency_goal_months
emergency_months_covered = current_emergency_fund / essential_expenses if essential_expenses else 0.0
goal_months = months_to_goal(savings_goal_amount, current_goal_progress, monthly_savings)
health_score = financial_health_score(
    housing_ratio,
    savings_ratio,
    debt_ratio,
    emergency_months_covered,
    surplus_ratio,
)

budget_df = pd.DataFrame(
    {
        "Category": [
            "Housing",
            "Utilities",
            "Groceries",
            "Transportation",
            "Insurance",
            "Lifestyle",
            "Debt",
            "Savings",
        ],
        "Amount": [
            housing,
            utilities,
            groceries,
            transportation,
            insurance,
            lifestyle,
            debt_payments,
            monthly_savings,
        ],
    }
)

allocation_df = pd.DataFrame(
    {
        "Bucket": ["Needs", "Wants", "Future"],
        "Current": [needs_total, lifestyle, monthly_savings],
        "Guide": [monthly_income * 0.5, monthly_income * 0.3, monthly_income * 0.2],
    }
)

pie_chart = px.pie(
    budget_df,
    names="Category",
    values="Amount",
    hole=0.58,
    color_discrete_sequence=["#0f766e", "#14b8a6", "#84cc16", "#eab308", "#f97316", "#ef4444", "#7c3aed", "#2563eb"],
)
pie_chart.update_traces(
    textfont_color="#ffffff",
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Amount: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
)
pie_chart.update_layout(
    margin=dict(l=0, r=0, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ffffff"),
)

allocation_chart = px.bar(
    allocation_df.melt(id_vars="Bucket", value_vars=["Current", "Guide"], var_name="Type", value_name="Amount"),
    x="Bucket",
    y="Amount",
    color="Type",
    barmode="group",
    color_discrete_map={"Current": "#0f766e", "Guide": "#d97706"},
)
allocation_chart.update_layout(
    margin=dict(l=0, r=0, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend_title_text="",
    yaxis_title="Monthly dollars",
    xaxis_title="",
)


st.markdown(
    f"""
    <div class="hero">
        <p style="margin:0; opacity:0.82; text-transform:uppercase; letter-spacing:0.16em; font-size:0.82rem;">ClearPath Money</p>
        <h1 style="margin:0.45rem 0 0 0; font-size:2.7rem; line-height:1.02;">Personal finance that feels organized, useful, and easy to act on.</h1>
        <p style="max-width:760px; margin:0.85rem 0 0 0; font-size:1rem;">
            Use the sidebar to model your monthly money plan. The dashboard turns it into a budget check, savings outlook,
            debt guidance, and a practical action list.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_values = [
    ("Financial Health", f"{health_score}/100", score_label(health_score)),
    ("Free Cash Flow", currency(surplus), "Money left after planned spending"),
    ("Savings Rate", pct(savings_ratio), "Share of income going to future goals"),
    ("Emergency Coverage", f"{emergency_months_covered:.1f} months", "Current cash cushion"),
]
for column, (title, value, note) in zip(metric_cols, metric_values, strict=True):
    with column:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-note">{title}</div>
                <div style="font-size:2rem; font-weight:800; margin:0.2rem 0;">{value}</div>
                <div class="small-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

overview_tab, budget_tab, goals_tab, learn_tab = st.tabs(["Overview", "Budget", "Goals", "Learn"])

with overview_tab:
    left, right = st.columns((1.25, 1))
    with left:
        st.subheader("Spending Breakdown")
        st.plotly_chart(pie_chart, use_container_width=True)
        st.subheader("50/30/20 Check")
        st.plotly_chart(allocation_chart, use_container_width=True)

    with right:
        st.subheader("Top Priorities")
        for title, detail in action_plan(
            housing_ratio,
            essentials_ratio,
            savings_ratio,
            debt_ratio,
            surplus,
            emergency_months_covered,
        ):
            st.markdown(
                f"""
                <div class="insight-card">
                    <div style="font-weight:800; margin-bottom:0.3rem;">{title}</div>
                    <div class="small-note">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.subheader("Quick Snapshot")
        st.info(
            f"Needs total {currency(needs_total)}. Wants are {currency(lifestyle)}. Future-focused money is {currency(monthly_savings)}."
        )
        if surplus > 0:
            st.success(f"Your current plan leaves {currency(surplus)} available each month.")
        elif surplus == 0:
            st.warning("Your plan currently breaks even. That works, but it leaves little room for surprises.")
        else:
            st.error(f"Your plan is short by {currency(abs(surplus))} per month.")

with budget_tab:
    left, right = st.columns((1.1, 1))
    with left:
        st.subheader("Budget Table")
        budget_view = budget_df.copy()
        budget_view["Share of Income"] = budget_view["Amount"].map(
            lambda amount: pct(amount / monthly_income) if monthly_income else "0%"
        )
        budget_view["Amount"] = budget_view["Amount"].map(currency)
        st.dataframe(budget_view, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Budget Coaching")
        st.markdown(
            """
            - Protect essentials first so the rest of your plan has a stable base.
            - Automate savings right after payday instead of waiting to see what is left.
            - Keep lifestyle spending intentional so it stays enjoyable without turning vague.
            - If money feels tight, review the biggest recurring costs before chasing small cuts.
            """
        )

        st.subheader("Rule of Thumb")
        st.write(f"`Needs`: {pct((needs_total / monthly_income) if monthly_income else 0)}")
        st.write(f"`Wants`: {pct((lifestyle / monthly_income) if monthly_income else 0)}")
        st.write(f"`Future`: {pct((monthly_savings / monthly_income) if monthly_income else 0)}")

with goals_tab:
    left, right = st.columns(2)
    with left:
        st.subheader("Emergency Fund")
        emergency_progress = (
            min(current_emergency_fund / recommended_emergency_goal, 1.0) if recommended_emergency_goal else 0.0
        )
        st.progress(emergency_progress)
        st.write(f"Saved: {currency(current_emergency_fund)}")
        st.write(f"Recommended target: {currency(recommended_emergency_goal)}")
        if emergency_months_covered < 1:
            st.info("First milestone: reach one month of essential expenses.")
        elif emergency_months_covered < 3:
            st.info("You are building traction. Three months would give you much more resilience.")
        else:
            st.success("Your emergency fund is starting to provide real stability.")

    with right:
        st.subheader(savings_goal_name)
        goal_progress = min(current_goal_progress / savings_goal_amount, 1.0) if savings_goal_amount else 0.0
        st.progress(goal_progress)
        st.write(f"Saved so far: {currency(current_goal_progress)}")
        st.write(f"Goal target: {currency(savings_goal_amount)}")
        if goal_months is None:
            st.info("Set savings above zero to estimate when this goal can be funded.")
        elif goal_months == 0:
            st.success("This goal is already funded.")
        else:
            st.success(f"At the current pace, you could reach this goal in about {goal_months} months.")

with learn_tab:
    learn_cols = st.columns(3)
    lessons = [
        (
            "Budgeting",
            "A budget is a plan for priorities, not a punishment. It should make decisions easier, not more stressful.",
        ),
        (
            "Emergency Funds",
            "Cash reserves keep routine life problems from turning into expensive debt problems.",
        ),
        (
            "Debt Payoff",
            "Keep every account current, then choose either the highest APR or the smallest balance and attack it consistently.",
        ),
    ]
    for column, (title, body) in zip(learn_cols, lessons, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="metric-card" style="height:100%;">
                    <div style="font-size:1.1rem; font-weight:800; margin-bottom:0.45rem;">{title}</div>
                    <div class="small-note">{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("Habits That Help")
    st.markdown(
        """
        - Review spending weekly so small problems stay small.
        - Increase savings when income rises before lifestyle spending absorbs the difference.
        - Use autopay and auto-save whenever possible so progress does not depend on memory.
        - Compare yourself to your own last month, not someone else’s highlight reel.
        """
    )
