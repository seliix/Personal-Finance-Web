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


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(15, 118, 110, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(251, 191, 36, 0.18), transparent 28%),
            linear-gradient(180deg, #f7f4ea 0%, #f3efe3 46%, #eef4ef 100%);
        color: #1f2937;
    }
    [data-testid="stSidebar"] {
        background: rgba(255, 251, 235, 0.92);
        border-right: 1px solid rgba(120, 113, 108, 0.16);
    }
    .hero-card {
        background: linear-gradient(135deg, rgba(17, 94, 89, 0.96), rgba(21, 128, 61, 0.92));
        color: white;
        border-radius: 28px;
        padding: 2rem 2rem 1.6rem 2rem;
        box-shadow: 0 24px 60px rgba(17, 94, 89, 0.18);
        margin-bottom: 1.4rem;
    }
    .soft-card {
        background: rgba(255, 252, 245, 0.9);
        border: 1px solid rgba(120, 113, 108, 0.14);
        border-radius: 22px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 14px 36px rgba(28, 25, 23, 0.05);
        height: 100%;
    }
    .step-card {
        background: rgba(255, 255, 255, 0.76);
        border-left: 4px solid #0f766e;
        border-radius: 18px;
        padding: 1rem 1rem 0.9rem 1rem;
        margin-bottom: 0.8rem;
    }
    h1, h2, h3 {
        letter-spacing: -0.03em;
    }
    p, li {
        color: #374151;
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
    <div class="hero-card">
        <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.18em; opacity: 0.78;">ClearPath Money</div>
        <div style="font-size: 3rem; font-weight: 800; line-height: 1.02; margin-top: 0.45rem;">A personal finance website that helps people build calmer, stronger money habits.</div>
        <div style="font-size: 1.05rem; max-width: 760px; margin-top: 0.9rem; opacity: 0.92;">
            See where your money is going, understand tradeoffs, and get a practical next-step plan for budgeting, debt, and savings.
        </div>
        <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1.2rem;">
            <div style="background: rgba(255,255,255,0.12); border-radius: 999px; padding: 0.55rem 0.9rem;">Monthly income: {currency(monthly_income)}</div>
            <div style="background: rgba(255,255,255,0.12); border-radius: 999px; padding: 0.55rem 0.9rem;">Planned savings: {currency(monthly_savings)}</div>
            <div style="background: rgba(255,255,255,0.12); border-radius: 999px; padding: 0.55rem 0.9rem;">Free cash flow: {currency(surplus)}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

top_metrics = st.columns(4)
metric_data = [
    ("Essentials", currency(essential_expenses), "Core monthly bills before lifestyle spending."),
    ("Savings Rate", pct(savings_ratio), "How much of take-home pay is going to future goals."),
    ("Debt Load", pct(debt_ratio), "Monthly income currently committed to debt payments."),
    ("Emergency Coverage", f"{emergency_months_covered:.1f} months", "How many months of essentials your current emergency fund could cover."),
]
for column, (label, value, help_text) in zip(top_metrics, metric_data, strict=True):
    with column:
        st.markdown(
            f"""
            <div class="soft-card">
                <div style="font-size: 0.9rem; color: #57534e;">{label}</div>
                <div style="font-size: 2rem; font-weight: 800; color: #111827; margin: 0.35rem 0;">{value}</div>
                <div style="font-size: 0.9rem; color: #57534e;">{help_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


dashboard_tab, budget_tab, debt_tab, goals_tab, learn_tab = st.tabs(
    ["Dashboard", "Budget Plan", "Debt Strategy", "Savings Goals", "Learn"]
)

with dashboard_tab:
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
                    <div style="font-weight: 800; color: #0f172a; margin-bottom: 0.3rem;">{title}</div>
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

with budget_tab:
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
            - Keep essentials as lean as your life allows so goals do not depend on motivation alone.
            - Treat savings like a bill by automating it right after payday.
            - Give lifestyle spending a number on purpose so you can enjoy it without guilt.
            - If money feels tight, audit the largest recurring costs first before chasing tiny cuts.
            """
        )

        if surplus > 0:
            st.success(f"You currently have {currency(surplus)} left after planned spending.")
        elif surplus == 0:
            st.warning("Your plan breaks even right now. That can work, but it leaves little room for surprises.")
        else:
            st.error(f"Your plan is short by {currency(abs(surplus))}. Reducing expenses or adjusting savings targets would make the budget workable.")

with debt_tab:
    st.subheader("Debt Payoff Focus")
    extra_payment = max(surplus, 0)
    estimated_acceleration = debt_payments + extra_payment

    debt_cols = st.columns(3)
    debt_cols[0].metric("Minimum payment", currency(debt_payments))
    debt_cols[1].metric("Potential extra payment", currency(extra_payment))
    debt_cols[2].metric("Possible monthly debt attack", currency(estimated_acceleration))

    st.markdown(
        """
        <div class="soft-card">
            <div style="font-weight: 800; margin-bottom: 0.45rem;">Simple debt roadmap</div>
            <div>1. Pay every minimum on time to protect your credit and avoid fees.</div>
            <div>2. Use any extra cash on one target debt at a time.</div>
            <div>3. Avalanche method saves the most interest by targeting the highest APR first.</div>
            <div>4. Snowball method can build momentum faster by clearing the smallest balance first.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with goals_tab:
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

with learn_tab:
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
                <div class="soft-card">
                    <div style="font-size: 1.2rem; font-weight: 800; margin-bottom: 0.45rem;">{title}</div>
                    <div>{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        ### Healthy money habits
        - Review spending weekly so course corrections stay small.
        - Increase savings when income rises instead of letting lifestyle costs absorb every raise.
        - Avoid comparing your timeline to other people. Stability is progress.
        - Choose systems over willpower: autopay, auto-save, reminders, and fixed transfer rules.
        """
    )
