# analytics.py
import pandas as pd
from repository import get_budgets_for_month, get_user_transactions


def get_transactions_df(
    user_id: int, start_date: str = None, end_date: str = None
) -> pd.DataFrame:
    """Fetches user transactions from DB and loads them into a Pandas DataFrame."""
    rows = get_user_transactions(user_id, start_date, end_date)
    data = [
        {
            "id": r.id,
            "date": r.date,
            "category": r.category,
            "amount": r.amount,
            "description": r.description,
            "payment_mode": r.payment_mode,
        }
        for r in rows
    ]
    df = pd.DataFrame(data)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def category_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates total spend and percentage by category."""
    if df.empty:
        return pd.DataFrame()

    grouped = (
        df.groupby("category")["amount"]
        .sum()
        .reset_index(name="total_spent")
        .sort_values(by="total_spent", ascending=False)
    )

    total_spend = grouped["total_spent"].sum()
    grouped["percentage"] = (grouped["total_spent"] / total_spend * 100).round(
        2
    )
    return grouped


def budget_vs_actual(
    user_id: int, month: str, df: pd.DataFrame
) -> pd.DataFrame:
    """Compares actual category spending against monthly budget targets."""
    budgets = get_budgets_for_month(user_id, month)
    budget_df = pd.DataFrame(
        [
            {"category": b.category, "budget_limit": b.budget_amount}
            for b in budgets
        ]
    )

    if df.empty:
        return budget_df

    # Filter transactions for the requested month (YYYY-MM)
    monthly_df = df[df["date"].dt.strftime("%Y-%m") == month]
    spent_df = (
        monthly_df.groupby("category")["amount"]
        .sum()
        .reset_index(name="actual_spent")
    )

    # Merge budget limits with actual spent
    merged = pd.merge(budget_df, spent_df, on="category", how="outer").fillna(0)
    merged["remaining_budget"] = merged["budget_limit"] - merged["actual_spent"]
    merged["status"] = merged.apply(
        lambda row: "Exceeded" if row["remaining_budget"] < 0 else "Within Budget",
        axis=1,
    )
    return merged


if __name__ == "__main__":
    USER_ID = 1
    MONTH = "2026-10"

    print("--- 1. Transaction DataFrame ---")
    tx_df = get_transactions_df(USER_ID)
    print(tx_df[["date", "category", "amount", "payment_mode"]], "\n")

    print("--- 2. Category Breakdown ---")
    cat_df = category_breakdown(tx_df)
    print(cat_df, "\n")

    print("--- 3. Budget vs Actual ---")
    budget_summary = budget_vs_actual(USER_ID, MONTH, tx_df)
    print(budget_summary)