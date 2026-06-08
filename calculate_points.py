#!/usr/bin/env python3
"""
KneeJerk — Daily points decay calculator
Runs via GitHub Actions each day at 01:00 UTC (02:00 BST)
Updates the six PTS_ variables, LAST_SUNDAY and NEXT_SUNDAY in index.html

Tournament start: 11 June 2026 (day 1, first decay applied)
Day 0: 10 June 2026 (max points, no decay)
Picks made on or before 10 June score maximum points.
"""

from datetime import date, timedelta
import re

TOURNAMENT_START = date(2026, 6, 11)

CATEGORIES = {
    "PTS_MGSP": {"max": 17, "decay": 1, "min": 1, "lock": date(2026, 6, 26)},
    "PTS_LGSP": {"max": 17, "decay": 1, "min": 1, "lock": date(2026, 6, 26)},
    "PTS_TST":  {"max": 39, "decay": 1, "min": 1, "lock": date(2026, 7, 18)},
    "PTS_AST":  {"max": 39, "decay": 1, "min": 1, "lock": date(2026, 7, 18)},
    "PTS_GBT":  {"max": 39, "decay": 1, "min": 1, "lock": date(2026, 7, 18)},
    "PTS_WCW":  {"max": 78, "decay": 2, "min": 2, "lock": date(2026, 7, 18)},
}

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def calculate_points(cat, today):
    cfg = CATEGORIES[cat]
    if today < TOURNAMENT_START:
        return cfg["max"]
    if today >= cfg["lock"]:
        return cfg["min"]
    # Day 1 = first decay already applied
    days_elapsed = (today - TOURNAMENT_START).days + 1
    pts = cfg["max"] - (days_elapsed * cfg["decay"])
    return max(cfg["min"], pts)

def format_date(d):
    month = MONTH_NAMES[d.month - 1]
    return f"Sun {d.day} {month}, 09:00 BST"

def get_sundays(today):
    days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
    last_sunday = today - timedelta(days=days_since_sunday)
    next_sunday = last_sunday + timedelta(days=7)
    return last_sunday, next_sunday

def update_html(filepath, today):
    with open(filepath, "r") as f:
        content = f.read()

    changed = False

    for cat in CATEGORIES:
        new_val = calculate_points(cat, today)
        pattern = rf'(var {cat}\s*=\s*)(\d+)(;)'
        replacement = rf'\g<1>{new_val}\g<3>'
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            changed = True
            content = new_content
            print(f"  {cat} = {new_val}")

    last_sunday, next_sunday = get_sundays(today)
    for var, val in [("LAST_SUNDAY", format_date(last_sunday)), ("NEXT_SUNDAY", format_date(next_sunday))]:
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
