# strava-coach

A Claude Code plugin that turns Claude into your running coach, backed by your Strava data.

- **Build a training plan** — `/strava-coach:strava-training-plan-create` interviews you like
  a coach and writes a personalized, periodized plan (VDOT-based paces) to local storage.
- **Auto progress checks** — on every session start, it pulls your newly-logged Strava runs and
  grades them against the plan (*Nailed it / On track / Off target / Missed*).
- **Browse your activities** — a local web UI to sync and inspect your recent activities.
- **Ask anything** — Claude answers questions about your training from the stored data.

Strava is post-activity data, so "live" means a fresh on-demand pull each time you ask — not
real-time streaming during a run.

## Design / footprint

- **One dependency.** The only third-party Python package is `mcp`. Strava HTTP, JSON storage,
  the OAuth flow, and the localhost UI all use the Python standard library. No database.
- **Bounded data.** Each sync stores at most **100 activities** from the **last 365 days**, and
  only lightweight summary fields — no route maps, photos, or per-second streams. Streams are
  fetched on demand only when you drill into a single activity.
- **Data location.** `~/.config/strava-coach/` by default (override with `$STRAVA_DATA_DIR`):
  `tokens.json`, `plan.json`, `activities.json`, `progress.json`.

## Prerequisites

1. **Python 3.10+**. [uv](https://docs.astral.sh/uv/) is optional but recommended (it makes
   startup faster). You don't have to install anything else: the launcher
   `server/_run.sh` uses `uv` if present, otherwise it creates a local virtualenv and
   `pip install`s the single `mcp` dependency automatically on first run.
2. **A Strava API application** (free): go to <https://www.strava.com/settings/api>, create an
   app, and set the **Authorization Callback Domain** to `localhost`. Note your **Client ID**
   and **Client Secret**.
3. Export your credentials so Claude Code and the scripts can see them:
   ```bash
   export STRAVA_CLIENT_ID=12345
   export STRAVA_CLIENT_SECRET=your_secret_here
   ```
   (Put these in your shell profile so they persist.)

## One-time setup

```bash
# from the repo root
python3 scripts/strava_login.py      # opens a browser; approve all permissions
```
This saves your tokens to the data dir. The MCP server auto-refreshes the 6-hour access token
(and rotates the refresh token) from then on.

## Install the plugin

**Locally (development):**
```bash
claude --plugin-dir ./strava-coach
```

**From a personal GitHub marketplace:** push this repo to GitHub, edit the `author`/`owner`
fields in `.claude-plugin/plugin.json` and `marketplace.json`, then:
```
/plugin marketplace add your-github-username/strava-coach
/plugin install strava-coach@your-plugins
```

## Usage

- `/strava-coach:strava-training-plan-create` — create or replace your training plan.
- Just ask: *"How did last week's runs go vs my plan?"*, *"What was my fastest 10k this year?"*,
  *"Show HR drift on my long run Sunday."* (the analysis skill handles these).
- Each new session automatically prints a short "recent runs vs plan" summary (silent until you
  connect Strava and create a plan).

### Local activity browser

```bash
python3 server/ui.py                 # the UI is stdlib-only, no venv needed
```
Open <http://localhost:8722>, click **Sync new** (or **Full backfill**), and browse. Click a row
to load that activity's detail + streams on demand.

## Components

| Path | Role |
|------|------|
| `.mcp.json` | Declares the stdio MCP server (`strava`) |
| `server/_run.sh` | Launcher: uses `uv`, else auto-creates a venv with `mcp` |
| `server/strava_server.py` | MCP tools (profile, sync, list/detail, streams, plan, grading) |
| `server/strava_client.py` | OAuth refresh + Strava HTTP (stdlib urllib) |
| `server/sync.py` | Capped incremental sync + run grading (also the SessionStart hook) |
| `server/vdot.py` | VDOT pace bands + grading logic |
| `server/store.py` | JSON storage |
| `server/ui.py` | Localhost activity browser |
| `scripts/strava_login.py` | One-time OAuth bootstrap |
| `skills/…` | Plan-create + ask-anything skills |
| `hooks/hooks.json` | SessionStart auto sync + grade |

## Privacy

All data stays on your machine. Tokens and activities are written under `$STRAVA_DATA_DIR`
with `0600` permissions. Nothing is sent anywhere except Strava's own API.
