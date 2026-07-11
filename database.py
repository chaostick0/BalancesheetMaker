import csv
import sqlite3
from io import StringIO
from pathlib import Path

DB_PATH = Path(__file__).with_name("database.db")

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


def get_connection(db_path=None):
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def normalize_amount(value):
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return 0.0
        cleaned = text.replace(",", "")
        try:
            return float(cleaned)
        except ValueError as exc:
            raise ValueError("Please enter valid numeric values.") from exc
    raise ValueError("Please enter valid numeric values.")


def round_amount(value):
    return round(normalize_amount(value), 2)


def validate_company_data(data):
    required_fields = ["company_name", "balance_sheet_date", "currency", "current_year", "previous_year"]
    missing = [field for field in required_fields if not str(data.get(field, "")).strip()]
    if missing:
        raise ValueError("Please fill in all company details.")
    return data


def create_database(db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS company (
                id INTEGER PRIMARY KEY,
                company_name TEXT,
                balance_sheet_date TEXT,
                currency TEXT,
                current_year TEXT,
                previous_year TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS balance_sheet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                section TEXT,
                group_name TEXT,
                item_name TEXT,
                note_no TEXT,
                current_amount REAL DEFAULT 0,
                previous_amount REAL DEFAULT 0
            )
            """
        )
        conn.commit()


def seed_balance_sheet(db_path=None):
    with get_connection(db_path) as conn:
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


def initialize_database(db_path=None):
    create_database(db_path)
    seed_balance_sheet(db_path)


def upsert_company(data, db_path=None):
    validated = validate_company_data(data)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        existing = cursor.execute("SELECT id FROM company LIMIT 1").fetchone()
        if existing:
            cursor.execute(
                """
                UPDATE company
                SET company_name=?, balance_sheet_date=?, currency=?, current_year=?, previous_year=?
                WHERE id=?
                """,
                (
                    validated["company_name"],
                    validated["balance_sheet_date"],
                    validated["currency"],
                    validated["current_year"],
                    validated["previous_year"],
                    existing["id"],
                ),
            )
            company_id = existing["id"]
        else:
            cursor.execute(
                """
                INSERT INTO company (company_name, balance_sheet_date, currency, current_year, previous_year)
                VALUES (?,?,?,?,?)
                """,
                (
                    validated["company_name"],
                    validated["balance_sheet_date"],
                    validated["currency"],
                    validated["current_year"],
                    validated["previous_year"],
                ),
            )
            company_id = cursor.lastrowid
        conn.commit()
    return company_id


def get_company(db_path=None):
    with get_connection(db_path) as conn:
        row = conn.execute("SELECT * FROM company LIMIT 1").fetchone()
        return dict(row) if row else None


def get_balance_sheet_rows(section=None, db_path=None):
    with get_connection(db_path) as conn:
        query = "SELECT * FROM balance_sheet"
        params = []
        if section:
            query += " WHERE section = ?"
            params.append(section)
        query += " ORDER BY section, group_name, note_no"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_balance_sheet_totals(section, db_path=None):
    with get_connection(db_path) as conn:
        row = conn.execute(
            "SELECT SUM(current_amount) AS current_amount, SUM(previous_amount) AS previous_amount FROM balance_sheet WHERE section = ?",
            (section,),
        ).fetchone()
        return {
            "current_amount": round_amount(row["current_amount"] or 0),
            "previous_amount": round_amount(row["previous_amount"] or 0),
        }


def save_balance_sheet_values(section, payload, db_path=None):
    with get_connection(db_path) as conn:
        for item_id, values in payload.items():
            current_amount = round_amount(values.get("current_amount", 0))
            previous_amount = round_amount(values.get("previous_amount", 0))
            conn.execute(
                "UPDATE balance_sheet SET current_amount=?, previous_amount=? WHERE id=? AND section=?",
                (current_amount, previous_amount, item_id, section),
            )
        conn.commit()


def insert_balance_sheet_row(section, group_name, item_name, note_no, current_amount=0, previous_amount=0, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO balance_sheet (section, group_name, item_name, note_no, current_amount, previous_amount)
            VALUES (?,?,?,?,?,?)
            """,
            (section, group_name, item_name, note_no, round_amount(current_amount), round_amount(previous_amount)),
        )
        conn.commit()
        return cursor.lastrowid


def reset_balance_sheet_section(section, db_path=None):
    with get_connection(db_path) as conn:
        conn.execute(
            "UPDATE balance_sheet SET current_amount=0, previous_amount=0 WHERE section=?",
            (section,),
        )
        conn.commit()


def clear_balance_sheet(db_path=None):
    with get_connection(db_path) as conn:
        conn.execute("DELETE FROM balance_sheet")
        conn.commit()


def insert_balance_sheet_row(section, group_name, item_name, note_no, current_amount=0, previous_amount=0, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO balance_sheet (section, group_name, item_name, note_no, current_amount, previous_amount)
            VALUES (?,?,?,?,?,?)
            """,
            (section, group_name, item_name, note_no, round_amount(current_amount), round_amount(previous_amount)),
        )
        conn.commit()
        return cursor.lastrowid


def delete_balance_sheet_row(item_id, db_path=None):
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM balance_sheet WHERE id=?", (item_id,))
        conn.commit()
        return cursor.rowcount > 0


def import_balance_sheet_from_csv(csv_text, db_path=None):
    rows = []
    reader = csv.DictReader(StringIO(csv_text))
    for row in reader:
        rows.append(
            (
                row.get("section", "").strip(),
                row.get("group_name", "").strip(),
                row.get("item_name", "").strip(),
                row.get("note_no", "").strip(),
                round_amount(row.get("current_amount", 0) or 0),
                round_amount(row.get("previous_amount", 0) or 0),
            )
        )
    if not rows:
        return 0
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO balance_sheet (section, group_name, item_name, note_no, current_amount, previous_amount)
            VALUES (?,?,?,?,?,?)
            """,
            rows,
        )
        conn.commit()
    return len(rows)


if __name__ == "__main__":
    initialize_database()
    print("Database created and seeded successfully.")
