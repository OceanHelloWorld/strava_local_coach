"""Strava API v3 client using only the Python standard library (urllib).

Handles OAuth token refresh (with refresh-token rotation) and a couple of small
HTTP helpers. The single third-party dependency in this project is `mcp`; this
module deliberately avoids requests/httpx to keep the install barrier minimal.
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

import store

API_BASE = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"

# Lightweight summary fields kept when storing an activity. Heavy fields
# (map/polyline, photos, segment_efforts, splits, laps) are intentionally dropped.
KEEP_FIELDS = [
    "id", "name", "sport_type", "type", "start_date", "start_date_local",
    "distance", "moving_time", "elapsed_time", "total_elevation_gain",
    "average_speed", "max_speed", "average_heartrate", "max_heartrate",
    "average_cadence", "average_watts", "max_watts", "weighted_average_watts",
    "device_watts", "kilojoules", "suffer_score", "calories", "average_temp",
    "workout_type", "trainer", "commute",
]


class StravaError(Exception):
    """User-facing error (auth, network, rate limit, or API failure)."""


def _client_creds():
    cid = os.environ.get("STRAVA_CLIENT_ID")
    secret = os.environ.get("STRAVA_CLIENT_SECRET")
    if not cid or not secret:
        raise StravaError(
            "Missing Strava credentials. Set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET."
        )
    return cid, secret


def _http(method: str, url: str, data: dict | None = None, headers: dict | None = None):
    headers = dict(headers or {})
    body = None
    if data is not None:
        body = urllib.parse.urlencode(data).encode()
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = resp.read().decode()
            return json.loads(payload) if payload else {}, dict(resp.headers)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        if e.code == 429:
            raise StravaError(
                "Strava rate limit reached (429). The 15-minute window resets on the "
                "quarter hour (:00/:15/:30/:45) — try again then."
            )
        if e.code == 401:
            raise StravaError("Strava auth failed (401). Re-run scripts/strava_login.py.")
        raise StravaError(f"Strava API error {e.code}: {detail[:300]}")
    except urllib.error.URLError as e:
        raise StravaError(f"Network error reaching Strava: {e.reason}")


def exchange_code(code: str) -> dict:
    """Exchange a one-time authorization code for tokens (used by the login script)."""
    cid, secret = _client_creds()
    data, _ = _http("POST", TOKEN_URL, data={
        "client_id": cid,
        "client_secret": secret,
        "code": code,
        "grant_type": "authorization_code",
    })
    return data


def refresh_if_needed() -> str:
    """Return a valid access token, refreshing (and rotating the refresh token) if expired."""
    tokens = store.load_tokens()
    if not tokens.get("refresh_token"):
        raise StravaError("Not connected to Strava yet. Run scripts/strava_login.py first.")

    # 60s safety buffer before the 6-hour access token expires.
    if tokens.get("access_token") and time.time() < tokens.get("expires_at", 0) - 60:
        return tokens["access_token"]

    cid, secret = _client_creds()
    data, _ = _http("POST", TOKEN_URL, data={
        "client_id": cid,
        "client_secret": secret,
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
    })
    tokens["access_token"] = data["access_token"]
    tokens["refresh_token"] = data["refresh_token"]  # Strava rotates this — must overwrite.
    tokens["expires_at"] = data["expires_at"]
    store.save_tokens(tokens)
    return tokens["access_token"]


def api_get(path: str, params: dict | None = None):
    """GET a Strava API path. Returns (json, response_headers)."""
    token = refresh_if_needed()
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return _http("GET", url, headers={"Authorization": f"Bearer {token}"})


def strip_activity(activity: dict) -> dict:
    """Keep only lightweight summary fields (drops maps, photos, heavy nested data)."""
    return {k: activity.get(k) for k in KEEP_FIELDS if k in activity}
