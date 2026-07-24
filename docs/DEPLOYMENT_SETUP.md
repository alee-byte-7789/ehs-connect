# Shared Backend + Frontend — One Vercel Project (Supabase for the DB)

This replaces the earlier Render plan. Reasoning: Render started requiring
card verification (a real, standard anti-abuse measure — not unique to us
— but still a blocker without a card), and Vercel's Hobby plan needs no
card at all, with much faster cold starts (~1-2s vs Render's 30-60s).

**Architecture:** one Vercel project serves both halves from the same
domain — the FastAPI backend as Python serverless functions under `/api/*`,
and the Expo web export (our PWA) as static files for everything else.
Same-origin means the frontend can call the API with a relative path, no
CORS juggling needed for that path.

---

## 1. Supabase — hosted PostgreSQL (already done)

Already set up in the earlier session — connection string in hand.
**One change for this setup:** grab the **Session pooler** connection
string this time (not "Direct connection"), from the same **Connect**
button → **ORM** or **Direct** tab → look for "Session pooler" instead.
Serverless functions open/close connections far more often than a
persistent server would, and the session pooler is built for exactly that
pattern — the direct connection can run out of available slots under
Vercel's function concurrency.

## 2. Push to GitHub (already done, `alee-byte-7789/ehs-connect`)

No change — Vercel deploys from the same repo already pushed.

## 3. Deploy to Vercel

1. Go to [vercel.com](https://vercel.com) → sign up (GitHub sign-in is
   easiest) → **no card required** for the Hobby plan.
2. **Add New → Project** → import the `ehs-connect` repo.
3. On the configure screen:
   - **Root Directory:** leave as the repo root (blank) — `vercel.json`
     at the top level defines both builds, so don't set this to `backend`
     or `mobile-app` like we would have for Render/Railway.
   - **Framework Preset:** Vercel may try to guess one — override to
     **Other**, since `vercel.json`'s `builds` array controls everything
     explicitly.
4. **Environment Variables** — add:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | the Supabase **session pooler** connection string (with the real password) |
   | `JWT_SECRET_KEY` | run `python -c "import secrets; print(secrets.token_hex(32))"` locally, paste the output |
   | `ENVIRONMENT` | `production` |
   | `CORS_ALLOW_ORIGINS` | `http://localhost:5173,http://localhost:19006` (only matters for local dev clients hitting the deployed API directly; the deployed frontend doesn't need CORS since it's same-origin) |
   | `EXPO_PUBLIC_API_BASE_URL` | `/api/v1` — a **relative** path, since frontend and backend share a domain here |

5. Click **Deploy**. First deploy takes a few minutes (it runs two builds:
   the Python function and the Expo web export).
6. Once live, Vercel gives you a URL like `https://ehs-connect.vercel.app`.
   Check both halves:
   - `https://ehs-connect.vercel.app/health` → should return `{"status":"ok"}`
     (note: `/health` is NOT under `/api/v1` — see the route prefix note below)
   - `https://ehs-connect.vercel.app/login` → should show the actual login
     screen (the Expo web export), not a 404

**Route prefix note:** the FastAPI app's own routes are `/health` (no
prefix) and everything else under `/api/v1/...` (`/api/v1/auth/login`,
etc. — see `app/main.py`, a pre-existing detail from Module 3). Since
`/health` doesn't start with `/api/`, `vercel.json` has an explicit rule
routing it to the backend function too, ahead of the catch-all that would
otherwise send it to the static frontend and 404. Verified directly: both
`/health` and `/api/v1/auth/login` were tested through the actual
`api/index.py` entrypoint and resolved correctly.

## 4. Running migrations against the real Supabase database

Unlike Render/Railway, Vercel's serverless functions don't have a
persistent "start command" that can run `alembic upgrade head` before
serving traffic — each function invocation is independent. Run migrations
from your own machine instead, pointed at Supabase, whenever the schema
changes:

```
cd backend
# Temporarily set DATABASE_URL to the real Supabase connection string
# (session pooler string works fine for this too)
$env:DATABASE_URL="postgresql://postgres:...@...supabase.co:5432/postgres"   # PowerShell
alembic upgrade head
```

This is a real workflow difference from the Render plan worth knowing:
migrations are a manual step you run locally, not an automatic part of
every deploy.

## What's already ready in the code (no further changes needed)

- `vercel.json` (repo root) — defines the two builds (`api/index.py` for
  the backend, `mobile-app/package.json` for the frontend) and routes
  `/api/*` to the backend, everything else to the static export
- `api/index.py` — thin adapter importing the real FastAPI app from
  `backend/app/main.py` unchanged; Vercel's Python runtime wraps it as a
  serverless function automatically
- `requirements.txt` (repo root) — duplicate of `backend/requirements.txt`,
  since Vercel's Python builder looks for it there, not inside `backend/`.
  **Keep both files in sync when adding a dependency.**
- `mobile-app/package.json`'s `vercel-build` script — runs
  `expo export --platform web`, which `@vercel/static-build` picks up automatically
- `app/core/database.py` — detects Vercel's `VERCEL` env var and switches
  to `NullPool` (no local connection pooling), since Supabase's session
  pooler already handles pooling externally; this has zero effect on local
  dev or any non-Vercel deployment

## Verified, not just written

- `api/index.py` was tested exactly as Vercel's runtime would use it:
  imported via the same `sys.path` adjustment, wrapped in a real
  `TestClient`, and hit with actual HTTP requests — `GET /health` returned
  `200`, and `POST /api/v1/auth/register` correctly wrote a new resident to
  a real (SQLite, for this test) database and returned `201` with the
  expected `pending` status.
- The `NullPool` toggle was verified directly: `engine.pool` is `NullPool`
  when `VERCEL=1` is set, and the normal `QueuePool` otherwise — confirming
  local dev and Render/Railway are unaffected.
- `npm run vercel-build` was run for real and produced `mobile-app/dist/`
  with all 5 routes (`/`, `/login`, `/register`, `/pending`, `/home`),
  exactly matching what `@vercel/static-build` expects.

## What I can't verify from here

This sandbox has no network path to Vercel, GitHub, or Supabase — only a
package-registry allowlist. So every piece above was tested individually
and end-to-end as far as this environment allows, but the *actual* Vercel
build (both builders running together, routing between them, the real
Supabase session-pooler connection under real serverless conditions)
hasn't been exercised by a live deploy. This is a legitimately new setup
(unifying a Python API and an Expo static export under one Vercel project
isn't a well-worn path the way Render's single-service model is), so
there's a real chance the first deploy surfaces something — a routing
edge case, a Python build path issue, a cold-start connection hiccup. If
it does, paste me the exact build log or error and I'll fix it directly.
