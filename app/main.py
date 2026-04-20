import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from pathlib import Path

load_dotenv()

app = FastAPI(title="Personal Data Science Portfolio")

BASE_DIR = Path(__file__).parent.parent

# Initialize rate limiter (L2 fix)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


# Security Headers Middleware (M1 fix)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.plot.ly cdn.tailwindcss.com cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.tailwindcss.com cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' data: cdn.jsdelivr.net"
        )
        return response


app.add_middleware(SecurityHeadersMiddleware)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Path to trading-analytics SQLite DB (override via TA_DB_PATH env var)
TA_DB_PATH = os.getenv("TA_DB_PATH", "/opt/trading-data/trading_app.db")

# Allowlisted tickers for portfolio site (H5 fix: restrict data exposure)
ALLOWED_TICKERS = {"NFLX", "TSLA"}


# ── Helpers ──────────────────────────────────────────────────────────────────


def _clean(series):
    return [None if pd.isna(x) else round(float(x), 4) for x in series]


def _ta_conn():
    """Open trading-analytics database in read-only mode (L4 fix)."""
    conn = sqlite3.connect(f"file:{TA_DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _validate_ticker(ticker: str) -> str:
    """Validate ticker is in allowlist (H5 fix: restrict data exposure)."""
    ticker = ticker.strip().upper()
    if ticker not in ALLOWED_TICKERS:
        raise HTTPException(
            status_code=403,
            detail=f"Ticker '{ticker}' is not available. Only {', '.join(sorted(ALLOWED_TICKERS))} are supported.",
        )
    return ticker


def _ta_perf_summary():
    try:
        conn = _ta_conn()
        row = conn.execute(
            "SELECT mean_hit_rate, median_hit_rate, min_hit_rate, max_hit_rate, ticker_count "
            "FROM model_performance_summary ORDER BY updated_at DESC LIMIT 1"
        ).fetchone()
        conn.close()
        if not row:
            return None
        mean = float(row["mean_hit_rate"])
        median = float(row["median_hit_rate"])
        return {
            "display_rate": max(mean, median) * 100,
            "mean": mean * 100,
            "median": median * 100,
            "min": float(row["min_hit_rate"]) * 100,
            "max": float(row["max_hit_rate"]) * 100,
            "ticker_count": row["ticker_count"],
            "label": "Mean" if mean >= median else "Median",
        }
    except Exception:
        pass

    # Fallback: compute summary from ml_model_metrics
    try:
        conn = _ta_conn()
        rows = conn.execute(
            "SELECT metric_value FROM ml_model_metrics WHERE metric_name='hit_rate'"
        ).fetchall()
        conn.close()
        if not rows:
            return None
        rates = [float(r["metric_value"]) for r in rows]
        mean = sum(rates) / len(rates)
        sorted_rates = sorted(rates)
        mid = len(sorted_rates) // 2
        median = (sorted_rates[mid] + sorted_rates[~mid]) / 2
        return {
            "display_rate": max(mean, median) * 100,
            "mean": mean * 100,
            "median": median * 100,
            "min": min(rates) * 100,
            "max": max(rates) * 100,
            "ticker_count": len(set(rates)),
            "label": "Mean" if mean >= median else "Median",
        }
    except Exception:
        return None


def _ta_watchlist():
    try:
        conn = _ta_conn()
        fixed = {
            r["ticker"]
            for r in conn.execute("SELECT ticker FROM watchlist_tickers").fetchall()
        }
        if not fixed:
            conn.close()
            return [], None

        placeholders = ",".join("?" * len(fixed))
        rows = conn.execute(
            f"SELECT ticker, last_price, buy_score, signal, reasoning, "
            f"win_rate, total_trades, total_pnl_pct, is_low_performance "
            f"FROM scanned_tickers WHERE ticker IN ({placeholders})",
            list(fixed),
        ).fetchall()

        last_refresh = None
        row = conn.execute(
            "SELECT last_run_time FROM task_logs ORDER BY last_run_time DESC LIMIT 1"
        ).fetchone()
        if row and row["last_run_time"]:
            try:
                last_refresh = datetime.fromisoformat(str(row["last_run_time"]))
            except Exception:
                pass

        conn.close()
    except Exception:
        return [], None

    items = [
        {
            "ticker": r["ticker"],
            "last_price": r["last_price"],
            "buy_score": r["buy_score"] or 0,
            "signal": r["signal"] or "No Signal",
            "reasoning": r["reasoning"] or "Awaiting next algorithmic scan...",
            "win_rate": r["win_rate"] or 0,
            "total_trades": r["total_trades"] or 0,
            "total_pnl_pct": r["total_pnl_pct"] or 0,
            "is_low_performance": bool(r["is_low_performance"]),
            "in_fixed": True,
            "in_portfolio": False,
        }
        for r in rows
    ]
    sorted_items = sorted(items, key=lambda x: x["buy_score"], reverse=True)
    return sorted_items[:2], last_refresh


# ── Project data ──────────────────────────────────────────────────────────────

PROJECTS = [
    {
        "id": 1,
        "slug": "trading-analytics",
        "title": "Swing Trading Analytics Dashboard",
        "description": (
            "A professional-grade automated stock analysis system combining "
            "technical indicators, AI forecasting, and sentiment analysis to "
            "generate actionable swing trading signals."
        ),
        "tags": ["CatBoost", "LightGBM", "Time Series", "Plotly", "FastAPI"],
        "highlights": [
            "Ensemble AI model (CatBoost + LightGBM + Theta) producing 30-day price forecasts",
            "Dual-mode strategy: Mean Reversion (buying oversold dips) and Trend Following (momentum breakouts)",
            "Buy signals gated by RSI, MACD alignment, relative volume > 1.2, buy pressure, and news sentiment",
            "Automated risk management: 2.5× ATR trailing stop, −10% hard stop, +20% take-profit",
            "Sector exposure cap at 20% per industry to prevent over-concentration",
            "Automated scans (3× per day via Celery Beat) with email alerts on strong signals",
        ],
        "tech_stack": [
            "CatBoost",
            "LightGBM",
            "DynamicOptimizedTheta",
            "Optuna",
            "FastAPI",
            "Celery",
            "Redis",
            "Plotly",
            "VADER Sentiment",
            "yfinance",
        ],
    },
]


# ── Pages ─────────────────────────────────────────────────────────────────────


@app.get("/")
async def homepage(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/projects")
async def projects_page(request: Request):
    return templates.TemplateResponse(request, "projects.html", {"projects": PROJECTS})


# Trading Analytics — must be defined BEFORE the generic /projects/{slug} route


@app.get("/projects/trading-analytics", response_class=HTMLResponse)
async def trading_analytics_page(request: Request):
    project = next(p for p in PROJECTS if p["slug"] == "trading-analytics")
    watchlist, last_refresh = _ta_watchlist()
    perf = _ta_perf_summary()
    return templates.TemplateResponse(
        request,
        "trading_analytics_detail.html",
        {
            "project": project,
            "watchlist": watchlist,
            "last_refresh": last_refresh,
            "perf": perf,
        },
    )


@app.get("/projects/trading-analytics/plot/{ticker}", response_class=HTMLResponse)
async def ta_plot_container(request: Request, ticker: str):
    ticker = _validate_ticker(ticker)
    return templates.TemplateResponse(
        request,
        "trading_plot_container.html",
        {"request": request, "ticker": ticker},
    )


@app.get("/projects/trading-analytics/api/plot-data/{ticker}")
@limiter.limit("30/minute")  # L2 fix: rate limiting
async def ta_plot_data(request: Request, ticker: str):
    ticker = _validate_ticker(ticker)
    conn = _ta_conn()

    rows = conn.execute(
        "SELECT dt, open, high, low, close, volume FROM stock_data "
        "WHERE ticker=? AND interval='1d' ORDER BY dt ASC",
        (ticker,),
    ).fetchall()

    if not rows:
        conn.close()
        raise HTTPException(status_code=404, detail=f"No stock data for {ticker}")

    df = pd.DataFrame(
        list(rows), columns=["dt", "open", "high", "low", "close", "volume"]
    )
    df["dt"] = pd.to_datetime(df["dt"])
    df = df.set_index("dt").sort_index()

    # Technical indicators
    df["MA20"] = df["close"].rolling(20).mean()
    df["MA50"] = df["close"].rolling(50).mean()
    df["MA200"] = df["close"].rolling(200).mean()

    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["RSI"] = 100 - (100 / (1 + gain / loss))

    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()

    dates = df.index.strftime("%Y-%m-%d").tolist()

    # Backtest signals
    signals = conn.execute(
        "SELECT signal_type, date, price FROM backtest_signals WHERE ticker=? ORDER BY date",
        (ticker,),
    ).fetchall()
    backtest_signals = [
        {"type": s["signal_type"], "date": s["date"], "price": s["price"]}
        for s in signals
    ]

    # Current signal from scanned_tickers
    st = conn.execute(
        "SELECT signal FROM scanned_tickers WHERE ticker=? LIMIT 1", (ticker,)
    ).fetchone()
    current_signal = st["signal"] if st else "No Signal"

    # ML predictions
    latest_ts_row = conn.execute(
        "SELECT MAX(prediction_date) as ts FROM ml_predictions WHERE ticker=?",
        (ticker,),
    ).fetchone()
    latest_ts = latest_ts_row["ts"] if latest_ts_row else None

    prediction_intervals = {}
    hit_rates = {}
    best_model = None

    if latest_ts:
        try:
            window_start = (
                datetime.fromisoformat(str(latest_ts)) - timedelta(seconds=60)
            ).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            window_start = latest_ts

        preds = conn.execute(
            "SELECT model_name, target_date, predicted_price, lower_bound_80, upper_bound_80 "
            "FROM ml_predictions WHERE ticker=? AND prediction_date >= ? ORDER BY model_name, target_date",
            (ticker, window_start),
        ).fetchall()

        for p in preds:
            mn = p["model_name"]
            if mn not in prediction_intervals:
                prediction_intervals[mn] = {
                    "dates": [],
                    "predicted_prices": [],
                    "lower_bound_80": [],
                    "upper_bound_80": [],
                }
            prediction_intervals[mn]["dates"].append(str(p["target_date"])[:10])
            prediction_intervals[mn]["predicted_prices"].append(p["predicted_price"])
            prediction_intervals[mn]["lower_bound_80"].append(p["lower_bound_80"])
            prediction_intervals[mn]["upper_bound_80"].append(p["upper_bound_80"])

        metrics = conn.execute(
            "SELECT model_name, metric_name, metric_value FROM ml_model_metrics WHERE ticker=?",
            (ticker,),
        ).fetchall()
        hit_rates = {
            m["model_name"]: m["metric_value"]
            for m in metrics
            if m["metric_name"] == "hit_rate"
        }
        best_model = max(hit_rates, key=hit_rates.get) if hit_rates else None

    conn.close()

    return {
        "ticker": ticker,
        "signal": current_signal,
        "confirmation_days": 3,
        "last_price_ts": None,
        "dates": dates,
        "open": _clean(df["open"]),
        "high": _clean(df["high"]),
        "low": _clean(df["low"]),
        "close": _clean(df["close"]),
        "ma20": _clean(df["MA20"]),
        "ma50": _clean(df["MA50"]),
        "ma200": _clean(df["MA200"]),
        "rsi": _clean(df["RSI"]),
        "rsi_dynamic": [],
        "macd": _clean(df["MACD"]),
        "macd_signal": _clean(df["Signal_Line"]),
        "macd_hist": _clean(df["MACD"] - df["Signal_Line"]),
        "backtest_signals": backtest_signals,
        "backtest_performance": {},
        "prediction_intervals": prediction_intervals,
        "hit_rates": hit_rates,
        "best_model": best_model,
    }


@app.get("/projects/trading-analytics/api/ml-forecast/{ticker}")
@limiter.limit("30/minute")  # L2 fix: rate limiting
async def ta_ml_forecast(request: Request, ticker: str):
    ticker = _validate_ticker(ticker)
    conn = _ta_conn()

    latest_ts_row = conn.execute(
        "SELECT MAX(prediction_date) as ts FROM ml_predictions WHERE ticker=?",
        (ticker,),
    ).fetchone()
    latest_ts = latest_ts_row["ts"] if latest_ts_row else None

    if not latest_ts:
        conn.close()
        return {"error": f"No predictions for {ticker}"}

    try:
        window_start = (
            datetime.fromisoformat(str(latest_ts)) - timedelta(seconds=60)
        ).isoformat()
    except Exception:
        window_start = latest_ts

    preds = conn.execute(
        "SELECT model_name, target_date, predicted_price, lower_bound_80, upper_bound_80 "
        "FROM ml_predictions WHERE ticker=? AND prediction_date >= ? ORDER BY model_name, target_date",
        (ticker, window_start),
    ).fetchall()

    models = {}
    for p in preds:
        mn = p["model_name"]
        if mn not in models:
            models[mn] = []
        entry = {
            "date": str(p["target_date"])[:10],
            "price": round(float(p["predicted_price"]), 2),
        }
        if p["lower_bound_80"] is not None:
            entry["lower_bound_80"] = round(float(p["lower_bound_80"]), 2)
            entry["upper_bound_80"] = round(float(p["upper_bound_80"]), 2)
        models[mn].append(entry)

    metrics = conn.execute(
        "SELECT model_name, metric_name, metric_value FROM ml_model_metrics WHERE ticker=?",
        (ticker,),
    ).fetchall()
    hit_rates = {
        m["model_name"]: m["metric_value"]
        for m in metrics
        if m["metric_name"] == "hit_rate"
    }
    wapes = {
        m["model_name"]: m["metric_value"]
        for m in metrics
        if m["metric_name"] == "wape"
    }
    best_model = max(hit_rates, key=hit_rates.get) if hit_rates else None

    conn.close()
    return {
        "ticker": ticker,
        "models": models,
        "hit_rates": hit_rates,
        "wapes": wapes,
        "best_model": best_model,
    }


# Generic project detail (all other slugs)


@app.get("/projects/{slug}")
async def project_detail(request: Request, slug: str):
    project = next((p for p in PROJECTS if p["slug"] == slug), None)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return templates.TemplateResponse(
        request, "project_detail.html", {"project": project}
    )


@app.get("/api/projects")
async def get_projects():
    return [
        {k: v for k, v in p.items() if k not in ("highlights", "tech_stack")}
        for p in PROJECTS
    ]
