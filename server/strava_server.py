"""strava-coach MCP server.

Exposes Strava data + the training plan to Claude as tools. Stored activities are
read from local JSON; activity detail and per-second streams are fetched live from
Strava on demand (streams are never stored).
"""

from mcp.server.fastmcp import FastMCP

import store
import strava_client
import sync as sync_mod
import vdot

mcp = FastMCP("strava")


@mcp.tool()
def get_athlete_profile() -> dict:
    """Get the authenticated athlete's Strava profile (name, location, FTP, weight, etc.)."""
    data, _ = strava_client.api_get("/athlete")
    return data


@mcp.tool()
def sync_activities(full: bool = False) -> str:
    """Fetch newly-logged activities into local storage (capped at 100 / last 365 days).

    Set full=true for a one-time backfill of the whole window.
    """
    n = sync_mod.sync_activities(full=full)
    total = len(store.load_activities())
    return f"Synced {n} new activities. {total} activities now in local storage."


@mcp.tool()
def list_activities(sport_type: str = "", since: str = "", limit: int = 30) -> list:
    """List stored activities, most recent first.

    sport_type: optional filter, e.g. 'Run'. since: optional 'YYYY-MM-DD' lower bound.
    """
    acts = store.load_activities()
    if sport_type:
        acts = [a for a in acts
                if (a.get("sport_type") or a.get("type") or "").lower() == sport_type.lower()]
    if since:
        acts = [a for a in acts if (a.get("start_date_local") or "")[:10] >= since]
    return acts[: max(1, limit)]


@mcp.tool()
def get_activity(activity_id: int) -> dict:
    """Get full detail for a single activity (fetched live from Strava)."""
    data, _ = strava_client.api_get(f"/activities/{activity_id}")
    return data


@mcp.tool()
def get_activity_streams(
    activity_id: int,
    keys: str = "time,heartrate,watts,velocity_smooth,altitude,cadence,distance",
) -> dict:
    """Get per-second streams (HR/power/pace/etc.) for one activity, fetched on demand."""
    data, _ = strava_client.api_get(
        f"/activities/{activity_id}/streams", {"keys": keys, "key_by_type": "true"}
    )
    return data


@mcp.tool()
def get_training_plan() -> dict:
    """Return the current training plan, or {} if none exists yet."""
    return store.load_plan() or {}


@mcp.tool()
def save_training_plan(plan: dict) -> str:
    """Save/replace the training plan.

    Expected shape: {athlete:{goal_distance, race_date, unit, target_model},
    vdot, paces:{E,M,T,I,R: [fast_sec_per_km, slow_sec_per_km]},
    weeks:[{week, phase, start_date, target_mileage, sessions:[{date, type, pace_key,
    distance_km, description}]}]}.
    """
    store.save_plan(plan)
    weeks = len(plan.get("weeks", []))
    return f"Training plan saved ({weeks} weeks)."


@mcp.tool()
def compute_vdot_paces(distance_m: float, time_sec: float) -> dict:
    """Compute VDOT and E/M/T/I/R pace bands (seconds per km) from a recent race result.

    Use this when building a plan: pass a recent race distance (meters) and finish
    time (seconds) to get target paces.
    """
    v = vdot.vdot_from_race(distance_m, time_sec)
    return {"vdot": round(v, 1), "paces": vdot.all_paces(v)}


@mcp.tool()
def evaluate_progress() -> str:
    """Grade recent runs against the plan and return verdicts (Nailed it / On track / Off target)."""
    return sync_mod.grade_recent()


if __name__ == "__main__":
    mcp.run()
