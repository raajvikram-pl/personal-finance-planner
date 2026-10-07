# app.py
from datetime import date
import io
import pandas as pd
import plotly.express as px
import streamlit as st

from analytics import budget_vs_actual, category_breakdown, get_transactions_df
from repository import (
    add_transaction,
    delete_transaction,
    set_budget,
    update_transaction,
)

# ---------------------------------------------------------
# Page Setup & Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Expense Analytics Studio",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

USER_ID = 1

# Custom CSS for UI styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.02);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Sidebar Navigation & Filter Controls
# ---------------------------------------------------------
st.sidebar.image(
    "https://img.icons8.com/duotone/96/4a6cf7/wallet.png", width=70
)
st.sidebar.title("Navigation")
navigation = st.sidebar.radio(
    "Select Screen",
    [
        "📊 Executive Summary",
        "➕ Log Transaction",
        "📥 Bulk CSV Import",
        "🎯 Set Category Budget",
        "📋 Ledger Records & Actions",
    ],
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Global Filters")
selected_month = st.sidebar.text_input(
    "Analysis Month (YYYY-MM)", value="2026-10"
)

# Fetch central DataFrame
df = get_transactions_df(USER_ID)

# ---------------------------------------------------------
# Screen 1: Executive Summary (Dashboard)
# ---------------------------------------------------------
if navigation == "📊 Executive Summary":
    st.markdown(
        '<div class="main-header">Financial Dashboard</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="sub-header">Overview & Analytics for <b>{selected_month}</b></div>',
        unsafe_allow_html=True,
    )

    if not df.empty:
        df["month_str"] = df["date"].dt.strftime("%Y-%m")
        monthly_df = df[df["month_str"] == selected_month]

        total_spend = (
            monthly_df["amount"].sum() if not monthly_df.empty else 0.0
        )
        total_count = len(monthly_df)

        budget_summary = budget_vs_actual(USER_ID, selected_month, df)
        total_budget = (
            budget_summary["budget_limit"].sum()
            if not budget_summary.empty
            else 0.0
        )
        remaining_budget = total_budget - total_spend

        # KPI Metric Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Total Spent</div>
                    <div class="metric-value">₹{total_spend:,.2f}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with kpi2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Monthly Target</div>
                    <div class="metric-value">₹{total_budget:,.2f}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with kpi3:
            status_color = "#10B981" if remaining_budget >= 0 else "#EF4444"
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Remaining Balance</div>
                    <div class="metric-value" style="color: {status_color}">₹{remaining_budget:,.2f}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        with kpi4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Transactions</div>
                    <div class="metric-value">{total_count}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("🍰 Spending Share by Category")
            cat_df = category_breakdown(
                monthly_df if not monthly_df.empty else df
            )

            if not cat_df.empty:
                fig = px.pie(
                    cat_df,
                    values="total_spent",
                    names="category",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                fig.update_traces(
                    textinfo="percent+label",
                    hovertemplate="%{label}: ₹%{value:,.2f}",
                )
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No transaction records found for this month.")

        with col_right:
            st.subheader("📊 Target Budget vs Actual Expense")
            if not budget_summary.empty:
                melted = budget_summary.melt(
                    id_vars=["category"],
                    value_vars=["budget_limit", "actual_spent"],
                    var_name="Metric",
                    value_name="Amount",
                )
                melted["Metric"] = melted["Metric"].map(
                    {
                        "budget_limit": "Budget Limit",
                        "actual_spent": "Actual Spent",
                    }
                )

                fig2 = px.bar(
                    melted,
                    x="category",
                    y="Amount",
                    color="Metric",
                    barmode="group",
                    color_discrete_map={
                        "Budget Limit": "#94A3B8",
                        "Actual Spent": "#3B82F6",
                    },
                )
                fig2.update_layout(xaxis_title="", yaxis_title="Amount (₹)")
                st.plotly_chart(fig2, width="stretch")
            else:
                st.info("No budgets configured for this month.")

        st.markdown("---")
        st.subheader("📋 Budget Target Breakdown")
        if not budget_summary.empty:
            st.dataframe(
                budget_summary.style.format(
                    {
                        "budget_limit": "₹{:,.2f}",
                        "actual_spent": "₹{:,.2f}",
                        "remaining_budget": "₹{:,.2f}",
                    }
                ),
                width="stretch",
            )
    else:
        st.warning("No data found in database. Please seed or add transactions.")

# ---------------------------------------------------------
# Screen 2: Log Single Transaction
# ---------------------------------------------------------
elif navigation == "➕ Log Transaction":
    st.markdown(
        '<div class="main-header">Log New Transaction</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Record an expense or income entry into the database</div>',
        unsafe_allow_html=True,
    )

    with st.form("add_tx_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            tx_date = st.date_input("Date", value=date.today())
            category = st.selectbox(
                "Category",
                [
                    "Food",
                    "Travel",
                    "Utilities",
                    "Entertainment",
                    "Shopping",
                    "Healthcare",
                    "Other",
                ],
            )
            amount = st.number_input(
                "Amount (₹)", min_value=1.0, step=50.0, format="%.2f"
            )

        with col_b:
            payment_mode = st.selectbox(
                "Payment Method", ["UPI", "Card", "Cash", "Net Banking"]
            )
            description = st.text_area(
                "Description", placeholder="e.g. Weekly grocery bills..."
            )

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("💾 Save Transaction")

        if submit_btn:
            tx = add_transaction(
                user_id=USER_ID,
                date=str(tx_date),
                category=category,
                amount=amount,
                description=description if description else None,
                payment_mode=payment_mode,
            )
            st.success(
                f"✅ Transaction logged successfully! Transaction ID: **{tx.id}**"
            )

# ---------------------------------------------------------
# Screen 3: Bulk CSV Statement Import
# ---------------------------------------------------------
elif navigation == "📥 Bulk CSV Import":
    st.markdown(
        '<div class="main-header">Bulk Statement Import</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Upload bank or credit card statement CSV files to import multiple entries at once</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "💡 **Expected CSV Header Format:** `date, category, amount, payment_mode, description`"
    )

    with st.form("bulk_import_form", clear_on_submit=False):
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
        submit_import = st.form_submit_button(
            "🚀 Confirm & Import All Records"
        )

    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)
            st.subheader("Preview Imported Data")
            st.dataframe(import_df, width="stretch")

            if submit_import:
                success_count = 0
                for _, row in import_df.iterrows():
                    add_transaction(
                        user_id=USER_ID,
                        date=str(row["date"]),
                        category=str(row["category"]),
                        amount=float(row["amount"]),
                        payment_mode=str(row.get("payment_mode", "UPI")),
                        description=str(
                            row.get("description", "Imported Statement")
                        ),
                    )
                    success_count += 1
                st.success(
                    f"✅ Successfully imported {success_count} transactions into SQLite!"
                )
        except Exception as e:
            st.error(f"❌ Error parsing CSV file: {e}")

# ---------------------------------------------------------
# Screen 4: Set Category Budget
# ---------------------------------------------------------
elif navigation == "🎯 Set Category Budget":
    st.markdown(
        '<div class="main-header">Set Monthly Category Budget</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Establish spending caps per category</div>',
        unsafe_allow_html=True,
    )

    with st.form("budget_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            category = st.selectbox(
                "Target Category",
                [
                    "Food",
                    "Travel",
                    "Utilities",
                    "Entertainment",
                    "Shopping",
                    "Healthcare",
                    "Other",
                ],
            )
            month = st.text_input("Target Month (YYYY-MM)", value="2026-10")

        with col_b:
            budget_limit = st.number_input(
                "Monthly Budget Cap (₹)",
                min_value=100.0,
                step=500.0,
                format="%.2f",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        submit_btn = st.form_submit_button("🎯 Set Budget Cap")

        if submit_btn:
            b = set_budget(
                user_id=USER_ID,
                category=category,
                month=month.strip(),
                amount=budget_limit,
            )
            st.success(
                f"✅ Budget target for **{b.category}** ({b.month}) set to **₹{b.budget_amount:,.2f}**!"
            )

# ---------------------------------------------------------
# Screen 5: Ledger Records & Actions (Edit / Delete / Export)
# ---------------------------------------------------------
elif navigation == "📋 Ledger Records & Actions":
    st.markdown(
        '<div class="main-header">Transaction History & Management</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Search, export (CSV/Excel), edit, or delete database entries</div>',
        unsafe_allow_html=True,
    )

    if not df.empty:
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])

        with col_s1:
            search_query = st.text_input(
                "🔍 Search by category or payment mode...", ""
            )

        filtered_df = df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["category"].str.contains(
                    search_query, case=False, na=False
                )
                | filtered_df["payment_mode"].str.contains(
                    search_query, case=False, na=False
                )
            ]

        # CSV Export Button
        with col_s2:
            st.markdown("<br>", unsafe_allow_html=True)
            csv_data = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export CSV",
                data=csv_data,
                file_name=f"expense_report_{selected_month}.csv",
                mime="text/csv",
            )

        # Excel Export Button (.xlsx)
        with col_s3:
            st.markdown("<br>", unsafe_allow_html=True)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                filtered_df.to_excel(
                    writer, index=False, sheet_name="Transactions"
                )
            excel_data = output.getvalue()

            st.download_button(
                label="📊 Export Excel",
                data=excel_data,
                file_name=f"expense_report_{selected_month}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        st.dataframe(
            filtered_df[
                [
                    "id",
                    "date",
                    "category",
                    "amount",
                    "payment_mode",
                    "description",
                ]
            ].style.format({"amount": "₹{:,.2f}"}),
            width="stretch",
        )

        st.markdown("---")
        col_edit, col_del = st.columns(2)

        # Edit Section
        with col_edit:
            st.subheader("✏️ Edit Transaction")
            with st.form("edit_tx_form"):
                edit_id = st.number_input(
                    "Transaction ID to Edit", min_value=1, step=1
                )
                new_category = st.selectbox(
                    "New Category",
                    [
                        "Food",
                        "Travel",
                        "Utilities",
                        "Entertainment",
                        "Shopping",
                        "Healthcare",
                        "Other",
                    ],
                )
                new_amount = st.number_input(
                    "New Amount (₹)", min_value=1.0, step=10.0, format="%.2f"
                )
                new_mode = st.selectbox(
                    "New Payment Mode", ["UPI", "Card", "Cash", "Net Banking"]
                )
                new_desc = st.text_input("New Description")

                edit_btn = st.form_submit_button("Update Record")
                if edit_btn:
                    if update_transaction(
                        int(edit_id),
                        category=new_category,
                        amount=new_amount,
                        payment_mode=new_mode,
                        description=new_desc,
                    ):
                        st.success(
                            f"✅ Transaction ID {edit_id} updated successfully!"
                        )
                        st.rerun()
                    else:
                        st.error(f"❌ Transaction ID {edit_id} not found.")

        # Delete Section
        with col_del:
            st.subheader("🗑️ Delete Transaction")
            with st.form("delete_tx_form"):
                delete_id = st.number_input(
                    "Transaction ID to Delete", min_value=1, step=1
                )
                delete_btn = st.form_submit_button("Delete Record")

                if delete_btn:
                    if delete_transaction(int(delete_id)):
                        st.success(
                            f"✅ Transaction ID {delete_id} deleted successfully!"
                        )
                        st.rerun()
                    else:
                        st.error(f"❌ Transaction ID {delete_id} not found.")
    else:
        st.info("No records present in the database.")