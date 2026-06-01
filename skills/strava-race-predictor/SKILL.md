---
description: Predict the athlete's finish time and pacing for an upcoming race by combining their Strava fitness with manually-entered data points and real-life factors (illness, poor sleep, stress, missed taper, heat, travel/altitude). Use when the user wants a race prediction or a "how will I do" estimate for a specific upcoming race.
---

# Race Predictor

Project a finish-time **range** (not false precision) for an upcoming race, blending hard training
data with the athlete's self-reported state and the race conditions. Always show your assumptions.

## Step 1 — Establish baseline fitness (from Strava)
- `sync_activities`, `list_activities(sport_type="Run", limit=30)`.
- Find the best **current fitness indicator**: a recent race, time-trial, or hard tempo. Convert it to
  meters+seconds and call `compute_vdot_paces` to get VDOT and equivalent race times. VDOT's
  race-equivalency is your anchor prediction for the goal distance.
- Sanity-check against recent long-run pace/HR, weekly volume, and consistency. If recent training is
  all easy/base (no hard efforts), say so — the anchor is softer and the range should widen.
- For endurance-limited races (marathon/ultra), weight long-run volume heavily; a great 10K VDOT
  doesn't guarantee a marathon if the long runs aren't there.

## Step 2 — Adjust for COURSE & CONDITIONS
Get the race's elevation and expected weather (web search, or reuse the analysis from
`strava-race-specific-plan`, or ask). Apply rule-of-thumb adjustments and state them:
- **Heat/humidity:** above ~13–15°C / 55–60°F, add roughly **1.5–3% to finish time per ~5°C** above
  that, more with high humidity. Cool/cold ≈ neutral to slightly fast.
- **Elevation:** net climbing costs more than net descending saves. Rough guide: **+~10 sec/mi for
  every ~50 ft (15 m) of net gain** over the course; steep late climbs hurt more.
- **Altitude (race elevation):** thinner air slows endurance pace measurably above ~1500 m.
- **Surface:** trail/technical adds time vs road.

## Step 3 — Incorporate MANUAL inputs & life factors
Ask the athlete for anything not in Strava, and fold each in **transparently** (name the factor and
how much it moved the estimate). Calibrate so you don't over- or under-react:
- **Illness:** a mild above-the-neck cold ≈ small downgrade. **Fever / systemic / chest / GI illness
  within ~7–10 days ≈ large downgrade**, and flag whether racing is even advisable.
- **Sleep:** **one poor night right before the race ≈ negligible physiologically** (don't overweight
  it — glycogen and training matter far more); **chronic** short sleep across the taper ≈ a real few-%
  hit. Say which case applies.
- **Taper quality:** under-tapered → lingering fatigue (slight downgrade); reasonable taper → neutral/positive.
- **Stress, travel, time-zone change, altitude arrival, fueling/hydration plan, recent niggles** →
  weight by severity; most single factors are small unless stacked.
- **Manually-entered workouts** not on Strava → factor into fitness as if they were logged.

## Step 4 — Deliver the prediction
- A **3-scenario range**: **bad-day**, **realistic** (most likely), and **good-day / everything-clicks**,
  each with a finish time and an average pace.
- A **confidence** note and the **single biggest uncertainty** (e.g. "heat is the swing factor").
- A short **assumptions list** — fitness anchor used, conditions, and each life-factor adjustment.
- A **recommended pacing strategy** consistent with the realistic scenario (target pace, even vs
  negative split, where to hold back). Be honest; never inflate the number to be encouraging.

## Units
Meters / seconds / m_per_s; convert for the user. Reference distances (m): 5k=5000, 10k=10000,
half=21097, marathon=42195. Default to the plan's `athlete.unit`, else ask.
