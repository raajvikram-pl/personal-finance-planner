# repository.py
from db import get_session
from models import Budget, Transaction


def get_user_transactions(
    user_id: int, start_date: str = None, end_date: str = None
):
    """Fetch all transactions for a given user with optional date range filtering."""
    session = get_session()
    try:
        query = session.query(Transaction).filter(
            Transaction.user_id == user_id
        )
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        return query.all()
    finally:
        session.close()


def get_budgets_for_month(user_id: int, month: str):
    """Fetch all budgets configured for a user for a specific month (YYYY-MM)."""
    session = get_session()
    try:
        return (
            session.query(Budget)
            .filter(Budget.user_id == user_id, Budget.month == month)
            .all()
        )
    finally:
        session.close()


def add_transaction(
    user_id: int,
    date: str,
    category: str,
    amount: float,
    description: str = None,
    payment_mode: str = "UPI",
):
    """Add a single new transaction to the database."""
    session = get_session()
    try:
        tx = Transaction(
            user_id=user_id,
            date=date,
            category=category,
            amount=amount,
            description=description,
            payment_mode=payment_mode,
        )
        session.add(tx)
        session.commit()
        session.refresh(tx)
        return tx
    finally:
        session.close()


def set_budget(user_id: int, category: str, month: str, amount: float):
    """Set or update a monthly category budget limit."""
    session = get_session()
    try:
        budget = (
            session.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category == category,
                Budget.month == month,
            )
            .first()
        )

        if budget:
            budget.budget_amount = amount
        else:
            budget = Budget(
                user_id=user_id,
                category=category,
                month=month,
                budget_amount=amount,
            )
            session.add(budget)

        session.commit()
        session.refresh(budget)
        return budget
    finally:
        session.close()


def update_transaction(
    tx_id: int,
    date: str = None,
    category: str = None,
    amount: float = None,
    payment_mode: str = None,
    description: str = None,
):
    """Update existing transaction details by ID."""
    session = get_session()
    try:
        tx = session.query(Transaction).filter(Transaction.id == tx_id).first()
        if tx:
            if date:
                tx.date = date
            if category:
                tx.category = category
            if amount is not None:
                tx.amount = amount
            if payment_mode:
                tx.payment_mode = payment_mode
            if description is not None:
                tx.description = description
            session.commit()
            return True
        return False
    finally:
        session.close()


def delete_transaction(tx_id: int):
    """Delete a transaction record by ID."""
    session = get_session()
    try:
        tx = session.query(Transaction).filter(Transaction.id == tx_id).first()
        if tx:
            session.delete(tx)
            session.commit()
            return True
        return False
    finally:
        session.close()