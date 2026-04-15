# Personal Data Science Portfolio Website — Project Overview

## Current Status
A professional portfolio website showcasing ML projects with live, interactive dashboards. **Primary feature complete**: Trading Analytics project page with dynamic stat tiles, watchlist table, and deep-dive technical charts.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI (Python) | REST API, template rendering, data aggregation |
| **Frontend** | HTML + Tailwind CSS + Alpine.js | Responsive UI, zero-build-step, interactive forms |
| **Database** | SQLite (trading-analytics) | Real trading data, ML metrics, predictions |
| **Charts** | Plotly.js | Interactive candlestick & indicator visualizations |
| **Styling** | Tailwind CSS (CDN) | Utility-first dark theme |

## Project Structure

```
PersonalWebsite/
├── app/
│   └── main.py                          # FastAPI app, routes, helper functions
├── static/
│   ├── css/
│   │   └── style.css                   # Custom overrides (minimal)
│   ├── profile.jpg                     # Hero image
│   └── projects/
│       └── SPYG.png                    # Project preview image
├── templates/
│   ├── base.html                       # Shared layout (nav, footer, CDN imports)
│   ├── index.html                      # Home page (hero, skills, experience, education)
│   ├── projects.html                   # Projects gallery
│   ├── project_detail.html             # Generic project detail template
│   ├── trading_analytics_detail.html    # ★ Trading analytics project page
│   └── trading_plot_container.html     # Accordion chart container (lazy-loaded)
├── docs/
│   ├── overview.md                     # This file
│   ├── trading-analytics-feature.md    # Deep dive into trading analytics
│   ├── running-locally.md              # How to run & test locally
│   └── next-steps.md                   # What's done, what's pending
├── requirements.txt
├── .gitignore
└── plan.md                             # Original architecture & deployment plan
```

## Key Routes

| Endpoint | Description |
|----------|-------------|
| `GET /` | Homepage (hero, skills, experience, education) |
| `GET /projects` | Projects gallery (card grid) |
| `GET /projects/trading-analytics` | **Trading analytics project page** (stat bar, watchlist, insights) |
| `GET /projects/trading-analytics/plot/{ticker}` | Lazy-loaded accordion chart for ticker |
| `GET /projects/trading-analytics/api/plot-data/{ticker}` | OHLCV + indicators + backtest signals + ML predictions |
| `GET /projects/trading-analytics/api/ml-forecast/{ticker}` | ML model hit rates & WAPE metrics |
| `GET /projects/{slug}` | Generic project detail page |
| `GET /api/projects` | JSON list of all projects (for homepage preview) |

## Database Connection
- **Path**: `D:/PythonRepos/trading-analytics/data/trading_app.db`
- **Tables Used**:
  - `model_performance_summary` — Aggregate hit rates (mean, median, min, max, ticker_count) updated every training run
  - `scanned_tickers` — Latest scan results (buy_score, signal, reasoning, win_rate, etc.)
  - `task_logs` — Task execution timestamps (last_run_time)
  - `stock_data` — Daily OHLCV + interval ('1d' or '15m')
  - `ml_predictions` — ML model forecasts (dates, prices, confidence intervals)
  - `ml_model_metrics` — Per-ticker hit rates & WAPE by model
  - `backtest_signals` — Historical signal dates + prices

## Data Flow (Trading Analytics Page)

1. **User visits** `/projects/trading-analytics`
2. **Backend** (`main.py: trading_analytics_page()`)
   - Queries `model_performance_summary` (latest row) → `perf` dict
   - Queries `scanned_tickers` → top 2 by buy_score → `watchlist`
   - Queries `task_logs` → last scan time → `last_refresh`
   - Renders `trading_analytics_detail.html` with all three
3. **Template** displays:
   - **Stat bar**: 4 tiles with accuracy %, model count, scan cadence, forecast horizon
   - **Insight cards**: "Why This Is Hard", "Signal Gate", "Production Infrastructure", "Rigorous Model Evaluation"
   - **Watchlist table**: Top 2 tickers + backtest KPIs
4. **User clicks ticker** → Accordion toggles
5. **Frontend** (JavaScript) fetches `/projects/trading-analytics/plot/{ticker}`
6. **Backend** queries plot data + indicators + ML predictions
7. **Frontend** renders Plotly chart + backtest history table

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| **SQLite for trading data** | Persistent storage on disk; no separate infrastructure |
| **Jinja2 server-side rendering** | Simple, no JavaScript framework build step |
| **Tailwind CDN** | Fast iteration, no build; dark theme out-of-box |
| **Alpine.js** | Minimal JS; handles accordion toggles & form submissions |
| **Plotly.js** | Interactive candlestick charts, built-in technical indicators |
| **Dynamic accuracy stat** | Read from DB (updated by cron) instead of hardcoding |
| **Lazy-loaded charts** | Accordions only fetch plot data on open; faster initial load |
| **Private repo notice** | Transparency: users know logic is proprietary, system is live-trading |

## Environment Variables & Secrets
- None currently used; all hardcoded paths are internal (no API keys exposed)
- Database path hardcoded in `main.py:18` — could be moved to `.env` if deploying

## Performance Notes
- **Startup**: ~500ms (imports + SQLite open)
- **Homepage**: ~50ms (0 DB queries, static template)
- **Trading analytics page**: ~100–150ms (3 DB queries + Jinja render)
- **Plot data endpoint**: ~200ms (large OHLCV query + technical indicator computation)
- **Lazy-load accordion**: ~300ms (fetch + Plotly render in browser)

## Known Limitations
1. **No caching** — every page load queries the DB fresh (acceptable at current traffic)
2. **No authentication** — public portfolio (by design)
3. **No form validation** on ticker input — assumes trading-analytics DB is clean
4. **Hardcoded database path** — Windows-specific path (would need env var for Linux/Mac)
5. **Single server process** — uvicorn on port 8080 (no load balancing needed)

## Next Steps
See [next-steps.md](next-steps.md) for pending work.
