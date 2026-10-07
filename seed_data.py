
from repository import add_transaction, create_user, set_budget


def seed():
    print("Populating database with sample data...")

    # Create user
    user = create_user(name="Raajvikram", email="raaj@example.com")
    print(f"User created: {user.name} (ID: {user.id})")

    # Set sample monthly budgets for October 2026
    set_budget(
        user_id=user.id, category="Food", month="2026-10", amount=5000.0
    )
    set_budget(
        user_id=user.id, category="Travel", month="2026-10", amount=2000.0
    )
    set_budget(
        user_id=user.id, category="Utilities", month="2026-10", amount=1500.0
    )

    # Add sample transactions
    add_transaction(
        user.id,
        "2026-10-01",
        "Food",
        450.0,
        "Grocery store",
        payment_mode="UPI",
    )
    add_transaction(
        user.id, "2026-10-02", "Travel", 120.0, "Bus ticket", payment_mode="Cash"
    )
    add_transaction(
        user.id,
        "2026-10-03",
        "Food",
        250.0,
        "Lunch at canteen",
        payment_mode="UPI",
    )
    add_transaction(
        user.id,
        "2026-10-04",
        "Utilities",
        800.0,
        "Electricity bill",
        payment_mode="Card",
    )

    print("Sample data successfully inserted!")


if __name__ == "__main__":
    seed()