#!/usr/bin/env python3
"""Refresh the checked-in NeetCode 150 catalog from NeetCode's public site data."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "neetcode150.json"
PRACTICE_URL = "https://neetcode.io/practice/practice/neetcode150"
USER_AGENT = "leetcode-practice-roadmap-refresh/1.0"

SCRIPT_RE = re.compile(r'<script[^>]+src="([^"]*main\.[^"]+\.js)"')
OBJECT_RE = re.compile(r"\{problem:(?:\\.|[^{}])*?\}")


def fetch_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def js_string_field(source: str, name: str) -> str | None:
    match = re.search(rf'{re.escape(name)}:"((?:\\.|[^"\\])*)"', source)
    if not match:
        return None
    return json.loads(f'"{match.group(1)}"')


def extract_catalog(bundle: str, bundle_url: str) -> dict[str, object]:
    problems: list[dict[str, str]] = []

    for candidate in OBJECT_RE.findall(bundle):
        if "neetcode150:!0" not in candidate:
            continue

        title = js_string_field(candidate, "problem")
        category = js_string_field(candidate, "pattern")
        difficulty = js_string_field(candidate, "difficulty")
        slug = js_string_field(candidate, "ncLink")
        leetcode_id = js_string_field(candidate, "code")
        if not all((title, category, difficulty, slug, leetcode_id)):
            continue

        clean_slug = slug.rstrip("/")
        problems.append(
            {
                "slug": clean_slug,
                "title": title,
                "category": category,
                "difficulty": difficulty,
                "leetcode_id": leetcode_id,
                "url": f"https://neetcode.io/problems/{clean_slug}/question",
            }
        )

    slugs = [problem["slug"] for problem in problems]
    if len(problems) != 150:
        raise RuntimeError(f"Expected 150 NeetCode problems, found {len(problems)}")
    if len(slugs) != len(set(slugs)):
        raise RuntimeError("The NeetCode catalog contains duplicate problem slugs")

    return {
        "name": "NeetCode 150",
        "source": PRACTICE_URL,
        "source_bundle": bundle_url,
        "problems": problems,
    }


def render_catalog() -> str:
    practice_html = fetch_text(PRACTICE_URL)
    script_matches = SCRIPT_RE.findall(practice_html)
    if not script_matches:
        raise RuntimeError("Could not locate NeetCode's main application bundle")

    bundle_url = urljoin("https://neetcode.io/", script_matches[-1])
    catalog = extract_catalog(fetch_text(bundle_url), bundle_url)
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if the checked-in catalog differs from NeetCode's current catalog",
    )
    args = parser.parse_args()

    rendered = render_catalog()
    if args.check:
        current = CATALOG_PATH.read_text(encoding="utf-8") if CATALOG_PATH.exists() else ""
        if current != rendered:
            print("data/neetcode150.json is out of date", file=sys.stderr)
            return 1
        print("data/neetcode150.json is current")
        return 0

    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(rendered, encoding="utf-8")
    print(f"Wrote {CATALOG_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
