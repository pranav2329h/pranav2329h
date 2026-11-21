"""Derive headline numbers (total, active days, streaks, best day) from the calendar."""
from datetime import date, timedelta


def compute_stats(payload):
    if not payload or not payload.get("days"):
        return None
    days = sorted(payload["days"], key=lambda d: d["date"])
    # Older data files only have levels; treat any non-zero level as activity.
    counts = {d["date"]: d.get("count", 1 if d["level"] else 0) for d in days}
    active = {k for k, v in counts.items() if v > 0}

    longest = run = 0
    for d in days:
        run = run + 1 if d["date"] in active else 0
        longest = max(longest, run)

    # Today may not have activity *yet*, so a streak ending yesterday still counts.
    cursor = date.fromisoformat(days[-1]["date"])
    if cursor.isoformat() not in active:
        cursor -= timedelta(days=1)
    current = 0
    while cursor.isoformat() in active:
        current += 1
        cursor -= timedelta(days=1)

    best_date = max(counts, key=lambda k: counts[k])
    return {
        "total": payload.get("total") or sum(counts.values()),
        "active_days": len(active),
        "current": current,
        "longest": longest,
        "best_count": counts[best_date],
        "best_date": best_date,
        "first": days[0]["date"],
        "last": days[-1]["date"],
    }
