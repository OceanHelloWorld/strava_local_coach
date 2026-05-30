---
description: Answer questions about the athlete's Strava activities and training progress — trends, PRs, single-workout deep dives, and how recent runs compare to their training plan. Use whenever the user asks about their runs, rides, workouts, mileage, paces, heart rate, or training progress.
---

# Strava Analysis

Use the `strava` MCP tools to answer questions about the athlete's training from their
locally-stored Strava data.

## Where the data is
- **`list_activities`** — stored activity summaries (most recent first; supports
  `sport_type`, `since`, `limit`). This is your default source for trends and lookups.
- **`get_activity(id)`** — full detail for one activity (live from Strava).
- **`get_activity_streams(id)`** — per-second HR / pace / power / elevation, fetched on
  demand. Use only when a question needs within-run detail (e.g. splits, HR drift, where
  they faded). Don't pull streams for simple list/trend questions.
- **`get_training_plan`** and **`evaluate_progress`** — the plan and graded runs, for
  "how am I tracking?" questions.

## Workflow
1. If the question is about very recent runs, call `sync_activities` first so the data is fresh.
2. Pull the minimum you need (prefer `list_activities` over per-activity calls).
3. Compute and present clearly.

## Units & conventions
- Distances are **meters**, times **seconds**, speeds **m/s**. Convert for the user:
  km = m/1000, mi = m/1609.34; pace min/km = (moving_time/60) / (distance/1000).
  Default to the unit on the plan (`athlete.unit`), else km.
- Heart rate is bpm; `average_watts`/`weighted_average_watts` are watts (only present when a
  power source exists — `device_watts: true` means a real power meter). `suffer_score` is
  Strava's relative effort (HR-based; may be absent).

## Good answers
- For trends, summarize across weeks (volume, average pace/HR, number of sessions) and call
  out what changed — don't just dump rows.
- For "how am I doing vs plan", lean on `evaluate_progress` (Nailed it / On track / Off target /
  Missed per run) plus weekly mileage adherence and easy-pace discipline (flag easy runs done
  too hard — the most common mistake).
- For a single workout, optionally use streams to comment on pacing/HR drift/fade.
