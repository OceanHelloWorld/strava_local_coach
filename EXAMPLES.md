# Examples

Real things you can say to Claude once **strava-coach** is connected, grouped by what you want to do.
Just copy a prompt and paste it into Claude — plain English works, you don't need exact wording.

> New here? Start with the [Quick start in the README](README.md#-quick-start-5-steps-10-minutes).

---

## 1. First look — sync and see your runs

**You:**
> Sync my Strava and show my last 10 runs.

**What you get:** a clean table of recent runs — date, distance, time, pace, average heart rate, and
elevation — plus a couple of things Claude noticed (e.g. "your long runs are very aerobic — HR only ~75%
of max").

---

## 2. Weekly / monthly check-ins

> Summarize the last 4 weeks: total mileage, average pace, and how hard I've been training.

> How does this week's volume compare to last week's?

> How many days did I run in May, and what was my longest run?

**What you get:** week-by-week totals and trends, written as a short summary rather than a wall of rows.

---

## 3. Honest feedback on your training

> Look at my last month of running and give me honest, actionable feedback — what should I fix?

> Am I running my easy days too hard?

> Does my training look like I'm overreaching?

**What you get:** a coach's verdict and a **prioritized top-3 list of changes** — backed by your numbers
(e.g. "your easy runs average 6:40/km at 155 bpm — that's tempo effort; slow to ~7:10 to actually
recover"), not generic tips.

---

## 4. Race-pace planning (uses your heart rate)

> I'm running a flat half marathon this weekend. Based on my recent runs and heart rate, what pace
> should I target — give me a conservative option and a push option.

> Build me a per-mile split table for a 1:58 half marathon with a negative split.

**What you get:** evidence-based pace targets grounded in your real data, plus a mile- or km-by-segment
pace table with heart-rate cues.

> 💡 Tip: mention the **course** (flat/hilly), the **distance**, and which **shoes** you'll wear — Claude
> can match those against similar runs in your history for a sharper estimate.

---

## 5. Single-run deep dives

> Show the splits and heart-rate drift on my long run last Sunday. Where did I start to fade?

> Was my tempo run actually at threshold, or was I going too easy?

> Compare my two 20K runs this month — same pace, but was one at a lower heart rate?

**What you get:** within-run detail from per-second data — split-by-split pace and HR, where effort
spiked or pace dropped, and what it means.

---

## 6. Post-race analysis

> Analyze my marathon and tell me what to do differently next time.

> Why did I blow up in the second half of my 10K?

> Break my half marathon into 5K splits and tell me if I paced it right.

**What you get:** a race post-mortem — split table, pacing shape (even/positive/negative), the
**root cause** of any fade read from the HR-vs-pace pattern (e.g. bonk vs heat drift vs went-out-too-fast),
and 3 concrete fixes (pacing, fueling, workouts) for the next one.

---

## 7. Training-plan creation

Run the guided interview:

```
/strava-coach:strava-training-plan-create
```

**What happens:** Claude asks a few coach-style questions (goal race & date, target time, a recent hard
effort to set paces, days per week, longest recent run), checks your answers against your real Strava
history, then writes a full periodized plan — base → build → peak → taper — with target paces for every
session, saved locally so future sessions can grade your runs against it.

Or just say:

> Make me a 12-week plan for a sub-2:00 half marathon. I can train 4 days a week and my long run is Sunday.

---

## 8. Race-*specific* plans (course + weather aware)

> Plan my training for the Napa Valley Marathon next March — factor in the actual course and the weather.

> I'm doing a hilly trail 50K in August. Build a plan for that specific course and the summer heat.

> Make a Boston-specific plan — it's net downhill with the hills late.

**What you get:** a plan built around the *real* race, not a generic template — it looks up the course's
elevation profile and the typical temperature/humidity for that place and date, then bakes in the right
work: hill or **downhill-quad** sessions, terrain-matched long runs, a **heat-acclimation block** in the
taper if it'll be hot, and a course-specific pacing strategy. Saved like any other plan.

---

## 9. Predict your race (with real-life factors)

> How will I do at my 10K Sunday? I was sick Tuesday and haven't slept well this week.

> Predict my marathon time. It's going to be 75°F and humid, and the course climbs 1,200 ft.

> I ran a 5K time trial in 22:30 last week (not on Strava). What's a realistic half-marathon target?

**What you get:** a **3-scenario finish-time range** (bad-day / realistic / good-day) with an average
pace for each, a confidence note and the biggest swing factor, a transparent list of how each
input was weighted (it won't overreact to one bad night's sleep, but *will* downgrade for a real
illness), and a pacing strategy for the realistic case.

---

## 10. Tracking your plan

After you have a plan, each new Claude session prints a quiet one-liner about new runs. You can also ask:

> How am I tracking against my plan this week?

> I missed Tuesday's interval session — should I move it or skip it?

**What you get:** per-run grades (*Nailed it / On track / Off target / Missed*), weekly mileage adherence,
and honest feedback — especially flagging easy days run too hard.

---

## Tips for good answers

- **Be specific about the goal.** "What pace for a flat half on Sunday?" beats "how fast am I?"
- **Name the race** for race-specific plans and predictions (location + date) so Claude can look up the
  course and weather.
- **Tell Claude your real-life context** for predictions — illness, sleep, stress, travel, heat.
- **Tell Claude what to ignore.** e.g. "skip the second half, I bonked" or "ignore the treadmill runs."
- **Ask for the unit you want** ("in miles" / "in km") and **ask follow-ups** ("now show per-mile splits").
