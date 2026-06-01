#!/usr/bin/env python3
"""
KneeJerk — Daily points decay calculator
Runs via GitHub Actions each day at 07:55 UTC (09:00 BST display time)
Updates PTS_ variables, LAST_SUNDAY and NEXT_SUNDAY in index.html

NOTE: Tournament start date is currently set to 04/06/2026 for dry run purposes.
When the real tournament begins, change TOURNAMENT_START to date(2026, 6, 11)
and update the lock dates accordingly.

DECAY RULE: Day 1 of the tournament already has one step of decay applied.
"""

from datetime import date, timedelta
import re

# ── Tournament configuration ───────────────────────────────────────────────────
# DRY RUN: fake start date. Change to date(2026, 6, 11) for real tournament.
TOURNAMENT_START = date(2026, 6, 4)

CATEGORIES = {
    # DRY RUN lock dates. For real tournament: MGSP/LGSP = date(2026, 6, 26), others = date(2026, 7, 18)
    "PTS_MGSP": {"max": 17, "decay": 1, "min": 1, "lock": date(2026, 6, 19)},
    "PTS_LGSP": {"max": 17, "decay": 1, "min": 1, "lock": date(2026, 6, 19)},
    "PTS_TST":  {"max": 39, "decay": 1, "min": 1, "lock": date(2026, 7, 11)},
    "PTS_AST":  {"max": 39, "decay": 1, "min": 1, "lock": date(2026, 7, 11)},
    "PTS_GBT":  {"max": 39, "decay": 1, "min": 1, "lock": date(2026, 7, 11)},
    "PTS_WCW":  {"max": 78, "decay": 2, "min": 2, "lock": date(2026, 7, 11)},
}

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def calculate_points(cat, today):
    cfg = CATEGORIES[cat]
    if today < TOURNAMENT_START:
        return cfg["max"]
    if today >= cfg["lock"]:
        return cfg["min"]
    days_elapsed = (today - TOURNAMENT_START).days + 1
    pts = cfg["max"] - (days_elapsed * cfg["decay"])
    return max(cfg["min"], pts)

def format_date(d):
    month = MONTH_NAMES[d.month - 1]
    return f"Sun {d.day} {month}, 09:00 BST"

def get_sundays(today):
    # Last Sunday on or before today
    days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
    last_sunday = today - timedelta(days=days_since_sunday)
    # Next Sunday after that
    next_sunday = last_sunday + timedelta(days=7)
    return last_sunday, next_sunday

def update_html(filepath, today):
    with open(filepath, "r") as f:
        content = f.read()

    changed = False

    # Update points values
    for cat in CATEGORIES:
        new_val = calculate_points(cat, today)
        pattern = rf'(var {cat}\s*=\s*)(\d+)(;)'
        replacement = rf'\g<1>{new_val}\g<3>'
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changed = True
            content = new_content
            print(f"  {cat} = {new_val}")

    # Update sunday dates
    last_sunday, next_sunday = get_sundays(today)
    last_str = format_date(last_sunday)
    next_str = format_date(next_sunday)

    for var, val in [("LAST_SUNDAY", last_str), ("NEXT_SUNDAY", next_str)]:
        pattern = rf'(var {var}\s*=\s*")[^"]*(")'
        replacement = rf'\g<1>{val}\g<2>'
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changed = True
            content = new_content
            print(f"  {var} = {val}")

    if changed:
        with open(filepath, "w") as f:
            f.write(content)
        print("index.html updated.")
    else:
        print("No changes needed - values already correct.")

    return changed

if __name__ == "__main__":
    today = date.today()
    print(f"Running for date: {today}")
    update_html("index.html", today)
