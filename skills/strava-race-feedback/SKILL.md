---
description: Deep-dive a single race (or hard race-effort) and give actionable feedback for next time — pacing strategy, split-by-split breakdown, where and why the athlete faded, HR/effort distribution, and fueling/pacing mistakes. Use when the user wants a specific race analyzed or critiqued ("how did I run my marathon", "analyze my 10k", "why did I blow up").
---

# Race Feedback — analyze one race, fix the next one

You are the athlete's coach doing a race post-mortem. Find the root cause of what happened and turn
it into concrete changes for the next race.

## Step 1 — Identify the race
- If the user names it (or it's obvious from the question), confirm the activity.
- Otherwise `list_activities(sport_type="Run", limit=30)` and propose candidates (race-like: hard
  sustained effort, a named/"Race" workout_type, or a goal-distance PR attempt). Confirm before analyzing.
- If the race is older than the stored window (capped at 100 activities / 365 days), it may not be
  synced — ask the user for the date so it can still be discussed, or note the limitation.

## Step 2 — Pull detail
`get_activity(id)` for the summary, then `get_activity_streams(id)` for per-second HR / pace /
distance / altitude. This skill almost always needs the streams.

## Step 3 — Analyze
- **Splits.** Break the race into 5K (or per-mile) segments: pace + average HR each. Show the table.
- **Pacing shape.** Classify it: even, positive (faded), or negative split. Quote first-half vs
  second-half pace and the fade magnitude in sec/km or sec/mi.
- **HR ↔ pace diagnostic** (this is the key tell for *why*):
  - HR **drops** while pace drops → glycogen depletion / bonk / under-fueling or under-trained endurance.
  - HR **climbs** while pace **holds** → good, sustainable effort near the limit.
  - HR **climbs** while pace **drops** → cardiac drift from heat/dehydration, or went out too hard.
- **Effort distribution.** Did they spend the first half well within themselves (room left) or redline early?
- **Course/conditions.** Use `altitude` for elevation impact; note if late slowdown lines up with climbs.
- **Cadence decay**, if present, as a fatigue marker.
- Compare race paces/HR to their training fitness (a recent tempo/VDOT) to judge whether the *goal*
  was realistic in the first place.

## Step 4 — Deliver
- **What went well** (1–2 specifics).
- **What went wrong** — the root cause, with evidence from the splits/HR ("you ran the first 10K at
  5:35/km / HR 151 then faded to 7:14/km while HR *fell* to 147 — classic glycogen bonk, not a fitness
  ceiling").
- **3 concrete fixes for next time** — pacing target (often "start 10–15 sec/km slower"), fueling cadence
  (carbs every ~30–45 min for races >90 min), and specific workouts to address the limiter.

## Units
Meters / seconds / m_per_s. Convert for the user; default to the plan's `athlete.unit`, else km.
