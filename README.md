# 🏃 strava-coach

**Turn Claude into your personal running coach, powered by your own Strava data.**

Ask Claude things like *"How did last week go?"* or *"What pace should I run my half marathon?"* and get
real answers based on your actual runs — paces, heart rate, splits, and how you're tracking toward a goal.

```
You:    I'm running a half marathon Sunday on a flat course. What pace should I target?
Claude: Looking at your runs… your long runs sit at 75% max HR (very aerobic), and the first
        half of your Napa marathon held 8:59/mi at only 151 bpm. For Sunday I'd target 9:00/mi
        (~1:58), let heart rate confirm it in the first 3 miles, then negative-split the finish.
```

It works for **everyone** — you do *not* need to be a programmer. The steps below are click-by-click.
There's an [advanced track](#-advanced--developer-track) further down if you'd rather clone from GitHub.

---

## What it can do

| | |
|---|---|
| 📊 **Ask anything about your training** | "What was my fastest 10K this year?" · "Show heart-rate drift on Sunday's long run" · "Am I running my easy days too hard?" |
| 🎯 **Build a training plan** | Claude interviews you like a coach and writes a week-by-week, pace-targeted plan toward your goal race. |
| ✅ **Auto-grade your runs** | Every time you start Claude, it quietly pulls new runs and grades them vs your plan (*Nailed it / On track / Off target / Missed*). |
| 🖥️ **Browse runs locally** | A simple web page on your own computer to sync and click through your activities. |
| 🔒 **Stays on your machine** | Your data lives in a folder on your computer. Nothing is uploaded anywhere except to Strava's own API to read your runs. |

> **Note:** Strava only has data *after* you finish a run, so "live" here means a fresh pull each
> time you ask — not real-time tracking during a run.

---

## ⚡ Quick start (5 steps, ~10 minutes)

You'll do this once. After that, just talk to Claude.

### Step 1 — Install the plugin

In Claude Code, type:

```
/plugin marketplace add OceanHelloWorld/strava_local_coach
/plugin install strava-coach@your-plugins
```

That's it — the plugin is installed. (It needs **Python 3.10+** on your computer, which Macs and most
Linux machines already have. Type `python3 --version` in a terminal to check.)

### Step 2 — Create a free Strava API app

This is how Strava gives *your* Claude permission to read *your* runs. It takes 2 minutes.

1. Go to **<https://www.strava.com/settings/api>** (log in to Strava if asked).
2. Fill in the form:
   - **Application Name:** anything, e.g. `My Coach`
   - **Category:** `Training`
   - **Website:** anything, e.g. `http://localhost`
   - **Authorization Callback Domain:** type exactly `localhost` ← *this one matters*
3. Click **Create**. You'll now see a **Client ID** (a number) and a **Client Secret** (a long code).
   Keep this page open — you need both in the next step.

### Step 3 — Save your two secrets so Claude can find them

Your Client ID and Secret need to live in a file that every program on your computer can read.

**On a Mac (or Linux with zsh — the default):** open the Terminal app and paste this, replacing the
two values with yours from Step 2:

```bash
echo 'export STRAVA_CLIENT_ID=PASTE_YOUR_ID_HERE'       >> ~/.zshenv
echo 'export STRAVA_CLIENT_SECRET=PASTE_YOUR_SECRET_HERE' >> ~/.zshenv
```

> 💡 **Why `~/.zshenv` and not `~/.zshrc`?** `~/.zshrc` is only read by terminal windows you open
> yourself. The coach runs quietly in the background, where only `~/.zshenv` is read. Using the wrong
> file is the #1 setup mistake — it makes the coach say *"Not connected to Strava yet"* forever even
> though everything looks right. (On bash, use `~/.bash_profile` and the same two `export` lines.)

**Now fully quit and reopen Claude Code** so it picks up the new values. To confirm they're set, open a
**new** terminal and run `echo $STRAVA_CLIENT_ID` — it should print your number.

### Step 4 — Connect your Strava account (one click in your browser)

Paste this single line into your terminal. It finds the connect script automatically and runs it:

```bash
python3 "$(find ~/.claude/plugins -name strava_login.py | head -1)"
```

Your browser opens → click **Authorize** (approve *all* the boxes) → you'll see *"Strava connected"*.
Done — your login is saved and refreshes itself automatically from now on.

### Step 5 — Tell Claude to use it

Back in Claude Code:

```
/reload-plugins
```

Then just ask: **"Sync my Strava and show my last 10 runs."** 🎉

---

## 💬 Try these (examples)

Once connected, talk to Claude in plain English. A few to get you going:

- *"Sync my Strava and summarize the last 4 weeks — mileage, average pace, and how hard I've been going."*
- *"What pace should I aim for in a flat half marathon this weekend? Check my heart rate to see how much I had left in recent runs."*
- *"Compare my two longest runs this month — was my heart rate higher for the same pace?"*
- *"Build me a training plan for a sub-2:00 half marathon 12 weeks from now. I can run 4 days a week."*
- *"Did I run my easy days too fast last week?"*
- *"Show the splits and where I slowed down in my marathon."*

👉 See **[EXAMPLES.md](EXAMPLES.md)** for more prompts and what the answers look like.

To build a structured plan specifically, you can also run the guided command:

```
/strava-coach:strava-training-plan-create
```

Every time you start a new Claude session after that, you'll get a quiet one-line check of any new runs
against your plan.

---

## 🖥️ Browse your runs in a web page (optional)

Prefer clicking over chatting? Run this in a terminal:

```bash
python3 "$(find ~/.claude/plugins -name ui.py | head -1)"
```

Open **<http://localhost:8722>** in your browser, click **Sync new** (or **Full backfill**), and click any
run to load its details and heart-rate / pace graphs.

---

## 🆘 Troubleshooting

<details>
<summary><b>"Not connected to Strava yet. Run scripts/strava_login.py first."</b></summary>

This means your credentials or login aren't reaching the background coach. Walk through, in order:

1. **Are your secrets visible everywhere?** Open a **new** terminal and run `echo $STRAVA_CLIENT_ID`.
   - Blank? They're in the wrong file. Put them in **`~/.zshenv`** (see [Step 3](#step-3--save-your-two-secrets-so-claude-can-find-them)), not `~/.zshrc`. Then fully restart Claude Code.
2. **Did the login actually finish?** Re-run the connect command from [Step 4](#step-4--connect-your-strava-account-one-click-in-your-browser) and make sure you approved **all** permission boxes (you need `activity:read_all`).
3. **Did the coach reload?** After connecting, run `/reload-plugins` in Claude, or quit and reopen it.
4. **Is the token file there?** Check that `~/.config/strava-coach/tokens.json` exists.
</details>

<details>
<summary><b>"Missing Strava credentials. Set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET."</b></summary>

Claude can't see your two secrets. Same fix as #1 above: put both `export` lines in `~/.zshenv`,
restart Claude Code, and confirm with `echo $STRAVA_CLIENT_ID` in a new terminal.
</details>

<details>
<summary><b>"python3: command not found" or a Python version error</b></summary>

You need **Python 3.10 or newer**. On a Mac, install it from <https://www.python.org/downloads/> or via
Homebrew (`brew install python`). Then re-run the failing command.
</details>

<details>
<summary><b>The browser didn't open during login</b></summary>

The connect script prints a URL like `https://www.strava.com/oauth/authorize?...`. Copy it into your
browser manually and approve the permissions there.
</details>

---

## 🔍 How it works (plain English)

- When you ask Claude about your running, it uses a small built-in helper (an "MCP server") to read your
  runs from a folder on your computer, and to fetch fresh data from Strava when needed.
- A training plan is just a file (`plan.json`) Claude writes when you do the plan interview.
- Each session, a tiny background step pulls new runs and checks them against that plan.
- Strava's login expires every 6 hours; the coach renews it automatically using the secrets from Step 3,
  so you only log in once.

### Where your data lives

Everything is stored under **`~/.config/strava-coach/`**:

| File | What it is |
|------|------------|
| `tokens.json` | Your Strava login (saved with private `0600` permissions) |
| `activities.json` | Summaries of your synced runs |
| `plan.json` | Your training plan |
| `progress.json` | The graded runs vs your plan |

It's bounded by design: at most **100 activities** from the **last 365 days**, and only lightweight
summary fields (no route maps, photos, or per-second data). Detailed graphs are fetched on demand only
when you drill into one run.

---

## 🛠️ Advanced / developer track

Prefer to run from source, hack on it, or publish your own copy?

**Requirements:** Python 3.10+. [uv](https://docs.astral.sh/uv/) is optional but makes startup faster —
the launcher (`server/_run.sh`) uses `uv` if present, otherwise it auto-creates a local virtualenv and
`pip install`s the single dependency (`mcp`) on first run.

```bash
# Clone and run the plugin straight from the repo
git clone https://github.com/OceanHelloWorld/strava_local_coach.git
cd strava_local_coach
export STRAVA_CLIENT_ID=...           # see Step 2 above
export STRAVA_CLIENT_SECRET=...
python3 scripts/strava_login.py       # one-time browser login
claude --plugin-dir .                 # launch Claude Code with this plugin
```

To publish it as your own marketplace: push to your GitHub, update the `author`/`owner` fields in
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, then have others run
`/plugin marketplace add <you>/<repo>` and `/plugin install strava-coach@<marketplace-name>`.

**Custom data location:** the default is `~/.config/strava-coach/`. To use a different folder, set
`STRAVA_DATA_DIR` to an **absolute path** in your environment (e.g. in `~/.zshenv`) before launching
Claude Code.

### Project layout

| Path | Role |
|------|------|
| `.mcp.json` | Declares the stdio MCP server (`strava`) and passes through your credentials |
| `.claude-plugin/` | Plugin + marketplace manifests |
| `server/_run.sh` | Launcher: uses `uv`, else auto-creates a venv with `mcp` |
| `server/strava_server.py` | The MCP tools (profile, sync, list/detail, streams, plan, grading) |
| `server/strava_client.py` | Strava OAuth refresh + HTTP (Python stdlib only) |
| `server/sync.py` | Capped incremental sync + run grading (also the SessionStart hook) |
| `server/vdot.py` | VDOT pace bands + grading logic |
| `server/store.py` | JSON file storage |
| `server/ui.py` | The localhost activity browser |
| `scripts/strava_login.py` | One-time OAuth bootstrap |
| `skills/` | The "ask anything" and "create a plan" skills |
| `hooks/hooks.json` | SessionStart auto-sync + grade |

### The MCP tools (for reference)

`get_athlete_profile` · `sync_activities` · `list_activities` · `get_activity` ·
`get_activity_streams` · `get_training_plan` · `save_training_plan` · `compute_vdot_paces` ·
`evaluate_progress`

---

## 🔒 Privacy

All data stays on your machine, under `~/.config/strava-coach/` (or your `$STRAVA_DATA_DIR`), with tokens
written `0600` (only you can read them). The plugin talks to exactly one external service — Strava's own
API — to read your activities. Nothing else is uploaded, shared, or phoned home.

## License

MIT
