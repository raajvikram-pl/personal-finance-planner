# visualize.py
import matplotlib.pyplot as plt
import seaborn as sns
from analytics import budget_vs_actual, category_breakdown, get_transactions_df

# Set visual style
sns.set_theme(style="whitegrid")


def plot_category_pie(cat_df):
    """Generates a pie chart of spending by category."""
    if cat_df.empty:
        print("No data available to plot.")
        return

    plt.figure(figsize=(7, 7))
    plt.pie(
        cat_df["total_spent"],
        labels=cat_df["category"],
        autopct="%1.1f%%",
        startangle=140,
        colors=sns.color_palette("pastel"),
    )
    plt.title("Expense Breakdown by Category")
    plt.tight_layout()
    plt.show()


def plot_budget_vs_actual(budget_df):
    """Generates a side-by-side bar chart comparing Budget vs. Actual Spent."""
    if budget_df.empty:
        print("No budget data to plot.")
        return

    # Reshape data for Seaborn barplot
    melted_df = budget_df.melt(
        id_vars=["category"],
        value_vars=["budget_limit", "actual_spent"],
        var_name="Type",
        value_name="Amount",
    )
    melted_df["Type"] = melted_df["Type"].map(
        {"budget_limit": "Budget Limit", "actual_spent": "Actual Spent"}
    )

    plt.figure(figsize=(8, 5))
    sns.barplot(
        data=melted_df, x="category", y="Amount", hue="Type", palette="Set2"
    )
    plt.title("Budget vs Actual Spending")
    plt.xlabel("Category")
    plt.ylabel("Amount (₹)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    USER_ID = 1
    MONTH = "2026-10"

    tx_df = get_transactions_df(USER_ID)
    cat_df = category_breakdown(tx_df)
    budget_df = budget_vs_actual(USER_ID, MONTH, tx_df)

    # Render charts
    print("Displaying Category Pie Chart...")
    plot_category_pie(cat_df)

    print("Displaying Budget vs Actual Bar Chart...")
    plot_budget_vs_actual(budget_df)