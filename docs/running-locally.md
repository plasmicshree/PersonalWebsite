# Running the Website Locally

## Full Stack Local Dev (Quick Start)

Both repos must run simultaneously for the trading-analytics page to show live data.

**Terminal 1 — trading-analytics (Docker):**
```powershell
cd D:\PythonRepos\trading-analytics
docker compose up -d
# Web: http://localhost:8000  |  Flower: http://localhost:5566/flower
```

**Terminal 2 — PersonalWebsite:**
```powershell
cd D:\PythonRepos\PersonalWebsite
uvicorn app.main:app --reload --port 8080
# Site: http://localhost:8080
```

To stop everything:
```powershell
# Terminal 2: Ctrl+C
# Terminal 1:
docker compose down
```

---

## Prerequisites
- Python 3.11+ (verify: `python --version`)
- Windows (hardcoded database path is Windows-specific)
- Dependencies installed (see **Setup** below)

## Setup (One-Time)

### 1. Install Dependencies
```bash
cd d:/PythonRepos/PersonalWebsite
pip install -r requirements.txt
```

**Current dependencies** (`requirements.txt`):
- `fastapi>=0.115.0`
- `uvicorn[standard]>=0.30.0`
- `jinja2==3.1.4`
- `python-multipart>=0.0.9`
- `scikit-learn>=1.5.0`
- `joblib>=1.4.0`

### 2. Verify Database Path
The app expects trading-analytics database at:
```
D:/PythonRepos/trading-analytics/data/trading_app.db
```

If the path is different, edit `app/main.py:18`:
```python
TA_DB_PATH = str(Path("D:/PythonRepos/trading-analytics/data/trading_app.db"))
```

## Running the Server

### Start Development Server
```bash
cd d:/PythonRepos/PersonalWebsite
uvicorn app.main:app --reload --port 8080
```

**Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8080
INFO:     Application startup complete.
```

### Access the Website
- **Homepage**: http://localhost:8080
- **Projects**: http://localhost:8080/projects
- **Trading Analytics**: http://localhost:8080/projects/trading-analytics

### Stop the Server
Press `Ctrl+C` in the terminal.

## Development Workflow

### Template Changes (Hot Reload)
- Edit any `.html` file
- Refresh browser (Ctrl+R)
- Changes appear immediately (no server restart needed)

### Python Code Changes (Restart Required)
- Edit `app/main.py`
- Stop server (Ctrl+C)
- Start server again
- Refresh browser

**Note**: The `--reload` flag auto-restarts on file changes, but new functions (like `_ta_perf_summary()`) require a fresh server start to be picked up.

### CSS Changes (Tailwind CDN)
- Edit `static/css/style.css`
- Refresh browser (Ctrl+R)
- Changes appear immediately

**Note**: Tailwind is loaded via CDN, so all utility classes (e.g., `text-sky-400`, `bg-slate-950`) work without a build step.

## Testing Routes Manually

### Homepage
```
GET http://localhost:8080/
```
Returns: HTML homepage with hero, skills, experience, education.

### Projects Gallery
```
GET http://localhost:8080/projects
```
Returns: HTML project cards.

### Trading Analytics Project Page
```
GET http://localhost:8080/projects/trading-analytics
```
Returns: HTML with stat bar, watchlist, insight cards.

### Plot Data API
```
GET http://localhost:8080/projects/trading-analytics/api/plot-data/AAPL
```
Returns: JSON with OHLCV, indicators, backtest signals, ML predictions.

Example response:
```json
{
  "ticker": "AAPL",
  "signal": "Strong Buy",
  "dates": ["2026-01-01", "2026-01-02", ...],
  "close": [150.25, 150.50, ...],
  "ma20": [149.10, 149.30, ...],
  "rsi": [65.3, 66.1, ...],
  "macd": [0.45, 0.48, ...],
  "prediction_intervals": {
    "CatBoost": {
      "dates": ["2026-01-15"],
      "predicted_prices": [155.20],
      "lower_bound_80": [153.10],
      "upper_bound_80": [157.30]
    }
  },
  "hit_rates": {
    "CatBoost": 0.63,
    "LightGBM": 0.54,
    "Theta": 0.51
  },
  "best_model": "CatBoost"
}
```

### ML Forecast API
```
GET http://localhost:8080/projects/trading-analytics/api/ml-forecast/AAPL
```
Returns: JSON with model predictions + hit rates + WAPE.

Example response:
```json
{
  "ticker": "AAPL",
  "models": {
    "CatBoost": [
      {
        "date": "2026-01-15",
        "price": 155.20,
        "lower_bound_80": 153.10,
        "upper_bound_80": 157.30
      }
    ]
  },
  "hit_rates": {
    "CatBoost": 0.63,
    "LightGBM": 0.54,
    "Theta": 0.51
  },
  "wapes": {
    "CatBoost": 0.0234
  },
  "best_model": "CatBoost"
}
```

### Project List API
```
GET http://localhost:8080/api/projects
```
Returns: JSON list of projects (used by homepage for featured projects preview).

Example response:
```json
[
  {
    "id": 1,
    "slug": "trading-analytics",
    "title": "Swing Trading Analytics Dashboard",
    "description": "A professional-grade automated stock analysis system...",
    "tags": ["CatBoost", "LightGBM", "Time Series", "Plotly", "FastAPI"]
  }
]
```

## Troubleshooting

### Error: `[Errno 10048] only one usage of each socket address`
**Cause**: Another process is using port 8080.

**Fix**: Use a different port:
```bash
uvicorn app.main:app --reload --port 8090
```
Then visit: http://localhost:8090

Or kill the existing process:
```bash
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Error: `ModuleNotFoundError: No module named 'fastapi'`
**Cause**: Dependencies not installed.

**Fix**: Run setup again:
```bash
pip install -r requirements.txt
```

### Error: `FileNotFoundError: trading_app.db`
**Cause**: Database path is wrong or trading-analytics is not set up.

**Fix**: Verify the path exists:
```bash
dir D:\PythonRepos\trading-analytics\data\trading_app.db
```

If missing, the page will show "No data available" in the watchlist table.

### Error: `[Errno 2] No such file or directory: 'D:\\PythonRepos\\...'`
**Cause**: Windows path format issue (backslashes).

**Fix**: The code uses `Path()` which handles this automatically. If error persists, edit `app/main.py:18` to use forward slashes:
```python
TA_DB_PATH = "D:/PythonRepos/trading-analytics/data/trading_app.db"
```

### Accuracy Tile Shows "—" (Dash)
**Cause**: `model_performance_summary` table is empty or not created.

**Fix**: Ensure trading-analytics has run at least once to populate the table. Or manually insert test data:
```python
import sqlite3
conn = sqlite3.connect("D:/PythonRepos/trading-analytics/data/trading_app.db")
conn.execute("""
    INSERT INTO model_performance_summary
    (mean_hit_rate, median_hit_rate, min_hit_rate, max_hit_rate, ticker_count)
    VALUES (0.657, 0.633, 0.367, 0.967, 122)
""")
conn.commit()
conn.close()
```

## Performance Baseline

**On Windows 11 (i7, 16GB RAM)**:
- Server startup: ~500ms
- Homepage load: ~50ms
- Trading analytics page load: ~100–150ms
- Plot data query: ~200ms
- Plotly chart render (browser): ~300ms
- Full accordion open (fetch + render): ~400–500ms

## File Watches & Auto-Reload

The `--reload` flag watches `app/` and `templates/` directories for changes. If adding new Python files in `app/`, they should be picked up automatically (but new functions require server restart).

**To watch additional directories**, pass `--reload-dir`:
```bash
uvicorn app.main:app --reload --reload-dir app --reload-dir templates --port 8080
```

## Browser DevTools

### Network Tab
- Monitor API calls to `/api/plot-data/{ticker}` and `/api/ml-forecast/{ticker}`
- Verify response size (~100–500 KB for plot data)

### Console Tab
- Check for JavaScript errors in Plotly rendering
- Alpine.js debug: open console and type `document.documentElement.__x` to inspect state

### Elements Tab
- Inspect Tailwind utility classes
- Verify `data-loaded="true"` attribute on accordions after opening

## Production Considerations

This guide covers **development only**. For production deployment, see `plan.md` for:
- Hetzner Cloud VPS setup
- Systemd service for auto-restart
- Caddy reverse proxy + HTTPS
- Domain setup (Cloudflare Registrar)
