# Personal Data Science Portfolio Website

## Context
A data scientist with zero web experience wants a personal website that:
1. Showcases ML projects with live, interactive predictions
2. Allows any visitor to submit inputs and receive model predictions in-browser
3. Serves as a professional portfolio with a custom domain

Starting from a completely empty directory (`d:\PythonRepos\PersonalWebsite`).

---

## Tech Stack Decision

| Layer | Choice | Why |
|-------|--------|-----|
| **Backend** | Python + FastAPI | You already know Python. FastAPI makes it trivial to wrap any ML model as a REST endpoint. |
| **Frontend** | HTML + Tailwind CSS + Alpine.js | No build step needed, no npm hell. Tailwind gives beautiful styling with utility classes. Alpine.js gives interactivity (form submission, live results) with plain JS syntax. |
| **ML Serving** | Scikit-learn / joblib / ONNX | Models saved as `.joblib` files on the server's persistent SSD. Each project gets its own prediction endpoint. |
| **Hosting** | Hetzner Cloud CX22 VPS | Permanent, always-on VM (never sleeps). Persistent 40GB SSD (models stay there forever). 2GB RAM, 2 vCPU. No cold starts, no ephemeral filesystem. $4.15/mo ≈ $50/year. |
| **Reverse Proxy** | Caddy (on the VPS) | Automatic free SSL from Let's Encrypt. Simple config compared to Nginx. Runs on the VPS in front of FastAPI. |
| **Domain** | Cloudflare Registrar | ~$10/year for `.dev` or `.me` domain. Cheapest registrar (at-cost pricing). |

---

## Cost Breakdown (Total: ~$55–65 per year)

| Item | Cost | Duration | Notes |
|------|------|----------|-------|
| **Hetzner Cloud CX22 VPS** | €3.29/mo | Monthly | ~$50/year (1 server, persistent SSD included) |
| **Domain (.dev or .me)** | ~$10–15 | Yearly | Cloudflare Registrar (at-cost), auto-renews |
| **SSL Certificate** | $0 | Forever | Let's Encrypt (free via Caddy on VPS) |
| **Email/DNS** | $0 | Forever | Cloudflare free tier (if using their registrar) |
| **Total** | **~$55–65/year** | | One-time setup, recurring hosting cost only |

**What you get:**
- 24/7 uptime, no cold starts, no spin-downs
- Persistent 40GB SSD on the server (your models live here forever)
- Full control; can install anything, no vendor lock-in
- HTTPS automatically handled by Caddy

---

## Where ML Models Live on Disk

**On the Hetzner VPS, the directory structure is:**

```
/home/username/personalwebsite/
├── app/
│   ├── main.py              # FastAPI app
│   ├── routers/
│   │   └── predict.py
│   ├── schemas.py
│   └── models/              # <-- MODEL FILES LIVE HERE
│       ├── house_price.joblib     (~10–50 MB)
│       ├── sentiment_analysis.joblib
│       └── iris_classifier.joblib
├── static/
├── templates/
├── requirements.txt
└── ...
```

**How models are loaded in `routers/predict.py`:**
```python
import joblib

# Load model from absolute path on VPS disk
MODEL_PATH = "/home/username/personalwebsite/app/models/house_price.joblib"
model = joblib.load(MODEL_PATH)

@router.post("/predict/house-price")
def predict(data: HousePriceInput):
    result = model.predict([[data.sqft, ...]])
    return {"price": result[0]}
```

**Key points:**
- The VPS has a persistent SSD (`/home/username/` is permanent storage)
- Model files (`.joblib`) live on this SSD alongside your code
- When you redeploy or restart the app, the files stay there — no loss
- Model files survive even if you stop/start the VPS
- Upload new models via SCP: `scp my_new_model.joblib user@vps_ip:/home/username/personalwebsite/app/models/`

**Storage considerations:**
- Sklearn models: 1–50 MB (very small)
- Neural networks: 50 MB – 2 GB
- 40GB SSD can comfortably hold 20+ trained models + code
- If models exceed disk space, upgrade to CX31 (~€6.49/mo, 80GB disk)

---

## Project Structure

```
PersonalWebsite/
├── app/
│   ├── main.py              # FastAPI app, routes, static file serving
│   ├── models/              # Saved ML model files (.joblib, .pkl, .onnx)
│   │   └── README.md
│   ├── routers/
│   │   └── predict.py       # Prediction API endpoints (one per project)
│   └── schemas.py           # Pydantic input/output schemas for each model
├── static/
│   ├── css/
│   │   └── style.css        # Custom overrides (Tailwind loaded via CDN)
│   └── js/
│       └── predict.js       # Fetch calls to prediction API
├── templates/
│   ├── base.html            # Shared layout (nav, footer)
│   ├── index.html           # Home / About page
│   ├── projects.html        # Projects gallery page
│   └── project_detail.html  # Individual project + prediction widget
├── Caddyfile                # Reverse proxy + HTTPS config (for VPS)
├── requirements.txt
├── plan.md                  # This file
└── .gitignore
```

---

## Phase-by-Phase Plan

### Phase 1 — Scaffold & Hello World
1. Create the directory structure above
2. `requirements.txt`: `fastapi`, `uvicorn[standard]`, `jinja2`, `python-multipart`, `scikit-learn`, `joblib`
3. `main.py`: minimal FastAPI app that serves the `index.html` homepage
4. `base.html`: nav bar (Home, Projects), footer with your name/links
5. `index.html`: hero section (name, tagline, photo placeholder), About blurb, links to GitHub/LinkedIn
6. Run locally: `uvicorn app.main:app --reload`
7. Verify homepage renders in browser

### Phase 2 — Projects Gallery
1. Define a `projects` list in `main.py` (title, description, tags, slug)
2. `projects.html`: card grid — one card per project with name, description, tech tags
3. Each card links to `/projects/{slug}`
4. `project_detail.html`: description, methodology, results section, **prediction widget**

### Phase 3 — Live Prediction Widgets
For each ML model you want to showcase:
1. Train/serialize the model with `joblib.dump(model, "app/models/my_model.joblib")`
2. Add a Pydantic schema in `schemas.py` (input fields + output)
3. Add a POST endpoint in `routers/predict.py`:
   ```python
   @router.post("/predict/house-price")
   def predict_house_price(data: HousePriceInput) -> HousePriceOutput:
       model = joblib.load("app/models/house_price.joblib")
       prediction = model.predict([[data.sqft, data.bedrooms, ...]])
       return {"predicted_price": prediction[0]}
   ```
4. On the project detail page: HTML form → Alpine.js submits via `fetch()` → displays result inline (no page reload)

### Phase 4 — Polish & Deploy
1. **Responsive design**: Tailwind's mobile-first classes
2. **Dark mode toggle**: Alpine.js + Tailwind `dark:` variants
3. **GitHub**: push to a new public repo
4. **Hetzner Cloud VPS Setup** (~1–2 hours, one-time):
   - Go to `hetzner.com` → create account, deploy CX22 server (Ubuntu 22.04)
   - SSH into the VPS: `ssh root@your_vps_ip`
   - Install dependencies: `apt update && apt install python3.11 python3.11-venv`
   - Clone your GitHub repo: `git clone https://github.com/yourname/personalwebsite /home/personalwebsite`
   - Install Python deps: `cd /home/personalwebsite && python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
   - Create a systemd service to auto-start FastAPI on boot
   - Install Caddy for automatic HTTPS
   - Point domain DNS to your VPS IP
5. **Domain**:
   - Buy domain at `cloudflare.com/products/registrar` (~$10/yr for `.dev`)
   - In Cloudflare DNS: create an A record → `yourdomain.dev` → `your_vps_ip`
   - HTTPS is automatic via Caddy (auto-renews Let's Encrypt certificate)

---

## Implementation Notes for Phase 4

**Systemd Service** (keeps FastAPI running permanently, auto-restarts on crash):
```ini
[Unit]
Description=Personal Website FastAPI
After=network.target

[Service]
Type=notify
User=personalwebsite
WorkingDirectory=/home/personalwebsite
ExecStart=/home/personalwebsite/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Caddyfile** (reverse proxy + auto HTTPS):
```
yourdomain.dev {
    reverse_proxy 127.0.0.1:8000
}
```

---

## Open Questions for Later
- Which specific ML projects/models do you want to feature first?
- Do you have existing trained models, or will we build sample ones?
- Do you have a headshot photo for the About page?
- What name/domain are you considering?
- Comfortable with basic Linux (SSH, apt, systemd) or prefer step-by-step guidance?
