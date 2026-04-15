# Deployment Guide — khaaskuro.com

Deploying PersonalWebsite + trading-analytics to a single Hetzner CX22 VPS.

## Architecture

```
khaaskuro.com          → Caddy :443 → PersonalWebsite (systemd, :8000)
trading.khaaskuro.com  → Caddy :443 → trading-analytics web (Docker, :8001)
                                              ↕
                            /opt/trading-data/trading_app.db  (shared host file)
                                              ↑ writes 3×/day
                            trading-analytics worker + beat + redis (Docker)
```

| Domain | App | How it runs |
|--------|-----|-------------|
| `khaaskuro.com` | PersonalWebsite | systemd → uvicorn, port 8000 |
| `trading.khaaskuro.com` | trading-analytics web | Docker → gunicorn, port 8001 |
| — | trading-analytics worker + beat + redis | Docker Compose |

**Shared DB:** `/opt/trading-data/trading_app.db` — worker writes, both web apps read.

---

## Windows Upload Notes

`rsync` is not available on Windows. Use these alternatives:

**Upload a directory (robocopy + scp):**
```powershell
# 1. Create filtered local copy
robocopy D:\PythonRepos\trading-analytics D:\temp\trading-analytics /E /XD .git __pycache__ data mlruns experiments /XF *.pyc .env

# 2. Upload to home dir (scp can't create dirs in /opt/ directly)
scp -r D:\temp\trading-analytics deploy@VPS_IP:~/

# 3. On server: move to /opt/
sudo mkdir -p /opt/trading-analytics
sudo chown deploy:deploy /opt/trading-analytics
cp -r ~/trading-analytics/* /opt/trading-analytics/
rm -rf ~/trading-analytics

# 4. Clean up local temp
Remove-Item -Recurse -Force D:\temp\trading-analytics
```

**Upload a single file:**
```powershell
scp D:\path\to\file deploy@VPS_IP:/opt/destination/
```

---

## Phase 1: Local Code Changes (already done — for reference)

These changes are already in the repos:

- `PersonalWebsite/requirements.txt` — added `pandas>=2.0.0` and `python-dotenv>=1.0.0`
- `PersonalWebsite/app/main.py` — DB path reads from `TA_DB_PATH` env var; WAL + busy_timeout pragmas in `_ta_conn()`
- `PersonalWebsite/.env` (local only) — `TA_DB_PATH=D:/PythonRepos/trading-analytics/data/trading_app.db`
- `trading-analytics/docker-compose.vps.yml` — VPS compose file (web + worker + beat + redis, bind mount `/opt/trading-data/`)

---

## Phase 2: Provision Hetzner VPS

### 2A. Create the server
1. Go to [console.hetzner.cloud](https://console.hetzner.cloud)
2. New Project → "khaaskuro"
3. Add Server: Ubuntu 22.04, CX22 (2 vCPU / 4 GB RAM / 40 GB SSD)
4. Note the assigned **IPv4 address**

> If no SSH key is uploaded, Hetzner emails you a root password. Use it to log in, then add your SSH key.

### 2B. Initial setup
```bash
ssh root@VPS_IP

# Create deploy user
adduser deploy
usermod -aG sudo deploy
mkdir -p /home/deploy/.ssh
cp /root/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh && chmod 600 /home/deploy/.ssh/authorized_keys

# Harden SSH
sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Firewall
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw --force enable

exit  # reconnect as deploy from now on
```

> **Important:** After `usermod -aG sudo deploy`, log out and back in as deploy before testing sudo. If deploy can't sudo, use `su -` (root password) from the deploy session to fix it — root SSH login will be disabled after the hardening step above.

### 2C. Install software
```bash
ssh deploy@VPS_IP

# System update
sudo apt-get update && sudo apt-get upgrade -y

# Python 3.11
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev

# Docker
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker deploy
sudo systemctl enable docker

# Caddy
sudo apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt-get update && sudo apt-get install -y caddy

# Git + sqlite3
sudo apt-get install -y git sqlite3

# Log out and back in to activate docker group membership
exit && ssh deploy@VPS_IP
```

Verify:
```bash
python3.11 --version   # 3.11.x
docker --version       # 29.x
caddy version          # 2.x
git --version
```

---

## Phase 3: Deploy trading-analytics

### 3A. Create directories
```bash
# On server
sudo mkdir -p /opt/trading-data /opt/trading-analytics
sudo chown deploy:deploy /opt/trading-data /opt/trading-analytics
```

### 3B. Upload repository
```powershell
# On local Windows (PowerShell)
robocopy D:\PythonRepos\trading-analytics D:\temp\trading-analytics /E /XD .git __pycache__ data mlruns experiments /XF *.pyc .env
scp -r D:\temp\trading-analytics deploy@VPS_IP:~/
Remove-Item -Recurse -Force D:\temp\trading-analytics
```
```bash
# On server
cp -r ~/trading-analytics/* /opt/trading-analytics/
rm -rf ~/trading-analytics
```

### 3C. Upload the database
```powershell
# Copy only the main .db file — NOT .db-shm or .db-wal
scp "D:\PythonRepos\trading-analytics\data\trading_app.db" deploy@VPS_IP:/opt/trading-data/
```

Verify integrity on server:
```bash
sqlite3 /opt/trading-data/trading_app.db "PRAGMA integrity_check;"  # expected: ok
```

### 3D. Add swap (prevents OOM during Docker build)
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h  # confirm Swap: 2.0G
```

### 3E. Create production .env
```bash
# Generate secrets
python3.11 -c "import secrets; print(secrets.token_hex(32))"      # → SECRET_KEY
python3.11 -c "import secrets; print(secrets.token_urlsafe(24))"  # → REDIS_PASSWORD

nano /opt/trading-analytics/.env
```

Paste and fill in:
```
APP_ENV=production
GCP_PROJECT_ID=
DATABASE_URL=sqlite:////app/data/trading_app.db
REDIS_URL=redis://:YOUR_REDIS_PASSWORD@redis:6379/0
REDIS_PASSWORD=YOUR_REDIS_PASSWORD
SECRET_KEY=YOUR_64_CHAR_HEX
CRON_SECRET=YOUR_CRON_SECRET
ENABLE_SCHEDULER=False
EMAIL_SENDER=your@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
ADMIN_EMAILS=your@gmail.com
ADMIN_EMAIL=your@gmail.com
USER_EMAIL=your@gmail.com
TEST_USER_EMAIL=your@gmail.com
TZ=America/New_York
FLOWER_URL=https://trading.khaaskuro.com/flower
```

```bash
chmod 600 /opt/trading-analytics/.env
```

> **Notes:**
> - `GCP_PROJECT_ID=` must be empty (not omitted) — prevents startup delay from failed GCP metadata calls
> - `ENABLE_SCHEDULER=False` — Celery Beat handles scheduling; this disables the secondary APScheduler
> - Use a Gmail App Password for `EMAIL_PASSWORD` (not your regular Gmail password)
> - `FLOWER_URL` controls the "Task Monitor" link in the admin dashboard — must point to the public proxy path, not localhost

### 3F. Build and start
```bash
cd /opt/trading-analytics
docker compose -f docker-compose.vps.yml build   # 5–15 min first time
docker compose -f docker-compose.vps.yml up -d
docker compose -f docker-compose.vps.yml ps      # all 5 should show Status: Up
```

Expected healthy state:
```
trading-analytics-redis-1    Up (healthy)
trading-analytics-worker-1   Up (healthy)
trading-analytics-beat-1     Up (healthy)
trading-analytics-web-1      Up (healthy)   127.0.0.1:8001->8000/tcp
trading-analytics-flower-1   Up (healthy)
```

Check logs:
```bash
docker compose -f docker-compose.vps.yml logs --tail=50 redis    # "Ready to accept connections"
docker compose -f docker-compose.vps.yml logs --tail=50 worker   # "celery@... ready"
docker compose -f docker-compose.vps.yml logs --tail=50 beat     # "beat: Starting..."
docker compose -f docker-compose.vps.yml logs --tail=50 web      # "Listening at: http://0.0.0.0:8000"
docker compose -f docker-compose.vps.yml logs --tail=50 flower   # "celery flower..."
```

---

## Phase 4: Deploy PersonalWebsite

### 4A. Create directory and upload
```bash
# On server
sudo mkdir -p /opt/personal-website
sudo chown deploy:deploy /opt/personal-website
```
```powershell
# On local Windows (PowerShell)
robocopy D:\PythonRepos\PersonalWebsite D:\temp\PersonalWebsite /E /XD .git __pycache__ /XF *.pyc .env
scp -r D:\temp\PersonalWebsite deploy@VPS_IP:~/
Remove-Item -Recurse -Force D:\temp\PersonalWebsite
```
```bash
# On server
cp -r ~/PersonalWebsite/* /opt/personal-website/
rm -rf ~/PersonalWebsite
```

### 4B. Install dependencies
```bash
cd /opt/personal-website
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -c "import pandas, fastapi, uvicorn, dotenv; print('OK')"
deactivate
```

### 4C. Create .env
```bash
echo "TA_DB_PATH=/opt/trading-data/trading_app.db" > /opt/personal-website/.env
chmod 600 /opt/personal-website/.env
```

### 4D. Create systemd service
```bash
sudo nano /etc/systemd/system/personal-website.service
```

```ini
[Unit]
Description=PersonalWebsite FastAPI (khaaskuro.com)
After=network.target

[Service]
User=deploy
WorkingDirectory=/opt/personal-website
EnvironmentFile=/opt/personal-website/.env
ExecStart=/opt/personal-website/venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 --port 8000 --workers 2 --log-level info
Restart=on-failure
RestartSec=10
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now personal-website
sudo systemctl status personal-website
```

Verify:
```bash
curl -s http://localhost:8000/ | head -5   # should return HTML
```

---

## Phase 5: Caddy + DNS

### 5A. Configure Caddy
```bash
sudo nano /etc/caddy/Caddyfile
```

```
khaaskuro.com {
    reverse_proxy localhost:8000
}

www.khaaskuro.com {
    redir https://khaaskuro.com{uri} permanent
}

trading.khaaskuro.com {
    reverse_proxy localhost:8001
}
```

```bash
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl restart caddy
```

### 5B. DNS records
At your registrar (Google Domains), add:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `@` | `VPS_IP` | 300 |
| A | `www` | `VPS_IP` | 300 |
| A | `trading` | `VPS_IP` | 300 |

Wait for propagation, then verify:
```bash
dig khaaskuro.com A +short          # → VPS_IP
dig trading.khaaskuro.com A +short  # → VPS_IP
```

> Do not proceed until DNS resolves — Let's Encrypt requires the domain to point at the server.

---

## Phase 6: Verification

```bash
# 1. PersonalWebsite direct
curl -s http://localhost:8000/ | head -5

# 2. trading-analytics web direct
curl -s http://localhost:8001/health

# 3. Docker services
docker compose -f /opt/trading-analytics/docker-compose.vps.yml ps

# 4. Redis
docker compose -f /opt/trading-analytics/docker-compose.vps.yml exec redis \
  redis-cli -a $REDIS_PASSWORD ping   # → PONG

# 5. Celery worker
docker compose -f /opt/trading-analytics/docker-compose.vps.yml exec worker \
  celery -A src.celery_app inspect ping   # → pong

# 6. Shared DB accessible
ls -lh /opt/trading-data/trading_app.db
```

In browser:
- `https://khaaskuro.com` — homepage with HTTPS padlock
- `https://khaaskuro.com/projects/trading-analytics` — charts and watchlist visible
- `https://www.khaaskuro.com` — redirects to apex domain
- `http://khaaskuro.com` — redirects to HTTPS
- `https://trading.khaaskuro.com` — trading dashboard login page
- Login with admin account (`ADMIN_EMAIL`) — dashboard loads with portfolio/watchlist data

---

## User Account Management

User accounts are stored in the shared DB. If passwords need to be reset after a fresh DB copy:

```bash
docker compose -f /opt/trading-analytics/docker-compose.vps.yml exec web python3 -c "
from passlib.context import CryptContext
import sqlite3
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
new_hash = pwd_context.hash('NewPassword123')
conn = sqlite3.connect('/app/data/trading_app.db')
conn.execute(\"UPDATE users SET hashed_password=? WHERE email='your@email.com'\", (new_hash,))
conn.commit()
conn.close()
print('Done')
"
```

Admin access is controlled by `ADMIN_EMAIL` / `ADMIN_EMAILS` in `/opt/trading-analytics/.env`, not the DB.

---

## Day-to-Day Operations

### Update PersonalWebsite
```bash
# Upload changed files via scp from local, then:
sudo systemctl restart personal-website
sudo journalctl -u personal-website -f
```

### Update trading-analytics
```bash
cd /opt/trading-analytics
# Upload files via scp/robocopy from local, then:
docker compose -f docker-compose.vps.yml build
docker compose -f docker-compose.vps.yml up -d
```

### View logs
```bash
sudo journalctl -u personal-website -f                                            # PersonalWebsite
docker compose -f /opt/trading-analytics/docker-compose.vps.yml logs -f web      # trading-analytics web
docker compose -f /opt/trading-analytics/docker-compose.vps.yml logs -f worker   # Celery worker
sudo journalctl -u caddy -f                                                       # Caddy
```

### Database backup
```bash
sqlite3 /opt/trading-data/trading_app.db \
  ".backup /opt/trading-data/backup_$(date +%Y%m%d).db"
```

Add to weekly cron (`crontab -e`):
```
0 2 * * 0 sqlite3 /opt/trading-data/trading_app.db ".backup /opt/trading-data/backups/trading_app_$(date +\%Y\%m\%d).db"
```
