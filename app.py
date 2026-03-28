from __future__ import annotations

import math

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="ClearPath Money",
    layout="wide",
)


def currency(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.0%}"


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(value, high))


def months_to_goal(goal_amount: float, current_savings: float, monthly_savings: float) -> float | None:
    remaining = max(goal_amount - current_savings, 0)
    if remaining == 0:
        return 0
    if monthly_savings <= 0:
        return None
    return math.ceil(remaining / monthly_savings)


def build_action_plan(
    housing_ratio: float,
    essentials_ratio: float,
    savings_ratio: float,
    debt_ratio: float,
    surplus: float,
    emergency_months: float,
) -> list[tuple[str, str]]:
    actions: list[tuple[str, str]] = []

    if housing_ratio > 0.3:
        actions.append(
            (
                "Housing pressure is high",
                "Aim to keep housing near 30% of take-home pay. Consider a roommate, refinance research, or trimming other fixed costs.",
            )
        )
    if essentials_ratio > 0.6:
        actions.append(
            (
                "Essentials are crowding out flexibility",
                "Your core bills are using most of your income. Review subscriptions, insurance, groceries, transport, and recurring autopay items.",
            )
        )
    if savings_ratio < 0.15:
        actions.append(
            (
                "Boost savings automation",
                "Try increasing automatic savings by 1% to 3% of income first. Small recurring changes usually stick better than large one-time cuts.",
            )
        )
    if debt_ratio > 0.2:
        actions.append(
            (
                "Debt payments deserve attention",
                "High minimums can delay progress. Focus extra cash on the highest-interest balance while keeping all other accounts current.",
            )
        )
    if emergency_months < 3:
        actions.append(
            (
                "Emergency fund needs reinforcement",
                "A first milestone is 1 month of essential expenses, then 3 months, then 6 months if income is variable or your household has less stability.",
            )
        )
    if surplus <= 0:
        actions.append(
            (
                "Your plan is overspending",
                "Reduce planned spending or debt acceleration before adding new goals. A realistic budget works better than an ambitious one that breaks every month.",
            )
        )

    if not actions:
        actions.append(
            (
                "Your foundation looks healthy",
                "You have room to keep building wealth. Consider directing future raises toward retirement, emergency savings, and one meaningful life goal.",
            )
        )

    return actions


def financial_health_score(
    housing_ratio: float,
    savings_ratio: float,
    debt_ratio: float,
    emergency_months: float,
    surplus: float,
    monthly_income: float,
) -> int:
    if monthly_income <= 0:
        return 0

    score = 0.0
    score += clamp(1 - abs(housing_ratio - 0.28) / 0.28) * 20
    score += clamp(savings_ratio / 0.2) * 25
    score += clamp(1 - debt_ratio / 0.25) * 20
    score += clamp(emergency_months / 6) * 25
    score += clamp((surplus / monthly_income + 0.1) / 0.2) * 10
    return round(score)


def score_label(score: int) -> str:
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Stable"
    if score >= 40:
        return "Needs Attention"
    return "Reset Mode"


st.markdown(
    """
    <style>
    :root {
        --bg-main: linear-gradient(180deg, #ebe7de 0%, #e4e7df 52%, #dde5e1 100%);
        --bg-glow-left: rgba(15, 118, 110, 0.10);
        --bg-glow-right: rgba(217, 119, 6, 0.10);
        --panel: rgba(249, 247, 242, 0.82);
        --panel-strong: rgba(250, 248, 243, 0.94);
        --panel-soft: rgba(255, 255, 255, 0.62);
        --border: rgba(87, 83, 78, 0.16);
        --text-main: #1f2937;
        --text-muted: #5b625f;
        --accent: #0f766e;
        --accent-strong: #115e59;
        --hero-start: rgba(20, 83, 75, 0.96);
        --hero-end: rgba(37, 99, 72, 0.92);
        --shadow: 0 18px 40px rgba(28, 25, 23, 0.08);
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-main: linear-gradient(180deg, #111827 0%, #0f172a 55%, #111827 100%);
            --bg-glow-left: rgba(45, 212, 191, 0.08);
            --bg-glow-right: rgba(251, 191, 36, 0.07);
            --panel: rgba(20, 27, 39, 0.82);
            --panel-strong: rgba(17, 24, 39, 0.95);
            --panel-soft: rgba(255, 255, 255, 0.04);
            --border: rgba(148, 163, 184, 0.18);
            --text-main: #e5e7eb;
            --text-muted: #a8b1bc;
            --accent: #2dd4bf;
            --accent-strong: #5eead4;
            --hero-start: rgba(15, 23, 42, 0.96);
            --hero-end: rgba(19, 78, 74, 0.95);
            --shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
        }
    }
    .block-container {
        padding-top: 1.35rem;
        padding-bottom: 2rem;
        max-width: 1220px;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, var(--bg-glow-left), transparent 28%),
            radial-gradient(circle at top right, var(--bg-glow-right), transparent 28%),
            var(--bg-main);
        color: var(--text-main);
    }
    div[data-testid="stVerticalBlock"] > div:has(> div.hero-shell) {
        margin-bottom: 0.35rem;
    }
    div[data-testid="stVerticalBlock"] > div:has(> div.section-shell) {
        margin-bottom: 0.6rem;
    }
    [data-testid="stSidebar"] {
        background: var(--panel-strong);
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {
        color: var(--text-main);
    }
    .hero-shell {
        display: grid;
        grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.9fr);
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .hero-card {
        background: linear-gradient(135deg, var(--hero-start), var(--hero-end));
        color: white;
        border-radius: 28px;
        padding: 1.65rem 1.7rem 1.4rem 1.7rem;
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.18);
        min-height: 100%;
    }
    .hero-side {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: 28px;
        padding: 1.2rem;
        box-shadow: var(--shadow);
    }
    .hero-kicker {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        opacity: 0.8;
    }
    .hero-title {
        font-size: 2.75rem;
        font-weight: 800;
        line-height: 0.98;
        margin-top: 0.5rem;
        max-width: 760px;
    }
    .hero-copy {
        font-size: 1rem;
        max-width: 720px;
        margin-top: 0.8rem;
        opacity: 0.92;
    }
    .hero-pills {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    .hero-pill {
        background: rgba(255,255,255,0.12);
        border-radius: 999px;
        padding: 0.48rem 0.85rem;
        font-size: 0.92rem;
    }
    .section-shell {
        background: color-mix(in srgb, var(--panel) 80%, transparent);
        border: 1px solid var(--border);
        border-radius: 26px;
        padding: 0.9rem 1rem 1rem 1rem;
    }
    .soft-card {
        background: var(--panel-strong);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 0.95rem 1rem;
        box-shadow: var(--shadow);
        height: 100%;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.8rem;
        margin-bottom: 1rem;
    }
    .mini-stat {
        background: color-mix(in srgb, var(--accent) 10%, var(--panel-strong));
        border: 1px solid color-mix(in srgb, var(--accent) 24%, transparent);
        border-radius: 18px;
        padding: 0.9rem 1rem;
    }
    .step-card {
        background: var(--panel-soft);
        border-left: 4px solid var(--accent);
        border-radius: 18px;
        padding: 0.85rem 0.95rem 0.8rem 0.95rem;
        margin-bottom: 0.65rem;
    }
    .tip-card {
        background: var(--panel-soft);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.65rem;
    }
    .lesson-card {
        background: linear-gradient(180deg, var(--panel-strong), color-mix(in srgb, var(--panel) 86%, transparent));
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 1rem;
        min-height: 180px;
    }
    .checklist {
        display: grid;
        gap: 0.55rem;
    }
    .checklist-item {
        background: var(--panel-soft);
        border-radius: 16px;
        padding: 0.75rem 0.9rem;
        border: 1px solid var(--border);
    }
    h1, h2, h3 {
        letter-spacing: -0.03em;
        color: var(--text-main);
    }
    p, li {
        color: var(--text-muted);
    }
    h2 {
        margin-top: 0.1rem;
        margin-bottom: 0.65rem;
    }
    [data-baseweb="tab-list"] {
        gap: 0.5rem;
        margin-bottom: 0.8rem;
    }
    [data-baseweb="tab"] {
        background: var(--panel-soft);
        border-radius: 999px;
        padding: 0.35rem 0.9rem;
        height: auto;
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricLabel"],
    .stMarkdown,
    .stAlert,
    .stDataFrame,
    .stProgress {
        color: var(--text-main);
    }
    @media (max-width: 980px) {
        .hero-shell {
            grid-template-columns: 1fr;
        }
        .metric-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .hero-title {
            font-size: 2.25rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Your Money Snapshot")
    monthly_income = st.number_input("Monthly take-home income", min_value=0.0, value=4200.0, step=100.0)
    housing = st.number_input("Housing", min_value=0.0, value=1450.0, step=50.0)
    utilities = st.number_input("Utilities", min_value=0.0, value=250.0, step=25.0)
    groceries = st.number_input("Groceries", min_value=0.0, value=450.0, step=25.0)
    transportation = st.number_input("Transportation", min_value=0.0, value=260.0, step=25.0)
    insurance = st.number_input("Insurance", min_value=0.0, value=180.0, step=20.0)
    lifestyle = st.number_input("Lifestyle and fun", min_value=0.0, value=420.0, step=25.0)
    debt_payments = st.number_input("Debt payments", min_value=0.0, value=300.0, step=25.0)
    monthly_savings = st.number_input("Savings or investing", min_value=0.0, value=500.0, step=25.0)

    st.divider()
    st.header("Goals")
    current_emergency_fund = st.number_input("Current emergency fund", min_value=0.0, value=1200.0, step=100.0)
    emergency_goal_months = st.slider("Emergency fund target", min_value=1, max_value=12, value=3)
    savings_goal_name = st.text_input("Next savings goal", value="Travel fund")
    savings_goal_amount = st.number_input("Goal amount", min_value=0.0, value=3000.0, step=100.0)
    current_goal_progress = st.number_input("Already saved toward goal", min_value=0.0, value=600.0, step=50.0)


essential_expenses = housing + utilities + groceries + transportation + insurance
planned_outflow = essential_expenses + lifestyle + debt_payments + monthly_savings
surplus = monthly_income - planned_outflow

housing_ratio = housing / monthly_income if monthly_income else 0
essentials_ratio = essential_expenses / monthly_income if monthly_income else 0
savings_ratio = monthly_savings / monthly_income if monthly_income else 0
debt_ratio = debt_payments / monthly_income if monthly_income else 0

recommended_emergency_goal = essential_expenses * emergency_goal_months
emergency_months_covered = current_emergency_fund / essential_expenses if essential_expenses else 0
goal_months = months_to_goal(savings_goal_amount, current_goal_progress, monthly_savings)
health_score = financial_health_score(
    housing_ratio,
    savings_ratio,
    debt_ratio,
    emergency_months_covered,
    surplus,
    monthly_income,
)

budget_df = pd.DataFrame(
    {
        "category": [
            "Housing",
            "Utilities",
            "Groceries",
            "Transportation",
            "Insurance",
            "Lifestyle",
            "Debt",
            "Savings",
        ],
        "amount": [
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

pie_chart = px.pie(
    budget_df,
    values="amount",
    names="category",
    hole=0.55,
    color_discrete_sequence=["#0f766e", "#14b8a6", "#84cc16", "#f59e0b", "#f97316", "#ef4444", "#7c3aed", "#2563eb"],
)
pie_chart.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=10, b=10),
    height=360,
)

allocation_df = pd.DataFrame(
    {
        "bucket": ["Needs", "Wants", "Future You"],
        "current": [essential_expenses + debt_payments, lifestyle, monthly_savings],
        "guide": [monthly_income * 0.5, monthly_income * 0.3, monthly_income * 0.2],
    }
)

allocation_chart = px.bar(
    allocation_df.melt(id_vars="bucket", value_vars=["current", "guide"], var_name="type", value_name="amount"),
    x="bucket",
    y="amount",
    color="type",
    barmode="group",
    color_discrete_map={"current": "#0f766e", "guide": "#d97706"},
)
allocation_chart.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend_title_text="",
    xaxis_title="",
    yaxis_title="Monthly dollars",
    height=340,
)


st.markdown(
    f"""
    <div class="hero-shell">
        <div class="hero-card">
            <div class="hero-kicker">ClearPath Money</div>
            <div class="hero-title">Design your money around real life, not guilt.</div>
            <div class="hero-copy">
                This dashboard helps people improve their personal finances with a cleaner monthly plan, better savings habits, and clearer debt decisions.
            </div>
            <div class="hero-pills">
                <div class="hero-pill">Monthly income: {currency(monthly_income)}</div>
                <div class="hero-pill">Planned savings: {currency(monthly_savings)}</div>
                <div class="hero-pill">Free cash flow: {currency(surplus)}</div>
            </div>
        </div>
        <div class="hero-side">
            <div style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 0.25rem;">Financial health score</div>
            <div style="font-size: 3rem; font-weight: 800; line-height: 1;">{health_score}</div>
            <div style="font-weight: 700; color: var(--accent); margin-top: 0.25rem;">{score_label(health_score)}</div>
            <div style="margin-top: 0.7rem; color: var(--text-muted);">A quick blend of savings, debt, housing pressure, emergency coverage, and monthly cash flow.</div>
            <div style="display: grid; gap: 0.55rem; margin-top: 0.95rem;">
                <div class="mini-stat"><strong>{pct(housing_ratio)}</strong> of income goes to housing</div>
                <div class="mini-stat"><strong>{pct(savings_ratio)}</strong> goes to savings and investing</div>
                <div class="mini-stat"><strong>{emergency_months_covered:.1f} months</strong> of essentials covered</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_data = [
    ("Essentials", currency(essential_expenses), "Core monthly bills before lifestyle spending."),
    ("Savings Rate", pct(savings_ratio), "How much of take-home pay is going to future goals."),
    ("Debt Load", pct(debt_ratio), "Monthly income currently committed to debt payments."),
    ("Emergency Coverage", f"{emergency_months_covered:.1f} months", "How many months of essentials your current emergency fund could cover."),
]
metric_cards = "".join(
    f"""
    <div class="soft-card">
        <div style="font-size: 0.88rem; color: var(--text-muted);">{label}</div>
        <div style="font-size: 1.85rem; font-weight: 800; color: var(--text-main); margin: 0.25rem 0;">{value}</div>
        <div style="font-size: 0.88rem; color: var(--text-muted);">{help_text}</div>
    </div>
    """
    for label, value, help_text in metric_data
)
st.markdown(f'<div class="metric-grid">{metric_cards}</div>', unsafe_allow_html=True)


dashboard_tab, budget_tab, debt_tab, goals_tab, learn_tab = st.tabs(
    ["Dashboard", "Budget Plan", "Debt Strategy", "Savings Goals", "Learn"]
)

with dashboard_tab:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    chart_col, guide_col = st.columns((1.15, 1))
    with chart_col:
        st.subheader("Spending Mix")
        st.plotly_chart(pie_chart, use_container_width=True)
        st.subheader("50/30/20 Reality Check")
        st.plotly_chart(allocation_chart, use_container_width=True)

    with guide_col:
        st.subheader("Personalized Next Steps")
        for title, detail in build_action_plan(
            housing_ratio,
            essentials_ratio,
            savings_ratio,
            debt_ratio,
            surplus,
            emergency_months_covered,
        ):
            st.markdown(
                f"""
                <div class="step-card">
                    <div style="font-weight: 800; color: var(--text-main); margin-bottom: 0.3rem;">{title}</div>
                    <div>{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="soft-card">
                <div style="font-weight: 800; margin-bottom: 0.45rem;">This month at a glance</div>
                <div>Planned outflow: <strong>{currency(planned_outflow)}</strong></div>
                <div>Remaining cash flow: <strong>{currency(surplus)}</strong></div>
                <div>Recommended emergency fund: <strong>{currency(recommended_emergency_goal)}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

with budget_tab:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    left, right = st.columns((1.15, 1))
    with left:
        st.subheader("Budget Breakdown")
        table_df = budget_df.copy()
        table_df["share_of_income"] = table_df["amount"].map(lambda amount: pct(amount / monthly_income) if monthly_income else "0%")
        table_df["amount"] = table_df["amount"].map(currency)
        st.dataframe(table_df, use_container_width=True, hide_index=True)

    with right:
        st.subheader("Budget Coaching")
        st.markdown(
            """
            <div class="tip-card"><strong>Protect the basics.</strong><br>Keep essentials as lean as your life allows so your goals do not depend on motivation alone.</div>
            <div class="tip-card"><strong>Automate the future.</strong><br>Treat savings like a bill by moving money right after payday instead of waiting to see what is left.</div>
            <div class="tip-card"><strong>Spend with intent.</strong><br>Give lifestyle spending a real number so you can enjoy it without guilt or guesswork.</div>
            <div class="tip-card"><strong>Cut the big rocks first.</strong><br>If money feels tight, audit rent, transport, insurance, and debt before chasing tiny cuts.</div>
            """
            ,
            unsafe_allow_html=True,
        )

        if surplus > 0:
            st.success(f"You currently have {currency(surplus)} left after planned spending.")
        elif surplus == 0:
            st.warning("Your plan breaks even right now. That can work, but it leaves little room for surprises.")
        else:
            st.error(f"Your plan is short by {currency(abs(surplus))}. Reducing expenses or adjusting savings targets would make the budget workable.")
    st.markdown('</div>', unsafe_allow_html=True)

with debt_tab:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    debt_left, debt_right = st.columns((1.05, 1))
    extra_payment = max(surplus, 0)
    estimated_acceleration = debt_payments + extra_payment

    with debt_left:
        st.subheader("Debt Payoff Focus")
        debt_cols = st.columns(3)
        debt_cols[0].metric("Minimum payment", currency(debt_payments))
        debt_cols[1].metric("Potential extra payment", currency(extra_payment))
        debt_cols[2].metric("Monthly debt attack", currency(estimated_acceleration))

        st.markdown(
            """
            <div class="soft-card">
                <div style="font-weight: 800; margin-bottom: 0.45rem;">Choose a payoff style</div>
                <div style="margin-bottom: 0.55rem;"><strong>Avalanche:</strong> pay the highest APR first to reduce total interest.</div>
                <div><strong>Snowball:</strong> pay the smallest balance first to build momentum and visible wins.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with debt_right:
        st.subheader("Roadmap")
        st.markdown(
            """
            <div class="checklist">
                <div class="checklist-item">1. Keep every account current to avoid fees and credit damage.</div>
                <div class="checklist-item">2. Pick one target balance and send all extra cash there.</div>
                <div class="checklist-item">3. Roll each paid-off minimum into the next debt for faster acceleration.</div>
                <div class="checklist-item">4. Pause aggressive extra payments briefly if your emergency fund is near zero.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

with goals_tab:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    left, right = st.columns((1, 1))
    with left:
        st.subheader("Emergency Fund Progress")
        emergency_progress = min(current_emergency_fund / recommended_emergency_goal, 1.0) if recommended_emergency_goal else 0.0
        st.progress(emergency_progress)
        st.write(
            f"You have saved {currency(current_emergency_fund)} toward a target of {currency(recommended_emergency_goal)}."
        )
        if emergency_months_covered < 1:
            st.info("First target: build one month of essentials for basic breathing room.")
        elif emergency_months_covered < 3:
            st.info("You are building traction. Reaching three months would make setbacks much easier to absorb.")
        else:
            st.success("Your emergency fund is starting to provide meaningful resilience.")

    with right:
        st.subheader(savings_goal_name)
        goal_progress = min(current_goal_progress / savings_goal_amount, 1.0) if savings_goal_amount else 0.0
        st.progress(goal_progress)
        if goal_months is None:
            st.write("Set a monthly savings amount above zero to forecast this goal.")
        elif goal_months == 0:
            st.success("This goal is already funded.")
        else:
            st.write(
                f"At {currency(monthly_savings)} per month, you could fully fund this goal in about {goal_months} months."
            )
        st.write(f"Saved so far: {currency(current_goal_progress)} of {currency(savings_goal_amount)}.")
    st.markdown('</div>', unsafe_allow_html=True)

with learn_tab:
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.subheader("Money Basics That Actually Help")
    learn_cols = st.columns(3)
    lessons = [
        (
            "Budgeting",
            "A budget is not punishment. It is a plan that tells your money what matters before the month gets noisy.",
        ),
        (
            "Emergency Funds",
            "Cash reserves protect you from turning normal life problems into high-interest debt problems.",
        ),
        (
            "Investing",
            "Long-term investing works best when it is automated, diversified, and boring enough to keep going.",
        ),
    ]
    for column, (title, body) in zip(learn_cols, lessons, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="lesson-card">
                    <div style="font-size: 1.2rem; font-weight: 800; margin-bottom: 0.45rem;">{title}</div>
                    <div>{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div style="margin-top: 0.9rem;">
            <h3 style="margin-bottom: 0.55rem;">Healthy money habits</h3>
            <div class="checklist">
                <div class="checklist-item">Review spending weekly so course corrections stay small.</div>
                <div class="checklist-item">Increase savings when income rises instead of letting lifestyle costs absorb every raise.</div>
                <div class="checklist-item">Avoid comparing your timeline to other people. Stability is progress.</div>
                <div class="checklist-item">Choose systems over willpower: autopay, auto-save, reminders, and fixed transfer rules.</div>
            </div>
        </div>
        """
        ,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
