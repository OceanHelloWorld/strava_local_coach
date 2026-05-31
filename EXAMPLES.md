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

**What you get:** week-by-week totals and trends, written as a short summary rather than a wall of rows —
with callouts like rising mileage or unusually easy/hard weeks.

---

## 3. Race-pace planning (uses your heart rate)

> I'm running a flat half marathon this weekend. Based on my recent runs and heart rate, what pace
> should I target — and give me a conservative option and a push option.

> Look at the first half of my last marathon (ignore the second half, I bonked) and tell me what that
> says about my current half-marathon pace.

> Build me a per-mile split table for a 1:58 half marathon with a negative split.

**What you get:** evidence-based pace targets grounded in your actual data — e.g. *"the first half of your
Napa marathon held 8:59/mi at only 151 bpm, so 9:00/mi for a half is well within reach"* — plus a
mile-by-mile or kilometer-by-kilometer pace table with heart-rate cues.

> 💡 Tip: mention the **course** (flat/hilly), the **distance**, and which **shoes** you'll wear — Claude
> can match those conditions against similar runs in your history for a sharper estimate.

---

## 4. Single-run deep dives

> Show the splits and heart-rate drift on my long run last Sunday. Where did I start to fade?

> Was my tempo run actually at threshold, or was I going too easy?

> Compare my two 20K runs this month — same pace, but was one at a lower heart rate?

**What you get:** within-run detail pulled from per-second data — split-by-split pace and HR, where effort
spiked or pace dropped, and what it means.

---

## 5. Training-plan creation

Run the guided interview:

```
/strava-coach:strava-training-plan-create
```

**What happens:** Claude asks you a few coach-style questions (goal race & date, target time, a recent
hard effort to set your paces, days per week, longest recent run), checks your answers against your real
Strava history, then writes a full periodized plan — base → build → peak → taper — with target paces for
every session. It's saved locally so future sessions can grade your runs against it.

You can also just say:

> Make me a 12-week plan for a sub-2:00 half marathon. I can train 4 days a week and my long run day is Sunday.

---

## 6. Tracking your plan

After you have a plan, each new Claude session prints a quiet one-liner about new runs. You can also ask:

> How am I tracking against my plan this week?

> Am I hitting my easy-pace targets, or running easy days too hard?

> I missed Tuesday's interval session — should I move it or skip it?

**What you get:** per-run grades (*Nailed it / On track / Off target / Missed*), weekly mileage adherence,
and honest feedback — especially flagging the most common mistake, running easy days too fast.

---

## 7. Just curious

> What was my fastest 10K this year?

> What's my average cadence, and has it changed over the last few months?

> How much total elevation have I climbed this year?

---

## Tips for good answers

- **Be specific about the goal.** "What pace for a flat half on Sunday?" beats "how fast am I?"
- **Tell Claude what to ignore.** e.g. "skip the second half, I bonked" or "ignore the treadmill runs."
- **Ask for the unit you want.** "in miles" or "in km" — Claude will convert.
- **Ask follow-ups.** "now show that as per-mile splits" or "make a wristband version with just the
  cumulative times."
