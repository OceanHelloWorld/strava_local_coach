---
description: Build a training plan tailored to a SPECIFIC target race — its real elevation profile and total gain/loss, terrain/surface, and the typical weather and temperature for that location and date — instead of a generic distance plan. Use when the user names a specific race (with a location/date or a course) and wants a course-specific, climate-aware plan.
---

# Race-Specific Training Plan

Generic "marathon plan for a time goal" ignores that a hilly, hot September race demands very
different preparation from a flat, cool, net-downhill one. This skill builds the plan **around the
actual race**: its course and its likely conditions.

> This is the course-aware sibling of `strava-training-plan-create`. Reuse that skill's
> **periodization principles, VDOT pace derivation, plan JSON schema, and `save_training_plan` step
> verbatim** — this skill only adds the race-specific layers below.

## Step 1 — Nail down the race
Get (ask for whatever's missing): **race name, date, location, distance**, and the **course** (a link,
a GPX/route, or "same as last year"). Also the athlete's **goal time** and a **recent hard result**
(to set paces). Pull their Strava context first (`sync_activities`, `list_activities`,
`get_athlete_profile`) to ground current fitness and weekly volume.

## Step 2 — Analyze the COURSE
Use web search/fetch if available; otherwise ask the user for the numbers.
- **Total elevation gain & loss**, and the **net** (net-downhill vs net-uphill vs rolling).
- **Profile shape** — where the climbs are (e.g. big hill at mile 20), late-race climbs, long
  descents, flat-and-fast, or constant rolling.
- **Surface/terrain** — road, trail, mixed; technical footing.
- Translate into **demands**:
  - **Hilly / big climbs** → weekly hill work; long runs with matching gain; climb at goal effort.
  - **Net-downhill** (e.g. Boston, many point-to-points) → **downhill running reps** to condition
    quads against eccentric load; without them the quads blow up late even when aerobically fine.
  - **Rolling** → strength-endurance, undulating tempo routes.
  - **Trail/technical** → terrain-specific long runs, ankle/stability work.
  - **Altitude** (if the race is high) → note acclimation/pace adjustment.

## Step 3 — Analyze the CLIMATE
Look up typical weather for that **location around that date** (historical averages, not a forecast
this far out): average high/low **temperature**, **humidity**, sun exposure, wind.
- **Hot/humid** (e.g. >~20°C / 68°F race-time) → build a **heat-acclimation block in the final 2–3
  weeks** (train in the heat of day, or overdress/sauna), plan hydration + electrolytes, and **adjust
  goal pace down** for the expected conditions. Set expectations honestly.
- **Cold** → minimal acclimation need; note warm-up/clothing logistics.
- **Mild/cool** → ideal; flag it as a non-issue.

## Step 4 — Build the plan
Follow `strava-training-plan-create` periodization (base → build → peak → taper, 80/20, ≤10%/wk ramp,
cutback weeks, long-run caps), then **weave in the race-specific work**: schedule the hill/downhill
sessions, terrain-matched long runs, race-pace segments on representative profile, and the heat block
in the taper. Put a **course-specific pacing strategy** in the race-week notes (e.g. "bank nothing on
the early downhill; save quads; attack the flat from mile 18").

## Step 5 — Save & summarize
Save via `save_training_plan` using the standard schema (so the auto-grader still works). You may add
a `race` block to `athlete` (e.g. `{"course":"net downhill, 600m loss","climate":"early-March, 7–15°C, low heat risk"}`).
Then summarize for the athlete: the **course demands**, the **climate plan**, and **how each block of
the plan specifically addresses them** — not just weeks and paces.
