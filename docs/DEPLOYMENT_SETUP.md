# Shared Backend Setup — Supabase (Postgres) + Render (hosting, free tier + keep-alive)

This moves the backend from "local-only, SQLite" to a real, shared,
always-reachable instance — for $0/month. The code side is done and
verified; what's left needs your browser (account creation, GitHub push)
since that can't be done from this environment.

---

## 1. Supabase — hosted PostgreSQL

Already covered — see the connection string you already sent. That part's done.

## 2. Push the project to GitHub

Render deploys from a GitHub repo, not a local folder — this is a one-time step.

1. Create a new repository on [github.com](https://github.com) (e.g. `ehs-connect`), empty, no README.
2. From the folder containing the whole `EHS-Connect/` project:
   ```
   cd EHS-Connect
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/ehs-connect.git
   git push -u origin main
   ```

## 3. Render — hosting the FastAPI backend

1. Go to [render.com](https://render.com) → sign up (GitHub sign-in is easiest, since you'll connect a repo anyway).
2. **New → Web Service** → connect the `ehs-connect` repo you just pushed.
3. Render should detect `backend/render.yaml` automatically and pre-fill
   the build/start commands and root directory. If it doesn't ask you
   manually, set:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free
4. Under **Environment**, add:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | your Supabase connection string (with the real password) |
   | `JWT_SECRET_KEY` | run `python -c "import secrets; print(secrets.token_hex(32))"` locally and paste the output |
   | `ENVIRONMENT` | `production` |
   | `CORS_ALLOW_ORIGINS` | `http://localhost:5173,http://localhost:19006` for now |

5. Click **Create Web Service**. First deploy takes a few minutes. You'll
   get a URL like `https://ehs-connect-backend.onrender.com`.
6. Confirm it's alive: visit `https://ehs-connect-backend.onrender.com/health`
   in a browser — should return `{"status":"ok"}`.

## 4. Keep it from sleeping (the part you asked for)

Render's free web services spin down after **15 minutes** with no
incoming requests, and the next request after that takes 30-60 seconds to
wake back up. Pinging the app on an interval **shorter than 15 minutes**
keeps it warm indefinitely, at zero cost. Two free ways to do this —
pick one:

### Option A — cron-job.org (simplest, no GitHub needed)
1. Go to [cron-job.org](https://cron-job.org) → free sign up.
2. **Create cronjob** → URL: `https://ehs-connect-backend.onrender.com/health`
3. Schedule: every 10 minutes.
4. Save. Done — it'll silently ping that URL forever, keeping the service warm.

### Option B — GitHub Actions (since the repo already exists from step 2)
Add this file to the repo and push it:

```yaml
# .github/workflows/keep-alive.yml
name: Keep Render backend awake
on:
  schedule:
    - cron: "*/10 * * * *"
  workflow_dispatch: {}
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - run: curl -sf https://ehs-connect-backend.onrender.com/health
```
GitHub's scheduled triggers aren't guaranteed to the exact minute (can
drift a few minutes under load), but that drift is comfortably inside the
15-minute sleep window, so it works fine in practice. `workflow_dispatch`
just lets you trigger it manually from GitHub's UI to test it immediately.

**A caveat worth knowing:** a few dedicated uptime-monitoring services
(UptimeRobot, for one) restrict their free tier to personal/non-commercial
use in their terms of service. `cron-job.org` is a general-purpose
scheduler, not a monitoring product, so it doesn't carry that restriction
— which is part of why it's the recommended option here over something
like UptimeRobot.

## 5. Point the frontends at it

- **Mobile app** (`mobile-app/.env`): `EXPO_PUBLIC_API_BASE_URL=https://ehs-connect-backend.onrender.com/api/v1`
- **Admin Portal** (once Module 5 exists): same idea with Vite's env convention.

Send me the real `.onrender.com` URL once step 3 is live and I'll update
`mobile-app/.env` and hand the file back to you.

## What's already ready in the code (no further changes needed)

- `backend/render.yaml` — Render reads this automatically to configure the service
- `app/core/config.py` auto-normalizes Supabase's connection string to the
  `psycopg` v3 driver scheme this project uses — paste it in unedited
- `cors_allow_origins` accepts a plain comma-separated string, easy to
  paste into Render's environment variable UI
- `/health` endpoint already exists (`app/main.py`) — this is what both
  Render's own health checks and the keep-alive ping use

## What I can't verify from here

This sandbox has no network path to Supabase, GitHub, or Render — only a
small package-registry allowlist. So the code is ready and was tested
against the same SQLite migration path used since Module 2, but the real
Supabase connection and the actual Render deploy haven't been exercised by
a live run. If `alembic upgrade head` fails against the real Supabase URL,
or the Render build fails, paste me the exact error and I'll fix it.
