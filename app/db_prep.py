from app.db import init_db

if __name__ == "__main__":
    print("Initializing database schema...")
    init_db()
    print("Database is ready!")
