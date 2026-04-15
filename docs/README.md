# Documentation Index

Welcome! This folder contains guides to help you understand, run, and extend the Personal Data Science Portfolio Website.

## Quick Start
**First time here?** Start with this flow:
1. Read [overview.md](overview.md) (5 min) — Understand the project architecture
2. Read [running-locally.md](running-locally.md) (5 min) — Get the server running
3. Read [trading-analytics-feature.md](trading-analytics-feature.md) (10 min) — Deep dive into the main feature
4. Read [next-steps.md](next-steps.md) (5 min) — Understand what's done & what's pending

## The Files

### [overview.md](overview.md)
**What**: High-level project architecture, tech stack, file structure, data flow

**For whom**: Anyone new to the project who wants to understand the big picture

**Key topics**:
- Tech stack (FastAPI, Tailwind, SQLite, Plotly)
- File structure and route mappings
- Database schema (trading_app.db tables)
- Key design decisions
- Performance baselines
- Known limitations

**Read time**: 5–10 minutes

---

### [trading-analytics-feature.md](trading-analytics-feature.md)
**What**: In-depth walkthrough of the Trading Analytics project page (the main feature)

**For whom**: Developers who want to understand or modify the trading analytics feature

**Key topics**:
- What the feature is (stat bar, watchlist, charts)
- How the dynamic accuracy stat works (DB integration)
- Font size changes applied
- Strategy rules section (threshold hiding)
- Lazy-loaded accordion mechanism
- Integration with trading-analytics cron job
- How to test it locally
- Known issues & TODOs

**Read time**: 15–20 minutes

---

### [running-locally.md](running-locally.md)
**What**: How to start the development server, test routes, troubleshoot

**For whom**: Anyone who wants to run the website locally or test changes

**Key topics**:
- Prerequisites & setup
- Starting the server (uvicorn commands)
- Template hot-reload (no restart needed)
- Python code changes (requires restart)
- Manual route testing (curl/browser)
- Troubleshooting common errors (port conflicts, missing DB, etc.)
- Performance baseline timings
- DevTools tips

**Read time**: 10–15 minutes

---

### [next-steps.md](next-steps.md)
**What**: Project status, what's done, what's pending, how to continue

**For whom**: Project managers, future-you planning the next work phase

**Key topics**:
- ✅ Complete work (Phase 1–4)
- 🚧 In progress (none currently)
- ⏳ Pending work (short, medium, long term)
- Known limitations to address (priority + solution)
- Files modified in latest session
- How to continue work later
- Git setup suggestion
- Questions to ask when resuming

**Read time**: 10–15 minutes

---

## Common Scenarios

### "I want to run the website locally"
→ Read [running-locally.md](running-locally.md)

### "I want to understand how the trading analytics page works"
→ Read [trading-analytics-feature.md](trading-analytics-feature.md)

### "I'm new to the project and want the big picture"
→ Read [overview.md](overview.md)

### "I want to add a new feature / extend the project"
→ Read [overview.md](overview.md), then [next-steps.md](next-steps.md) for ideas

### "I want to deploy to production"
→ See `../plan.md` (original architecture plan) — covers Hetzner VPS, Caddy, domain setup

### "I want to troubleshoot an error"
→ See **Troubleshooting** section in [running-locally.md](running-locally.md)

## Project at a Glance

| | |
|---|---|
| **Status** | Trading Analytics feature complete; ready for extension or deployment |
| **Tech Stack** | FastAPI, Tailwind CSS, Alpine.js, Plotly.js, SQLite |
| **Main Feature** | Trading Analytics project page (stat bar, watchlist, technical charts) |
| **Data Source** | SQLite database from trading-analytics repo |
| **Last Update** | 2026-04-13 (font size improvements to stat tiles) |
| **Server** | Uvicorn on port 8080 |
| **Database Path** | `D:/PythonRepos/trading-analytics/data/trading_app.db` |

## Key Contacts & Links

- **GitHub**: https://github.com/plasmicshree
- **LinkedIn**: https://www.linkedin.com/in/shree-bhattarai-phd-92625316/
- **Email**: shree.bhattarai@gmail.com
- **trading-analytics repo**: `D:/PythonRepos/trading-analytics/`

## Glossary

| Term | Meaning |
|------|---------|
| **Stat bar** | 4 tiles showing accuracy %, models, scan cadence, forecast horizon |
| **Watchlist** | Table of top 2 tickers with buy scores and backtest KPIs |
| **Accordion** | Expandable row in the watchlist; lazy-loads technical chart |
| **OHLCV** | Open, High, Low, Close, Volume (candlestick data) |
| **Directional Accuracy** | Hit rate: % of predictions where price direction (up/down) was correct |
| **Backtest** | Historical simulation: testing strategy on past data |
| **MA20/50/200** | 20/50/200-day moving averages (trend indicators) |
| **RSI** | Relative Strength Index (momentum oscillator, 0–100 scale) |
| **MACD** | Moving Average Convergence Divergence (trend-following momentum indicator) |
| **Model Ensemble** | CatBoost + LightGBM + DynamicOptimizedTheta (3 complementary models) |
| **Cron job** | Automated task that runs on a schedule (training happens 3× daily) |

## File Tree

```
PersonalWebsite/
├── docs/
│   ├── README.md                   ← You are here
│   ├── overview.md                 ← Start here for architecture
│   ├── trading-analytics-feature.md ← Deep dive into main feature
│   ├── running-locally.md          ← How to run & test
│   └── next-steps.md               ← Status & pending work
├── app/
│   └── main.py                     # FastAPI routes & logic
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── projects.html
│   ├── project_detail.html
│   ├── trading_analytics_detail.html ← Main feature template
│   └── trading_plot_container.html
├── static/
│   ├── css/style.css
│   ├── profile.jpg
│   └── projects/SPYG.png
├── requirements.txt
├── .gitignore
├── plan.md                         # Original deployment plan
└── README.md                       # (Optional: GitHub intro)
```

## Tips for Success

1. **Always restart the server** if you modify Python code (the `--reload` flag doesn't pick up new functions)
2. **Refresh the browser** (Ctrl+R) after template changes to clear cache
3. **Check DevTools** (F12) → Network tab to debug API calls
4. **Query the DB directly** to verify data is there:
   ```bash
   sqlite3 D:\PythonRepos\trading-analytics\data\trading_app.db
   ```
5. **Keep notes** of any changes you make, so future-you remembers why

## Getting Help

- **Python error?** Check [running-locally.md](running-locally.md) → Troubleshooting
- **What was the last change?** Check [next-steps.md](next-steps.md) → "Files Modified This Session"
- **How does [feature] work?** Check [trading-analytics-feature.md](trading-analytics-feature.md)
- **Where's [file]?** Check [overview.md](overview.md) → Project Structure

---

**Last Updated**: 2026-04-13  
**Maintainer**: Shree K Bhattarai
