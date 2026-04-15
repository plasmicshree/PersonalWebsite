# Trading Analytics Project Page — Feature Deep Dive

## What It Is
A live trading analytics dashboard showcasing an automated swing-trading system. Visitors see:
1. **Stat bar** (4 tiles) — directional accuracy, model count, scan cadence, forecast horizon
2. **Insight cards** (4 cards) — why the system is hard, signal gating, infrastructure, model evaluation
3. **Watchlist table** — top 2 tickers by buy score with backtest KPIs
4. **Technical chart accordion** — on-demand Plotly candlestick + indicators + ML predictions

## Key Features

### 1. Dynamic Directional Accuracy Stat

**File**: `app/main.py` → `_ta_perf_summary()` function

**How it works:**
- Queries latest row from `model_performance_summary` table
- Reads `mean_hit_rate`, `median_hit_rate`, `min_hit_rate`, `max_hit_rate`, `ticker_count`
- **Displays** whichever is greater (mean or median) as the headline number
- **Label** shows "Mean" or "Median" depending on which is greater
- **Min/Max** displayed in sub-row for full range visibility

**Template location**: `templates/trading_analytics_detail.html` lines 70–86

```jinja2
{% if perf %}
<div class="text-4xl font-black text-sky-400 font-mono">{{ "%.0f"|format(perf.display_rate) }}%</div>
<div class="text-sm font-bold text-slate-500 uppercase tracking-widest mt-1">
  {{ perf.label }} Directional Accuracy
</div>
<div class="flex justify-center items-center gap-2 mt-2">
  <span class="text-sm text-slate-600">
    Low <span class="text-slate-400 font-mono font-bold">{{ "%.0f"|format(perf.min) }}%</span>
  </span>
  <span class="text-slate-700">·</span>
  <span class="text-sm text-slate-600">
    High <span class="text-slate-400 font-mono font-bold">{{ "%.0f"|format(perf.max) }}%</span>
  </span>
</div>
<div class="text-xs text-slate-700 mt-1">across {{ perf.ticker_count }} tickers</div>
{% endif %}
```

**Current values** (as of 2026-04-13):
- Mean: 65.7%, Median: 63.3% → **Display 66%** (labeled "Mean")
- Range: 37% – 97% across 122 tickers

**How it updates:**
- `D:\PythonRepos\trading-analytics\ML\train_model.py` calculates metrics on each run
- Appends new row to `model_performance_summary` table
- Website reads latest row on next page load
- **No manual intervention needed** — stat auto-updates

### 2. Stat Bar (4 Tiles)

**File**: `templates/trading_analytics_detail.html` lines 66–102

Three static tiles (unchanged by cron):
| Tile | Value | Meaning |
|------|-------|---------|
| **Model Ensemble** | 3 | CatBoost + LightGBM + Theta |
| **Daily Scan Cadence** | 3× | Automated scans per day |
| **Forecast Horizon** | 30d | 30-day price predictions |

One dynamic tile (described above):
| Tile | Source | Updated By |
|------|--------|-----------|
| **Directional Accuracy** | `model_performance_summary` | Cron job (train_model.py) |

### 3. Insight Cards (4 Cards)

**File**: `templates/trading_analytics_detail.html` lines 107–131

| Card | Content | Purpose |
|------|---------|---------|
| **Why This Is Hard** | Random walk, overfitting, mitigation (regime filter, multi-condition gating, walk-forward validation) | Credibility: shows rigor |
| **Signal Gate** | "Proprietary set of technical, volume, and sentiment parameters" | Mystique: intentionally vague on inner workings |
| **Production Infrastructure** | "Task scheduler fires scans 3× daily, message broker queues jobs, live prices + news ingested automatically" | Shows sophistication & automation |
| **Rigorous Model Evaluation** | "Each model's directional accuracy tracked independently on out-of-sample data. Best-performing model per ticker highlighted" | Data science credibility |

### 4. Private Repo Notice

**File**: `templates/trading_analytics_detail.html` lines 22–30

```html
<div class="flex items-start gap-3 bg-slate-800/40 border border-slate-700/60 rounded-lg px-4 py-3 mb-5">
  <svg class="w-4 h-4 text-slate-500 shrink-0 mt-0.5"><!-- lock icon --></svg>
  <p class="text-xs text-slate-500 leading-relaxed">
    Core logic lives in a <strong class="text-slate-400">private repository</strong>.
    The system runs automated scans and emails me actionable signals
    <strong class="text-slate-400">3× daily</strong> — I use those alerts to make
    real stock purchases.
  </p>
</div>
```

**Purpose**: Transparency + live-trading credibility

### 5. Watchlist Table

**File**: `templates/trading_analytics_detail.html` lines 136–293

**Data source**: `_ta_watchlist()` function
- Queries `watchlist_tickers` (fixed list of tickers to monitor)
- For each ticker, fetches latest row from `scanned_tickers`
- Extracts: buy_score, signal, reasoning, win_rate, total_trades, total_pnl_pct
- Sorts by buy_score descending, takes top 2

**Columns displayed**:
| Column | Source | Example |
|--------|--------|---------|
| **Ticker** | `scanned_tickers.ticker` | AAPL |
| **Price** | `scanned_tickers.last_price` | $150.25 |
| **Score** | `scanned_tickers.buy_score` | 73 (color-coded: red <50, amber 50–69, green ≥70) |
| **Signal & Insights** | `scanned_tickers.signal`, `reasoning` | "Strong Buy" + "RSI oversold, breakout forming..." |
| **Backtest Performance** | `win_rate`, `total_trades`, `total_pnl_pct` | "67.2% Win Rate / 24 Trades", "+145.3% SIGNAL GROWTH" |

**Interactivity**:
- Click row → Accordion expands
- First expansion: lazy-loads `/projects/trading-analytics/plot/{ticker}` via fetch
- Caches result in `data-loaded="true"` to avoid re-fetching

### 6. Technical Chart Accordion (Lazy-Loaded)

**File**: `templates/trading_plot_container.html`

**Triggered when**: User clicks a row in the watchlist table

**What loads**:
1. Plotly candlestick chart (OHLCV bars)
2. Moving averages (20, 50, 200-day)
3. Technical indicators:
   - **RSI** (14-period EMA)
   - **MACD** + Signal Line
   - **Volume bars**
4. **Backtest signals** (colored markers on chart)
5. **ML predictions** (shaded bands showing confidence intervals)
6. **Backtest KPI table** (win rate, total trades, P/L %, multiplier)

**Data source**: `ta_plot_data()` endpoint
- Queries `stock_data` (daily OHLCV)
- Computes technical indicators in-memory (pandas)
- Queries `backtest_signals`, `ml_predictions`, `ml_model_metrics`
- Returns JSON; Plotly renders in browser

**Performance**: ~300ms first load (fetch + render)

## Font Size Changes (Latest Update)

**Applied on 2026-04-13** to improve readability in stat tiles:

| Element | Before | After | Tailwind Class |
|---------|--------|-------|-----------------|
| Big number (66%, 3, 3×, 30d) | `text-4xl` | `text-4xl` | (unchanged) |
| Tile label | `text-xs` | `text-sm` | 12px → 14px |
| Low/High row | `text-xs` | `text-sm` | 12px → 14px |
| "across N tickers" | `text-[11px]` | `text-xs` | 11px → 12px |
| Model list (CatBoost · LightGBM · Theta) | `text-[11px]` | `text-xs` | 11px → 12px |

All changes in `templates/trading_analytics_detail.html` lines 73, 75–76, 79, 84, 90–91, 95, 99.

## Strategy Rules Section

**File**: `templates/trading_analytics_detail.html` lines 39–62

Lists entry/exit conditions WITHOUT specific thresholds:
- ✓ Market filter: SPY > 100-day MA
- ✓ Entry: RSI oversold + MACD bullish + Volume spike + Positive sentiment
- ⬡ Trailing stop: ATR-based, triggered when price retreats from peak
- ✕ Hard stop: fixed drawdown limit from entry
- ↑ Take profit: fixed gain target from entry

**Purpose**: Show sophistication without revealing exact parameters (ATR multiplier, stop %, take-profit %)

## Integration with trading-analytics Cron

**How the stat updates work** (end-to-end):

1. **trading-analytics** (`train_model.py`)
   - Celery Beat triggers `train_model()` 3× daily
   - Trains CatBoost, LightGBM, DynamicOptimizedTheta models
   - Calculates per-ticker hit rates via cross-validation
   - Saves to `ml_model_metrics` table
   - **Computes aggregate summary**: mean, median, min, max of best-model-per-ticker hit rates
   - **Inserts new row** into `model_performance_summary`

2. **PersonalWebsite** (next user visit)
   - `_ta_perf_summary()` queries latest `model_performance_summary` row
   - Template displays the summary with min/max range

3. **Database schema** (`D:\PythonRepos\trading-analytics\src\models.py`)
   ```python
   class ModelPerformanceSummary(Base):
       __tablename__ = "model_performance_summary"
       id = Column(Integer, primary_key=True)
       mean_hit_rate = Column(Float)
       median_hit_rate = Column(Float)
       min_hit_rate = Column(Float)
       max_hit_rate = Column(Float)
       ticker_count = Column(Integer)
       updated_at = Column(DateTime, default=datetime.utcnow)
   ```

## Testing the Feature Locally

1. **Start server**:
   ```bash
   cd d:/PythonRepos/PersonalWebsite
   uvicorn app.main:app --reload --port 8080
   ```

2. **Visit**:
   ```
   http://localhost:8080/projects/trading-analytics
   ```

3. **Test user interactions**:
   - Verify stat bar displays (accuracy %, min/max, ticker count)
   - Click a ticker row → accordion expands
   - Wait for chart to load → verify Plotly renders
   - Check backtest KPI table in accordion

4. **Verify dynamic data**:
   - Query the DB directly: `SELECT * FROM model_performance_summary ORDER BY updated_at DESC LIMIT 1;`
   - Compare displayed accuracy with DB value
   - Should match (within rounding)

## Known Issues & TODOs
- **Accuracy tile shows dash** if `model_performance_summary` is empty or has no data
- **Lazy-load performance** could be improved with caching (Redis, memcached)
- **Mobile responsiveness** of chart accordion could be better (long table may require horizontal scroll on phone)
- **No error handling** for missing ticker data (assumes trading-analytics DB is always populated)
