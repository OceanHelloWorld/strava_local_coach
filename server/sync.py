"""Fetch newly-logged Strava activities and grade them against the training plan.

Used three ways:
  - the SessionStart hook:  `sync.py --grade --quiet`
  - the localhost UI:       imported, calls sync_activities()
  - the MCP server:         imported, calls sync_activities() / grade_recent()

Capping: every sync keeps at most 100 activities, none older than 365 days, and
stores only lightweight summary fields (no maps/photos/streams).
"""

import argparse
import sys
import time
from datetime import datetime, timezone

import store
import strava_client
import vdot

MAX_COUNT = 100
MAX_AGE_DAYS = 365


def _to_epoch(iso: str | None):
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _newest_epoch(activities: list):
    best = 0.0
    for a in activities:
        best = max(best, _to_epoch(a.get("start_date")) or 0.0)
    return best or None


def sync_activities(full: bool = False, max_count: int = MAX_COUNT,
                    max_age_days: int = MAX_AGE_DAYS) -> int:
    """Fetch activities into local storage. Returns the number of new ones fetched.

    Incremental by default (only activities newer than the latest stored one);
    pass full=True for a backfill of the last `max_count`/`max_age_days` window.
    """
    existing = store.load_activities()
    after = None if full else _newest_epoch(existing)
    cutoff = time.time() - max_age_days * 86400

    collected = []
    page = 1
    while len(collected) < max_count:
        params = {"per_page": 100, "page": page}
        if after:
            params["after"] = int(after)
        batch, _ = strava_client.api_get("/athlete/activities", params)
        if not batch:
            break
        stop = False
        for a in batch:
            epoch = _to_epoch(a.get("start_date"))
            if epoch and epoch < cutoff:   # older than the age window — done.
                stop = True
                break
            collected.append(strava_client.strip_activity(a))
            if len(collected) >= max_count:
                stop = True
                break
        if stop or len(batch) < 100:
            break
        page += 1

    merged = store.merge_activities(collected)
    # Enforce caps on the stored set so it never grows unbounded.
    capped = [a for a in merged if (_to_epoch(a.get("start_date")) or 0) >= cutoff][:max_count]
    if len(capped) != len(merged):
        store.save_activities(capped)
    return len(collected)


def grade_recent(quiet: bool = False) -> str:
    """Grade not-yet-graded running activities against the plan; return a summary."""
    plan = store.load_plan()
    if not plan:
        return ("" if quiet else
                "No training plan yet. Run /strava-coach:strava-training-plan-create to build one.")

    activities = store.load_activities()
    progress = store.load_progress()
    graded_ids = {g["activity_id"] for g in progress.get("graded", [])}
    paces = {k: list(v) for k, v in plan.get("paces", {}).items()}
    unit = (plan.get("athlete") or {}).get("unit", "km")

    sessions_by_date = {}
    for week in plan.get("weeks", []):
        for s in week.get("sessions", []):
            if s.get("date"):
                sessions_by_date[s["date"]] = s

    new_grades = []
    for a in activities:
        if a.get("id") in graded_ids:
            continue
        if "run" not in (a.get("sport_type") or a.get("type") or "").lower():
            continue
        date = (a.get("start_date_local") or "")[:10]
        session = sessions_by_date.get(date)
        if not session:
            continue
        new_grades.append(vdot.grade(a, session, paces, unit))

    if new_grades:
        progress.setdefault("graded", []).extend(new_grades)
    progress["last_synced"] = datetime.now(timezone.utc).isoformat()
    store.save_progress(progress)

    if not new_grades:
        return "" if quiet else "No new graded runs since last check."
    lines = [f"  - {g['date']}: {g['label']} — {g['reason']}" for g in new_grades]
    return "Strava coach — recent runs vs plan:\n" + "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync Strava activities and grade vs plan.")
    ap.add_argument("--grade", action="store_true", help="grade new runs against the plan")
    ap.add_argument("--full", action="store_true", help="backfill instead of incremental sync")
    ap.add_argument("--quiet", action="store_true", help="stay silent on errors / no-ops")
    args = ap.parse_args()

    out = []
    try:
        n = sync_activities(full=args.full)
        if n:
            out.append(f"[strava-coach] Synced {n} new activit{'y' if n == 1 else 'ies'}.")
        if args.grade:
            summary = grade_recent(quiet=args.quiet)
            if summary:
                out.append(summary)
    except strava_client.StravaError as e:
        if not args.quiet:
            out.append(f"[strava-coach] {e}")
    except Exception as e:  # hook must never block a session — fail soft.
        if not args.quiet:
            out.append(f"[strava-coach] unexpected error: {e}")

    text = "\n".join(out)
    if text:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
