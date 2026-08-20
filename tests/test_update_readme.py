from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "update_readme.py"
SPEC = importlib.util.spec_from_file_location("update_readme", MODULE_PATH)
assert SPEC and SPEC.loader
update_readme = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update_readme)


class ProgressTrackerTests(unittest.TestCase):
    def test_catalog_matches_neetcode_150_totals(self) -> None:
        catalog_path = Path(__file__).resolve().parents[1] / "data" / "neetcode150.json"
        problems = json.loads(catalog_path.read_text(encoding="utf-8"))["problems"]

        self.assertEqual(len(problems), 150)
        self.assertEqual(
            {
                difficulty: sum(
                    problem["difficulty"] == difficulty for problem in problems
                )
                for difficulty in ("Easy", "Medium", "Hard")
            },
            {"Easy": 28, "Medium": 101, "Hard": 21},
        )

    def test_streaks_include_historical_neetcode_activity(self) -> None:
        current, best = update_readme.calculate_streaks(
            {date(2026, 8, 9), date(2026, 8, 10), date(2026, 8, 20)},
            date(2026, 8, 20),
        )
        self.assertEqual(current, 1)
        self.assertEqual(best, 2)

    def test_current_streak_expires_after_a_missed_day(self) -> None:
        current, best = update_readme.calculate_streaks(
            {date(2026, 8, 9), date(2026, 8, 10)},
            date(2026, 8, 20),
        )
        self.assertEqual(current, 0)
        self.assertEqual(best, 2)

    def test_discovers_and_groups_submission_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            problem = root / "Data Structures & Algorithms" / "two-integer-sum"
            problem.mkdir(parents=True)
            (problem / "submission-0.py").write_text("pass\n", encoding="utf-8")
            (problem / "submission-1.py").write_text("pass\n", encoding="utf-8")
            (root / "not-a-submission.py").write_text("pass\n", encoding="utf-8")

            submissions = update_readme.discover_submissions(root)

        self.assertEqual(list(submissions), ["two-integer-sum"])
        self.assertEqual(len(submissions["two-integer-sum"]), 2)

    def test_render_marks_solved_and_remaining_problems(self) -> None:
        catalog = [
            {
                "slug": "one",
                "title": "One",
                "category": "Arrays",
                "difficulty": "Easy",
                "url": "https://example.test/one",
            },
            {
                "slug": "two",
                "title": "Two",
                "category": "Arrays",
                "difficulty": "Medium",
                "url": "https://example.test/two",
            },
        ]
        rendered = update_readme.render_tracker(
            catalog,
            {"one": [Path("solutions/one/submission-0.py")]},
            {date(2026, 8, 20)},
            {"one": date(2026, 8, 20)},
            date(2026, 8, 20),
        )

        self.assertIn("**1 / 2 solved**", rendered)
        self.assertIn("- [x] [One]", rendered)
        self.assertIn("- [ ] [Two]", rendered)

    def test_progress_bar_shows_small_nonzero_progress(self) -> None:
        self.assertTrue(update_readme.progress_bar(1, 150, 20).startswith("█"))


if __name__ == "__main__":
    unittest.main()
