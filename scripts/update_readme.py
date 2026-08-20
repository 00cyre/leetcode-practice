#!/usr/bin/env python3
"""Generate the README progress tracker from synced submission files."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"
CATALOG_PATH = ROOT / "data" / "neetcode150.json"
CONFIG_PATH = ROOT / "config" / "tracker.json"
START_MARKER = "<!-- progress-tracker:start -->"
END_MARKER = "<!-- progress-tracker:end -->"
DIFFICULTIES = ("Easy", "Medium", "Hard")
SUBMISSIONS_DIRECTORY = "Data Structures & Algorithms"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_submissions(root: Path = ROOT) -> dict[str, list[Path]]:
    submissions: dict[str, list[Path]] = defaultdict(list)
    submissions_root = root / SUBMISSIONS_DIRECTORY
    if not submissions_root.exists():
        return {}

    for problem_directory in submissions_root.iterdir():
        if not problem_directory.is_dir():
            continue
        for path in problem_directory.glob("submission-*.*"):
            if path.is_file():
                submissions[problem_directory.name].append(path.relative_to(root))
    return {slug: sorted(paths) for slug, paths in submissions.items()}


def parse_git_datetime(value: str, timezone: ZoneInfo) -> date:
    return datetime.fromisoformat(value).astimezone(timezone).date()


def git_submission_history(
    root: Path, timezone: ZoneInfo
) -> tuple[set[date], dict[str, date]]:
    command = [
        "git",
        "log",
        "--format=@@%aI",
        "--name-only",
        "--",
        ":(glob)Data Structures & Algorithms/*/submission-*.*",
    ]
    result = subprocess.run(
        command,
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )

    activity_dates: set[date] = set()
    latest_by_slug: dict[str, date] = {}
    commit_date: date | None = None

    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if line.startswith("@@"):
            commit_date = parse_git_datetime(line[2:], timezone)
            activity_dates.add(commit_date)
            continue
        if not line or commit_date is None or not Path(line).name.startswith("submission-"):
            continue
        slug = Path(line).parent.name
        latest_by_slug.setdefault(slug, commit_date)

    return activity_dates, latest_by_slug


def calculate_streaks(activity_dates: set[date]) -> tuple[int, int]:
    if not activity_dates:
        return 0, 0

    ordered = sorted(activity_dates)
    best = 1
    run = 1
    for previous, current in zip(ordered, ordered[1:]):
        if current == previous + timedelta(days=1):
            run += 1
            best = max(best, run)
        else:
            run = 1

    latest_streak = 1
    cursor = ordered[-1]
    while cursor - timedelta(days=1) in activity_dates:
        latest_streak += 1
        cursor -= timedelta(days=1)
    return latest_streak, best


def progress_bar(completed: int, total: int, width: int = 14) -> str:
    filled = round(width * completed / total) if total else 0
    if completed and not filled:
        filled = 1
    return "█" * filled + "░" * (width - filled)


def percent(completed: int, total: int) -> str:
    return f"{(100 * completed / total):.1f}%" if total else "0.0%"


def markdown_path(path: Path) -> str:
    return quote(path.as_posix(), safe="/")


def table_text(value: str) -> str:
    return value.replace("|", "\\|")


def render_tracker(
    catalog: list[dict[str, str]],
    submissions: dict[str, list[Path]],
    activity_dates: set[date],
    latest_by_slug: dict[str, date],
) -> str:
    catalog_by_slug = {problem["slug"]: problem for problem in catalog}
    solved = set(submissions) & set(catalog_by_slug)
    uncatalogued = set(submissions) - set(catalog_by_slug)
    total_submissions = sum(len(paths) for paths in submissions.values())
    latest_streak, best_streak = calculate_streaks(activity_dates)

    difficulty_totals = {
        difficulty: sum(problem["difficulty"] == difficulty for problem in catalog)
        for difficulty in DIFFICULTIES
    }
    difficulty_solved = {
        difficulty: sum(
            catalog_by_slug[slug]["difficulty"] == difficulty for slug in solved
        )
        for difficulty in DIFFICULTIES
    }

    grouped: dict[str, list[dict[str, str]]] = {}
    for problem in catalog:
        grouped.setdefault(problem["category"], []).append(problem)

    latest_activity = max(activity_dates).isoformat() if activity_dates else "—"
    lines = [
        START_MARKER,
        "## Progress",
        "",
        f"**{len(solved)} / {len(catalog)} solved** · `{progress_bar(len(solved), len(catalog), 20)}` · **{percent(len(solved), len(catalog))}**",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Unique roadmap problems | **{len(solved)} / {len(catalog)}** |",
        f"| Synced submission files | **{total_submissions}** |",
        f"| Remaining problems | **{len(catalog) - len(solved)}** |",
        f"| Latest submission streak | **{latest_streak} day{'s' if latest_streak != 1 else ''}** |",
        f"| Best activity streak | **{best_streak} day{'s' if best_streak != 1 else ''}** |",
        f"| Latest submission activity | **{latest_activity}** |",
        "",
        "> Counts come from folder slugs under `Data Structures & Algorithms`. Activity streaks and last-active dates come only from commits that changed submission files.",
        "",
        "### Difficulty",
        "",
        "| Difficulty | Progress | Completed |",
        "|---|---|---:|",
    ]

    for difficulty in DIFFICULTIES:
        completed = difficulty_solved[difficulty]
        total = difficulty_totals[difficulty]
        lines.append(
            f"| {difficulty} | `{progress_bar(completed, total)}` {percent(completed, total)} | **{completed} / {total}** |"
        )

    lines.extend(
        [
            "",
            "## Roadmap overview",
            "",
            "| Topic | Progress | Completed | Next unsolved |",
            "|---|---|---:|---|",
        ]
    )

    for category, problems in grouped.items():
        completed = sum(problem["slug"] in solved for problem in problems)
        next_problem = next(
            (problem for problem in problems if problem["slug"] not in solved), None
        )
        next_link = (
            f"[{table_text(next_problem['title'])}]({next_problem['url']})"
            if next_problem
            else "Complete ✅"
        )
        lines.append(
            f"| {table_text(category)} | `{progress_bar(completed, len(problems), 10)}` | **{completed} / {len(problems)}** | {next_link} |"
        )

    lines.extend(["", "## Solved problems", ""])
    if solved:
        lines.extend(
            [
                "| Problem | Topic | Difficulty | Submissions | Last activity |",
                "|---|---|---|---:|---:|",
            ]
        )
        for problem in catalog:
            slug = problem["slug"]
            if slug not in solved:
                continue
            solution_dir = submissions[slug][0].parent
            lines.append(
                "| "
                f"[{table_text(problem['title'])}]({problem['url']}) "
                f"([solutions]({markdown_path(solution_dir)})) | "
                f"{table_text(problem['category'])} | {problem['difficulty']} | "
                f"{len(submissions[slug])} | {latest_by_slug.get(slug, '—')} |"
            )
    else:
        lines.append("No synced roadmap submissions yet.")

    if uncatalogued:
        lines.extend(
            [
                "",
                "### Other synced problems",
                "",
                "These folders are tracked as submissions but are not part of the current NeetCode 150 catalog:",
                "",
            ]
        )
        for slug in sorted(uncatalogued):
            solution_dir = submissions[slug][0].parent
            lines.append(
                f"- [{slug}]({markdown_path(solution_dir)}) — {len(submissions[slug])} submission(s)"
            )

    lines.extend(["", "## Full NeetCode 150 checklist", ""])
    for category, problems in grouped.items():
        completed = sum(problem["slug"] in solved for problem in problems)
        lines.extend(
            [
                "<details>",
                f"<summary><strong>{category}</strong> — {completed}/{len(problems)}</summary>",
                "",
            ]
        )
        for problem in problems:
            slug = problem["slug"]
            checked = "x" if slug in solved else " "
            suffix = f" · {problem['difficulty']}"
            if slug in solved:
                solution_dir = submissions[slug][0].parent
                suffix += f" · [solutions]({markdown_path(solution_dir)})"
            lines.append(
                f"- [{checked}] [{problem['title']}]({problem['url']}){suffix}"
            )
        lines.extend(["", "</details>", ""])

    lines.extend([END_MARKER, ""])
    return "\n".join(lines)


def replace_generated_section(readme: str, generated: str) -> str:
    if START_MARKER not in readme or END_MARKER not in readme:
        raise RuntimeError(
            f"README.md must contain {START_MARKER} and {END_MARKER} markers"
        )
    before = readme.split(START_MARKER, 1)[0]
    after = readme.split(END_MARKER, 1)[1]
    return before + generated.rstrip("\n") + after


def build_readme() -> str:
    catalog_document = load_json(CATALOG_PATH)
    config = load_json(CONFIG_PATH)
    timezone = ZoneInfo(str(config.get("timezone", "UTC")))
    activity_dates, latest_by_slug = git_submission_history(ROOT, timezone)

    current_readme = README_PATH.read_text(encoding="utf-8")
    generated = render_tracker(
        catalog_document["problems"],
        discover_submissions(ROOT),
        activity_dates,
        latest_by_slug,
    )
    return replace_generated_section(current_readme, generated)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of writing when README.md is out of date",
    )
    args = parser.parse_args()

    rendered = build_readme()
    current = README_PATH.read_text(encoding="utf-8")
    if args.check:
        if current != rendered:
            print("README.md progress tracker is out of date", file=sys.stderr)
            return 1
        print("README.md progress tracker is current")
        return 0

    if current == rendered:
        print("README.md is already current")
        return 0
    README_PATH.write_text(rendered, encoding="utf-8")
    print("Updated README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
