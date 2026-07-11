import os
import sqlite3
import tempfile
import unittest

from database import (
    delete_balance_sheet_row,
    import_balance_sheet_from_csv,
    insert_balance_sheet_row,
    normalize_amount,
    upsert_company,
)


class DatabaseHelpersTests(unittest.TestCase):
    def test_normalize_amount_parses_numeric_strings(self):
        self.assertEqual(normalize_amount("125.50"), 125.5)
        self.assertEqual(normalize_amount(10), 10.0)

    def test_normalize_amount_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            normalize_amount("abc")

    def test_upsert_company_keeps_single_record(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE company (
                    id INTEGER PRIMARY KEY,
                    company_name TEXT,
                    balance_sheet_date TEXT,
                    currency TEXT,
                    current_year TEXT,
                    previous_year TEXT
                )
                """
            )
            conn.commit()
            conn.close()

            upsert_company(
                {
                    "company_name": "Demo Ltd",
                    "balance_sheet_date": "2024-03-31",
                    "currency": "₹",
                    "current_year": "2024",
                    "previous_year": "2023",
                },
                db_path=db_path,
            )
            upsert_company(
                {
                    "company_name": "Demo Ltd 2",
                    "balance_sheet_date": "2024-03-31",
                    "currency": "$",
                    "current_year": "2025",
                    "previous_year": "2024",
                },
                db_path=db_path,
            )

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM company")
            count = cursor.fetchone()[0]
            cursor.execute("SELECT company_name, currency FROM company WHERE id=1")
            company = cursor.fetchone()
            conn.close()

            self.assertEqual(count, 1)
            self.assertEqual(company[0], "Demo Ltd 2")
            self.assertEqual(company[1], "$")
        finally:
            os.remove(db_path)

    def test_import_balance_sheet_from_csv_creates_rows(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE balance_sheet (
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
            conn.close()

            csv_data = "section,group_name,item_name,note_no,current_amount,previous_amount\nASSETS,Current Assets,Cash,1,100,80\n"
            imported = import_balance_sheet_from_csv(csv_data, db_path=db_path)

            self.assertEqual(imported, 1)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM balance_sheet")
            count = cursor.fetchone()[0]
            cursor.execute("SELECT item_name, current_amount FROM balance_sheet WHERE id=1")
            row = cursor.fetchone()
            conn.close()

            self.assertEqual(count, 1)
            self.assertEqual(row[0], "Cash")
            self.assertEqual(row[1], 100.0)
        finally:
            os.remove(db_path)

    def test_insert_and_delete_balance_sheet_row(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE balance_sheet (
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
            conn.close()

            row_id = insert_balance_sheet_row("ASSETS", "Current Assets", "Inventory", "2", 50, 40, db_path=db_path)
            self.assertGreater(row_id, 0)
            deleted = delete_balance_sheet_row(row_id, db_path=db_path)
            self.assertTrue(deleted)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM balance_sheet")
            count = cursor.fetchone()[0]
            conn.close()
            self.assertEqual(count, 0)
        finally:
            os.remove(db_path)


if __name__ == "__main__":
    unittest.main()
