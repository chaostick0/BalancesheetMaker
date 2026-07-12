import pathlib
import unittest


class ThemeCssTests(unittest.TestCase):
    def test_light_and_dark_theme_variables_cover_semantic_tokens(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        base_css = (root / "static" / "css" / "base.css").read_text()
        dark_css = (root / "static" / "css" / "dark.css").read_text()

        required_tokens = [
            "--bg",
            "--surface",
            "--surface-strong",
            "--text",
            "--muted",
            "--border",
            "--accent",
            "--success",
            "--danger",
            "--icon-color",
            "--dropdown-bg",
            "--dropdown-text",
            "--pill-bg",
            "--overlay-bg",
        ]

        for token in required_tokens:
            self.assertIn(token, base_css)

        for token in required_tokens:
            self.assertIn(token, dark_css)


if __name__ == "__main__":
    unittest.main()
