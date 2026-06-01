"""Tiny JSON-file storage for strava-coach.

All state lives as plain JSON files under a single data directory so there is
nothing to install (no database) and everything is human-readable. The data dir
is shared by the MCP server and the sync job.
"""

import json
import os
from pathlib import Path


def data_dir() -> Path:
    """Return the data directory, honoring $STRAVA_DATA_DIR (default ~/.config/strava-coach)."""
    override = os.environ.get("STRAVA_DATA_DIR")
    p = Path(override).expanduser() if override else Path.home() / ".config" / "strava-coach"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _path(name: str) -> Path:
    return data_dir() / name


def _load(name: str, default):
    p = _path(name)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _save(name: str, obj, mode: int = 0o600) -> None:
    """Atomically write JSON with restrictive permissions (tokens hold secrets)."""
    p = _path(name)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=False))
    os.chmod(tmp, mode)
    tmp.replace(p)


# --- tokens ---------------------------------------------------------------
def load_tokens() -> dict:
    return _load("tokens.json", {})


def save_tokens(tokens: dict) -> None:
    _save("tokens.json", tokens, 0o600)


# --- training plan --------------------------------------------------------
def load_plan():
    return _load("plan.json", None)


def save_plan(plan) -> None:
    _save("plan.json", plan, 0o600)


# --- activities -----------------------------------------------------------
def load_activities() -> list:
    return _load("activities.json", [])


def save_activities(acts: list) -> None:
    _save("activities.json", acts, 0o600)


def merge_activities(new: list) -> list:
    """Merge new activities into the store, deduping by id, newest first."""
    by_id = {a["id"]: a for a in load_activities() if "id" in a}
    for a in new:
        if "id" in a:
            by_id[a["id"]] = a
    merged = sorted(by_id.values(), key=lambda x: x.get("start_date", ""), reverse=True)
    save_activities(merged)
    return merged


# --- progress / grades ----------------------------------------------------
def load_progress() -> dict:
    return _load("progress.json", {"graded": [], "last_synced": None})


def save_progress(progress: dict) -> None:
    _save("progress.json", progress, 0o600)
