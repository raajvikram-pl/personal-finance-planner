from db import Base, engine
from models import Budget, Transaction, User


def init_database():
    print("Initializing SQLite database...")
    Base.metadata.create_all(bind=engine)
    print("Database successfully initialized! Created 'expenses.db'.")


if __name__ == "__main__":
    init_database()