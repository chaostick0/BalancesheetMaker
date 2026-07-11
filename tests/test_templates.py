import os
import tempfile
import unittest

import app as flask_app
import database as db_module
from database import initialize_database, upsert_company


class TemplateRenderingTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        self.original_db_path = db_module.DB_PATH
        db_module.DB_PATH = self.db_path
        initialize_database(self.db_path)
        upsert_company(
            {
                "company_name": "Demo Ltd",
                "balance_sheet_date": "2024-03-31",
                "currency": "₹",
                "current_year": "2024",
                "previous_year": "2023",
            },
            db_path=self.db_path,
        )

    def tearDown(self):
        db_module.DB_PATH = self.original_db_path
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_report_renders_for_company_and_rows(self):
        client = flask_app.app.test_client()
        response = client.get("/report")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Demo Ltd", response.data)
        self.assertIn(b"Balance Sheet", response.data)


if __name__ == "__main__":
    unittest.main()
