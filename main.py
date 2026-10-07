# main.py
import sys
from analytics import budget_vs_actual, category_breakdown, get_transactions_df
from repository import add_transaction, create_user, set_budget
from visualize import plot_budget_vs_actual, plot_category_pie


def print_menu():
    print("\n" + "=" * 40)
    print("   EXPENSE & BUDGET ANALYTICS SYSTEM   ")
    print("=" * 40)
    print("1. Add New Transaction")
    print("2. Set Monthly Category Budget")
    print("3. View Recent Transactions")
    print("4. View Category Spending Breakdown")
    print("5. View Budget vs. Actual Report")
    print("6. Show Expense Charts (Pie & Bar)")
    print("7. Exit")
    print("=" * 40)


def main():
    # Using default demo user (ID: 1) created in seed_data.py
    user_id = 1

    while True:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            print("\n--- Add New Transaction ---")
            date = input("Enter date (YYYY-MM-DD): ").strip()
            category = input(
                "Enter category (e.g. Food, Travel, Utilities): "
            ).strip()
            amount = float(input("Enter amount (₹): ").strip())
            desc = input("Enter description (optional): ").strip() or None
            mode = (
                input(
                    "Enter payment mode (UPI, Cash, Card - optional): "
                ).strip()
                or None
            )

            tx = add_transaction(
                user_id, date, category, amount, desc, mode
            )
            print(f"✅ Transaction added successfully! ID: {tx.id}")

        elif choice == "2":
            print("\n--- Set Monthly Category Budget ---")
            category = input("Enter category: ").strip()
            month = input("Enter month (YYYY-MM): ").strip()
            amount = float(input("Enter budget limit (₹): ").strip())

            b = set_budget(user_id, category, month, amount)
            print(
                f"✅ Budget set for {b.category} ({b.month}): ₹{b.budget_amount}"
            )

        elif choice == "3":
            print("\n--- Recent Transactions ---")
            df = get_transactions_df(user_id)
            if df.empty:
                print("No transactions found.")
            else:
                print(df[["id", "date", "category", "amount", "payment_mode"]])

        elif choice == "4":
            print("\n--- Category Spending Breakdown ---")
            df = get_transactions_df(user_id)
            cat_df = category_breakdown(df)
            if cat_df.empty:
                print("No data available.")
            else:
                print(cat_df.to_string(index=False))

        elif choice == "5":
            print("\n--- Budget vs. Actual Report ---")
            month = input("Enter month to analyze (YYYY-MM): ").strip()
            df = get_transactions_df(user_id)
            report = budget_vs_actual(user_id, month, df)
            if report.empty:
                print("No budget records found for this month.")
            else:
                print(report.to_string(index=False))

        elif choice == "6":
            print("\n--- Displaying Visual Charts ---")
            month = input("Enter month for visual charts (YYYY-MM): ").strip()
            df = get_transactions_df(user_id)
            cat_df = category_breakdown(df)
            b_df = budget_vs_actual(user_id, month, df)

            print("Opening Pie Chart... (Close chart window to continue)")
            plot_category_pie(cat_df)

            print("Opening Bar Chart... (Close chart window to continue)")
            plot_budget_vs_actual(b_df)

        elif choice == "7":
            print("\nExiting Expense Analytics App. See you next time!")
            sys.exit()

        else:
            print("❌ Invalid option! Please select a number between 1 and 7.")


if __name__ == "__main__":
    main()