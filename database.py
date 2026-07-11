import sqlite3

DEFAULT_BALANCE_SHEET_ITEMS = [
    ("ASSETS", "Current Assets", "Cash and Cash Equivalents", "25", 0, 0),
    ("ASSETS", "Current Assets", "Trade Receivables", "24", 0, 0),
    ("ASSETS", "Current Assets", "Inventories", "23", 0, 0),
    ("ASSETS", "Current Assets", "Other Current Assets", "27", 0, 0),
    ("ASSETS", "Non Current Assets", "Property Plant & Equipment", "13", 0, 0),
    ("ASSETS", "Non Current Assets", "Tangible Assets", "14", 0, 0),
    ("ASSETS", "Non Current Assets", "Intangible Assets", "15", 0, 0),
    ("LIABILITIES", "Shareholders Funds", "Share Capital", "1", 0, 0),
    ("LIABILITIES", "Shareholders Funds", "Reserves and Surplus", "2", 0, 0),
    ("LIABILITIES", "Current Liabilities", "Trade Payables", "10", 0, 0),
    ("LIABILITIES", "Current Liabilities", "Short Term Borrowings", "9", 0, 0),
    ("LIABILITIES", "Non Current Liabilities", "Long Term Borrowings", "5", 0, 0),
]


def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company (
            id INTEGER PRIMARY KEY,
            company_name TEXT,
            balance_sheet_date TEXT,
            currency TEXT,
            current_year TEXT,
            previous_year TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balance_sheet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT,
            group_name TEXT,
            item_name TEXT,
            note_no TEXT,
            current_amount REAL DEFAULT 0,
            previous_amount REAL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def seed_balance_sheet():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM balance_sheet")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            """
                INSERT INTO balance_sheet(
                    section,
                    group_name,
                    item_name,
                    note_no,
                    current_amount,
                    previous_amount
                ) VALUES (?,?,?,?,?,?)
            """,
            DEFAULT_BALANCE_SHEET_ITEMS,
        )
        conn.commit()
    conn.close()


def initialize_database():
    create_database()
    seed_balance_sheet()


if __name__ == "__main__":
    initialize_database()
    print("Database created and seeded successfully.")
