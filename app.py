import streamlit as st
import pandas as pd
from groq import Groq
from datetime import datetime
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Subscription Waste Detector",
    page_icon="💸",
    layout="wide"
)

# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

.main {
    background-color: #f3f6fb;
}

.block-container {
    padding-top: 0.7rem;
    padding-bottom: 0.3rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

.hero-section {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    padding: 28px;
    border-radius: 22px;
    margin-bottom: 16px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.12);
    text-align: center;
}

.hero-title {
    color: white;
    font-size: 44px;
    font-weight: 800;
    margin-bottom: 4px;
}

.hero-subtitle {
    color: #cbd5e1;
    font-size: 18px;
    font-weight: 400;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
    text-align: center;
    border: 1px solid #e2e8f0;
}

.metric-card h1 {
    margin-top: 8px;
}

.subscription-card {
    padding: 12px 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    font-size: 15px;
    font-weight: 600;
}

.high {
    background-color: #fee2e2;
    color: #991b1b;
}

.medium {
    background-color: #fef3c7;
    color: #92400e;
}

.low {
    background-color: #dcfce7;
    color: #166534;
}

.section-box {
    background-color: white;
    padding: 14px 18px;
    border-radius: 18px;
    margin-top: 4px;
    margin-bottom: 10px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.06);
    border: 1px solid #e2e8f0;
}

.section-box h2{
    margin-top: 0px;
    margin-bottom: 8px;
    padding:0px;
    font-size: 24px;
}

hr {
    margin-top: 14px !important;
    margin-bottom: 14px !important;
}

div[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HERO SECTION
# ==================================================

st.markdown("""
<div class="hero-section">
    <div class="hero-title">💸 Subscription Waste Detector</div>
    <div class="hero-subtitle">
        AI-powered dashboard to track subscriptions,
        renewal reminders, and reduce unnecessary spending.
    </div>
</div>
""", unsafe_allow_html=True)

# ==================================================
# API KEY
# ==================================================

client = Groq(
    api_key="PASTE_YOUR_GROQ_API_KEY_HERE"
)

# ==================================================
# FILE UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "📂 Upload Expense CSV or Excel File",
    type=["csv", "xlsx"]
)

# ==================================================
# MANUAL EXPENSE ENTRY
# ==================================================

st.markdown("---")
st.subheader("✍️ Add Expense Manually")

col1, col2 = st.columns(2)

with col1:
    manual_date = st.date_input("Date")
    manual_desc = st.text_input("Expense Description")

with col2:
    manual_amount = st.number_input(
        "Amount",
        min_value=0
    )

    renewal_date = st.date_input(
        "Renewal Date"
    )

if "manual_expenses" not in st.session_state:
    st.session_state.manual_expenses = []

if st.button("Add Expense"):

    new_expense = {
        "Date": str(manual_date),
        "Description": manual_desc,
        "Amount": manual_amount,
        "Renewal_Date": str(renewal_date)
    }

    st.session_state.manual_expenses.append(
        new_expense
    )

    st.success("Expense added successfully!")

# ==================================================
# LOAD DATA
# ==================================================

df = pd.DataFrame()

if uploaded_file is not None:

    try:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        else:
            df = pd.read_excel(uploaded_file)

    except Exception as e:
        st.error(f"Error loading file: {e}")

manual_df = pd.DataFrame(
    st.session_state.manual_expenses
)

if not manual_df.empty:
    df = pd.concat(
        [df, manual_df],
        ignore_index=True
    )

# ==================================================
# MAIN DASHBOARD
# ==================================================

if not df.empty:

    df.columns = df.columns.str.strip()

    df["Description"] = (
        df["Description"].astype(str)
    )

    df["Amount"] = pd.to_numeric(
        df["Amount"]
    )

    # ==============================================
    # SMART SUBSCRIPTION DETECTION
    # ==============================================

    subscriptions = []

    grouped = df.groupby("Description")

    for name, group in grouped:

        if len(group) >= 2:

            amount_std = group["Amount"].std()
            avg_amount = group["Amount"].mean()

            is_same_amount = (
                amount_std < (avg_amount * 0.1)
            )

            known = [
                "netflix",
                "spotify",
                "amazon prime",
                "adobe",
                "google one",
                "claude",
                "youtube",
                "hotstar",
                "Microsoft 365",
                "Apple TV",
                "canva",
                "chatgpt",
                "snapchat",
                "prime video",
                "zee5",
                "MidJourney",
                "duolingo",
                "Xbox game pass",
                "playstation plus",
                "Perplexity",
                "reddit"
            ]

            is_known = any(
                word in name.lower()
                for word in known
            )

            if is_same_amount or is_known:
                subscriptions.append(name)

    # ==============================================
    # METRICS
    # ==============================================

    total_spending = int(
        df["Amount"].sum()
    )

    possible_savings = 0

    for sub in subscriptions:

        sub_rows = df[
            df["Description"].str.contains(
                sub,
                case=False
            )
        ]

        possible_savings += int(
            sub_rows["Amount"].mean()
        )

    # ==============================================
    # METRIC CARDS
    # ==============================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(f"""
        <div class="metric-card">
            <h4>💰 Total Spending</h4>
            <h1>₹ {total_spending}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        st.markdown(f"""
        <div class="metric-card">
            <h4>📌 Active Subscriptions</h4>
            <h1>{len(subscriptions)}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col3:

        st.markdown(f"""
        <div class="metric-card">
            <h4>💵 Possible Savings</h4>
            <h1>₹ {possible_savings}</h1>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==============================================
    # CHART DATA
    # ==============================================

    chart_data = []

    for sub in subscriptions:

        sub_rows = df[
            df["Description"].str.contains(
                sub,
                case=False
            )
        ]

        avg_cost = int(
            sub_rows["Amount"].mean()
        )

        chart_data.append({
            "Subscription": sub,
            "Monthly Cost": avg_cost
        })

    chart_df = pd.DataFrame(chart_data)

    left, right = st.columns(2)

    # ==============================================
    # DETECTED SUBSCRIPTIONS
    # ==============================================

    with left:

        st.markdown("""
        <div class="section-box">
        <h2>🔄 Detected Subscriptions</h2>
        """, unsafe_allow_html=True)

        for sub in subscriptions:

            sub_rows = df[
                df["Description"].str.contains(
                    sub,
                    case=False
                )
            ]

            avg_cost = int(
                sub_rows["Amount"].mean()
            )

            if avg_cost > 1000:
                usage_text = (
                    "🔴 High Monthly Expense"
                )

            elif avg_cost > 400:
                usage_text = (
                    "🟡  Moderate Spend"
                )

            else:
                usage_text = (
                    "🟢 Worth the Cost"
                )

            if avg_cost > 1000:

                st.markdown(f"""
                <div class="subscription-card high">
                🔴 {sub} — ₹{avg_cost}/month<br>
                {usage_text}
                </div>
                """, unsafe_allow_html=True)

            elif avg_cost > 400:

                st.markdown(f"""
                <div class="subscription-card medium">
                🟡 {sub} — ₹{avg_cost}/month<br>
                {usage_text}
                </div>
                """, unsafe_allow_html=True)

            else:

                st.markdown(f"""
                <div class="subscription-card low">
                🟢 {sub} — ₹{avg_cost}/month<br>
                {usage_text}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ==============================================
    # PIE CHART
    # ==============================================

    with right:

        st.markdown("""
        <div class="section-box">
        <h2>📊 Subscription Breakdown</h2>
        """, unsafe_allow_html=True)

        pie_chart = px.pie(
            chart_df,
            names="Subscription",
            values="Monthly Cost",
            hole=0.45
        )

        pie_chart.update_layout(
            height=380
        )

        st.plotly_chart(
            pie_chart,
            use_container_width=True
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ==============================================
    # RENEWAL REMINDERS
    # ==============================================

    st.markdown("""
    <div class="section-box">
    <h2>⏰ Subscription Renewal Reminders</h2>
    """, unsafe_allow_html=True)

    if "Renewal_Date" in df.columns:

        today = datetime.today().date()

        for index, row in df.iterrows():

            try:

                if pd.notna(row["Renewal_Date"]):

                    renewal = pd.to_datetime(
                        row["Renewal_Date"]
                    ).date()

                    days_left = (
                        renewal - today
                    ).days

                    if 0 <= days_left <= 7:

                        st.warning(
                            f"{row['Description']} renews in "
                            f"{days_left} day(s) on {renewal}"
                        )

            except:
                pass

    st.markdown("</div>", unsafe_allow_html=True)

    # ==============================================
    # AI SUGGESTIONS
    # ==============================================

    with st.expander(
        "🧠 AI Cost-Saving Suggestions"
    ):

        if st.button(
            "Get AI Suggestions",
            key="ai_button"
        ):

            try:

                summary_text = ""

                for sub in subscriptions:

                    sub_rows = df[
                        df["Description"].str.contains(
                            sub,
                            case=False
                        )
                    ]

                    avg_cost = int(
                        sub_rows["Amount"].mean()
                    )

                    summary_text += (
                        f"{sub}: ₹{avg_cost}/month\n"
                    )

                prompt = f"""
                Analyze these subscriptions and give smart
                cost-saving suggestions:

                {summary_text}
                """

                response = (
                    client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
                )

                ai_text = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                st.success(ai_text)

            except Exception as e:

                st.error(f"AI Error: {e}")

    # ==============================================
    # RAW DATA
    # ==============================================

    with st.expander(
        "📋 View Raw Expense Data"
    ):

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    # ==============================================
    # MONTHLY COST TABLE
    # ==============================================

    with st.expander(
        "💳 Monthly Subscription Cost"
    ):

        st.dataframe(
            chart_df,
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # ==============================================
    # DOWNLOAD REPORT
    # ==============================================

    report = f"""
SUBSCRIPTION WASTE DETECTOR REPORT

Total Spending: ₹ {total_spending}

Detected Subscriptions:
{", ".join(subscriptions)}

Monthly Subscription Costs:
"""

    report += chart_df.to_string(index=False)

    st.download_button(
        label="📥 Download Report",
        data=report,
        file_name="subscription_report.txt"
    )