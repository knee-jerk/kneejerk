#!/usr/bin/env python3
"""
KneeJerk — Daily points decay calculator
Runs via GitHub Actions each day at 01:00 UTC (02:00 BST)
Updates PTS_ variables, LAST_UPDATED and NEXT_UPDATED in index.html

Tournament start: 11 June 2026 (day 1, first decay applied)
Day 0: 10 June 2026 (max points, no decay)
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

# Full update schedule
UPDATE_SCHEDULE = [
    date(2026, 6, 10),  # Wed - launch day
    date(2026, 6, 14),  # Sun
    date(2026, 6, 21),  # Sun
    date(2026, 6, 28),  # Sun
    date(2026, 7, 5),   # Sun
    date(2026, 7, 12),  # Sun
    date(2026, 7, 19),  # Sun - final weekend
]

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DAY_NAMES   = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

def format_update_date(d):
    day_name = DAY_NAMES[d.weekday()]
    month = MONTH_NAMES[d.month - 1]
    return f"{day_name} {d.day} {month}, 09:00 BST"

def get_update_dates(today):
    last = None
    next_ = None
    for d in UPDATE_SCHEDULE:
        if d <= today:
            last = d
        else:
            if next_ is None:
                next_ = d
    return last, next_

def calculate_points(cat, today):
    cfg = CATEGORIES[cat]
    if today < TOURNAMENT_START:
        return cfg["max"]
    if today >= cfg["lock"]:
        return cfg["min"]
    days_elapsed = (today - TOURNAMENT_START).days + 1
    pts = cfg["max"] - (days_elapsed * cfg["decay"])
    return max(cfg["min"], pts)

def update_html(filepath, today):
    with open(filepath, "r") as f:
        content = f.read()

    changed = False

    # Update points values
    for cat in CATEGORIES:
        new_val = calculate_points(cat, today)
        pattern = rf'(var {cat}\s*=\s*)(\d+)(;)'
        new_content = re.sub(pattern, rf'\g<1>{new_val}\g<3>', content)
        if new_content != content:
            changed = True
            content = new_content
            print(f"  {cat} = {new_val}")

    # Update last/next update dates
    last, next_ = get_update_dates(today)
    last_str = format_update_date(last) if last else "Not yet updated"
    next_str = format_update_date(next_) if next_ else "Season complete"

    for var, val in [("LAST_SUNDAY", last_str), ("NEXT_SUNDAY", next_str)]:
        pattern = rf'(var {var}\s*=\s*")[^"]*(")'
        new_content = re.sub(pattern, rf'\g<1>{val}\g<2>', content)
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
