# Project Status & Next Steps

**Last Updated**: 2026-04-13

## ✅ Complete

### Phase 1: Scaffold & Hello World
- [x] Create directory structure (`app/`, `templates/`, `static/`, `docs/`)
- [x] Create `requirements.txt` with FastAPI, Uvicorn, Jinja2, etc.
- [x] Create `app/main.py` with FastAPI app + 7 main routes
- [x] Create `templates/base.html` with nav, footer, CDN imports (Tailwind, Alpine, Plotly)
- [x] Create `templates/index.html` (hero, skills, experience, education)
- [x] Test homepage locally on port 8080

### Phase 2: Projects Gallery
- [x] Define `PROJECTS` list in `main.py` with metadata
- [x] Create `templates/projects.html` (card grid)
- [x] Create generic `templates/project_detail.html`
- [x] Route: `GET /projects` and `GET /projects/{slug}`

### Phase 3: Live Prediction Widgets (Trading Analytics Focus)
- [x] Create `templates/trading_analytics_detail.html` with:
  - [x] Private repo notice (lock icon + explanation)
  - [x] Strategy rules (entry/exit conditions, no thresholds)
  - [x] Stat bar (4 tiles):
    - [x] Dynamic directional accuracy (reads from DB)
    - [x] Model ensemble count
    - [x] Daily scan cadence
    - [x] Forecast horizon
  - [x] Insight cards (4 cards: why hard, signal gate, infrastructure, model evaluation)
  - [x] Watchlist table (top 2 tickers with KPIs)
  - [x] Accordion chart loader (lazy-load on click)
- [x] Create `templates/trading_plot_container.html` (Plotly chart + backtest table)
- [x] Create `/projects/trading-analytics` route with `_ta_perf_summary()` + `_ta_watchlist()`
- [x] Create `/projects/trading-analytics/plot/{ticker}` route
- [x] Create `/projects/trading-analytics/api/plot-data/{ticker}` endpoint
- [x] Create `/projects/trading-analytics/api/ml-forecast/{ticker}` endpoint
- [x] Integrate with trading-analytics database:
  - [x] Read `model_performance_summary` (aggregate hit rates)
  - [x] Read `scanned_tickers` (watchlist)
  - [x] Read `task_logs` (last scan time)
  - [x] Read `stock_data`, `backtest_signals`, `ml_predictions`, `ml_model_metrics`
- [x] Create `ModelPerformanceSummary` SQLAlchemy model in trading-analytics
- [x] Extend `train_model.py` to compute & persist aggregate summary after each run
- [x] Increase font sizes in stat tiles for readability
- [x] Create `/docs` folder with comprehensive guides

### Phase 4: Polish & Testing
- [x] Verify responsive design (Tailwind mobile-first)
- [x] Test dark theme (already applied)
- [x] Test all routes locally
- [x] Test database integration (plot data, ML forecasts)
- [x] Test lazy-load accordion (fetch + Plotly render)
- [x] Verify accuracy stat updates when DB changes

## 🚧 In Progress
- Nothing currently (last session completed)

## ⏳ Pending

### Short Term (If You Want to Extend)
1. **Add more projects**
   - Identify other ML projects worth showcasing
   - Create individual detail pages with prediction widgets
   - Each project could have a separate prediction endpoint

2. **Improve watchlist table**
   - Add filter by sector, signal type, score range
   - Add sort buttons (by score, win rate, P/L)
   - Add pagination if > 10 tickers

3. **Enhance technical chart**
   - Add volume profile heatmap
   - Add support for multiple timeframes (intraday 15m)
   - Add overlays (Ichimoku, Bollinger Bands)
   - Add drawing tools (trendlines, annotations)

4. **Add dark mode toggle** (if not already preferred)
   - Alpine.js + Tailwind `dark:` classes
   - Save preference to localStorage

5. **Implement basic caching**
   - Cache plot data for 5 minutes (avoid repeated queries)
   - Use a simple in-memory dict or Redis

6. **Add form validation**
   - Sanitize ticker input (uppercase, length check)
   - Validate plot data requests (return 404 if ticker not found)

### Medium Term (Before Public Launch)
1. **Environment variables**
   - Move hardcoded database path to `.env`
   - Add `DEBUG` flag, `PORT`, `HOST` config
   - Create `.env.example` template

2. **Error handling**
   - Add try-catch in all database queries
   - Return user-friendly error messages (500 errors → "Data unavailable")
   - Log errors to a file or service

3. **API rate limiting**
   - Prevent abuse of `/api/plot-data/` and `/api/ml-forecast/` endpoints
   - Use `slowapi` or similar

4. **Search/Analytics**
   - Add Google Analytics or Plausible to track visitors
   - Monitor which projects get clicked
   - Track any leads/contact form submissions

5. **Contact form**
   - Add `/contact` page with email form
   - Validate + send email via SendGrid/Mailgun
   - Or use a form service (Formspree, Basin)

6. **README**
   - Document project architecture
   - Include setup instructions
   - Link to GitHub profile

### Long Term (After Launch)
1. **Deployment**
   - Set up Hetzner Cloud CX22 VPS (~€3.29/mo)
   - Use Caddy reverse proxy + Let's Encrypt SSL
   - Configure systemd service for auto-start/restart
   - Point domain (Cloudflare Registrar) to VPS IP

2. **CI/CD Pipeline**
   - GitHub Actions to run tests on push
   - Auto-deploy to VPS on main branch

3. **Database Backups**
   - Periodic backups of trading_app.db to S3 or local storage
   - Set up monitoring/alerts for stale data

4. **Additional Features**
   - User authentication (if you want to add private portfolio tracking)
   - Email alerts when new trading signals fire
   - Mobile app (React Native/Flutter) pulling from same API
   - Webhooks to notify Slack/Discord of strong signals

## Known Limitations to Address (Optional)

| Issue | Priority | Solution |
|-------|----------|----------|
| No error handling on 404 tickers | Low | Return `HTTPException(404)` + custom error page |
| No input validation on ticker | Low | Sanitize + validate in endpoint |
| Hardcoded database path (Windows-specific) | Medium | Use `.env` or environment variable |
| No caching (every page load hits DB) | Low | Add Redis/in-memory cache with TTL |
| No mobile optimization for accordion table | Low | Add horizontal scroll or collapse columns on mobile |
| No email/contact mechanism | Medium | Add contact form or link to email |
| No tests (unit/integration) | Low | Add pytest suite for endpoints + functions |

## Files Modified This Session (2026-04-13)

| File | Change | Impact |
|------|--------|--------|
| `templates/trading_analytics_detail.html` | Font size increases in stat tiles | Improved readability |
| (all others) | No changes | Stable |

## How to Continue Work Later

1. **Read** `docs/overview.md` — understand architecture & file structure
2. **Read** `docs/trading-analytics-feature.md` — understand the main feature
3. **Read** `docs/running-locally.md` — start the server, test changes
4. **Refer to** `docs/next-steps.md` (this file) — pick your next task

## Server Restart for Production

To make all latest changes permanent on your main server:

```bash
# Stop existing server
pkill -f "uvicorn"  # or Ctrl+C if running in terminal

# Start fresh (port 8080 or preferred)
cd d:/PythonRepos/PersonalWebsite
uvicorn app.main:app --port 8080
```

The font size changes will be visible immediately after refresh.

## Git & Version Control

Currently not a git repo. Consider:
```bash
cd d:/PythonRepos/PersonalWebsite
git init
git add .
git commit -m "Initial commit: portfolio site with trading analytics"
git remote add origin https://github.com/plasmicshree/personalwebsite.git
git push -u origin main
```

Then add to `.gitignore`:
```
__pycache__/
*.pyc
.DS_Store
.env
.venv
venv/
```

## Questions to Ask When Resuming

- Which new project should be added next?
- Should the trading analytics page have more interactivity (filters, sorts, exports)?
- Ready to deploy to VPS, or more development first?
- Want to add contact/lead capture mechanism?
- Should the ML models be updated via UI, or always from trading-analytics cron?
