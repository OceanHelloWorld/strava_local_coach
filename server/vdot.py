"""VDOT pace model (Jack Daniels) + run grading.

A recent race result -> VDOT -> training pace bands (Easy / Marathon / Threshold /
Interval / Repetition). The same paces are used to build the plan and to grade
logged runs against planned sessions.

The VO2-from-velocity and %max-from-time relationships are Daniels' published
formulas; pace bands are derived by inverting the velocity equation at intensity
percentages of VDOT. This is a faithful approximation of Daniels' tables, good
enough for planning and grading (not a substitute for a coach).
"""

import math

# Intensity as a fraction of VDOT (VO2max), expressed as (slow%, fast%).
# Ordering guarantees E (slowest) < M < T < I < R (fastest).
INTENSITIES = {
    "E": (0.62, 0.74),   # Easy / recovery / long-run aerobic
    "M": (0.79, 0.84),   # Marathon pace
    "T": (0.85, 0.89),   # Threshold / tempo ("comfortably hard")
    "I": (0.95, 1.00),   # Interval / VO2max
    "R": (1.02, 1.06),   # Repetition (speed/economy)
}

PACE_LABELS = {
    "E": "Easy", "M": "Marathon", "T": "Threshold", "I": "Interval", "R": "Repetition",
}

# Map a workout 'type' (used in the plan) to its pace key.
TYPE_TO_KEY = {
    "easy": "E", "recovery": "E", "long": "E",
    "marathon": "M", "race-pace": "M",
    "tempo": "T", "threshold": "T",
    "interval": "I", "intervals": "I", "vo2": "I",
    "repetition": "R", "rep": "R", "strides": "R",
}


def _vo2_from_velocity(v_m_per_min: float) -> float:
    return -4.60 + 0.182258 * v_m_per_min + 0.000104 * v_m_per_min ** 2


def _velocity_from_vo2(vo2: float) -> float:
    """Invert the quadratic to get velocity (m/min) for a target VO2."""
    a, b, c = 0.000104, 0.182258, -4.60 - vo2
    disc = b * b - 4 * a * c
    return (-b + math.sqrt(disc)) / (2 * a)


def _pct_max_from_time(t_min: float) -> float:
    return (0.8
            + 0.1894393 * math.exp(-0.012778 * t_min)
            + 0.2989558 * math.exp(-0.1932605 * t_min))


def vdot_from_race(distance_m: float, time_sec: float) -> float:
    """Estimate VDOT from a single race/time-trial performance."""
    t_min = time_sec / 60.0
    velocity = distance_m / t_min
    vo2 = _vo2_from_velocity(velocity)
    pct = _pct_max_from_time(t_min)
    return vo2 / pct


def pace_band(vdot: float, key: str) -> tuple[int, int]:
    """Return (fast_sec_per_km, slow_sec_per_km) for an intensity key."""
    slow_pct, fast_pct = INTENSITIES[key]
    v_fast = _velocity_from_vo2(vdot * fast_pct)   # m/min
    v_slow = _velocity_from_vo2(vdot * slow_pct)
    fast = round(1000.0 / v_fast * 60.0)           # sec per km
    slow = round(1000.0 / v_slow * 60.0)
    return fast, slow


def all_paces(vdot: float) -> dict:
    """Return every pace band as {key: [fast_sec_per_km, slow_sec_per_km]}."""
    return {k: list(pace_band(vdot, k)) for k in INTENSITIES}


def format_pace(sec_per_km: float, unit: str = "km") -> str:
    sec = sec_per_km * 1.60934 if unit == "mi" else sec_per_km
    m, s = divmod(int(round(sec)), 60)
    return f"{m}:{s:02d}/{unit}"


def grade(activity: dict, session: dict, paces: dict, unit: str = "km") -> dict:
    """Grade one logged activity against a planned session.

    `session` keys used: type, pace_key (optional), distance_km (optional).
    `paces` is {key: [fast, slow]} in seconds per km.
    Returns a verdict dict with a label and a human-readable reason.
    """
    dist_m = activity.get("distance") or 0
    moving = activity.get("moving_time") or 0
    actual_km = dist_m / 1000.0
    planned_km = session.get("distance_km") or 0
    stype = (session.get("type") or "").lower()
    key = session.get("pace_key") or TYPE_TO_KEY.get(stype)

    label = "On track"
    reasons = []

    # Distance adherence (+/-10% on target, >15% over is a long day).
    if planned_km:
        ratio = actual_km / planned_km if planned_km else 0
        if ratio < 0.9:
            label = "Off target"
            reasons.append(f"{actual_km:.1f}{unit} vs {planned_km:.1f}{unit} planned (short)")
        elif ratio > 1.15:
            reasons.append(f"{actual_km:.1f}{unit} vs {planned_km:.1f}{unit} planned (long)")
        else:
            reasons.append(f"distance on point ({actual_km:.1f}{unit})")

    # Pace vs target band.
    if key and key in paces and actual_km > 0 and moving > 0:
        actual_sec_per_km = moving / actual_km
        fast, slow = paces[key]
        if actual_sec_per_km < fast - 10:
            reasons.append(f"pace {format_pace(actual_sec_per_km, unit)} faster than {key}-zone")
            if stype in ("easy", "recovery", "long"):
                label = "Off target"
                reasons.append("(easy day run too hard — 80/20 discipline)")
        elif actual_sec_per_km > slow + 15:
            reasons.append(f"pace {format_pace(actual_sec_per_km, unit)} slower than {key}-zone")
            if label == "On track":
                label = "Off target"
        else:
            reasons.append(f"pace in {key}-zone ({format_pace(actual_sec_per_km, unit)})")

    # Upgrade to a top grade when distance is on point and nothing flagged off.
    if label == "On track" and planned_km and 0.9 <= (actual_km / planned_km) <= 1.15:
        label = "Nailed it"

    return {
        "activity_id": activity.get("id"),
        "date": (activity.get("start_date_local") or "")[:10],
        "label": label,
        "reason": "; ".join(reasons) or "logged",
        "session_type": session.get("type"),
        "planned_km": planned_km,
        "actual_km": round(actual_km, 2),
    }
