# PROJECT_ROADMAP.md
## EHS Connect — Resident Complaint & Maintenance Management System

**Status:** Module 4 — Resident Mobile App foundation (Complete, awaiting review)
**Last Updated:** 2026-07-23
**Owner:** Ali (BSCS-25, SEECS NUST)

This file is the single source of truth for the entire project. It is updated after every completed module and must always reflect the current real state of the codebase — not the aspirational state.

---

## 1. Project Vision

EHS Connect digitizes the day-to-day administrative life of a housing society (Employees Housing Society / EHS): resident verification, complaint lodging and resolution, maintenance coordination, emergency contacts, and society-wide notifications.

It is built as two client applications sharing one backend:

- **Resident Mobile App** — the primary interface for residents. Register, get verified, raise complaints, track status, give feedback, view emergency numbers.
- **Admin Portal** — desktop-first web app for Housing Office Admins, IT Admins, Maintenance Staff, and Super Admins to verify residents, triage and assign complaints, and monitor the society.

Design north star: it should feel like **Apple / Linear / Stripe / Notion / Material 3** — calm, premium, minimal, fast. Not a college project. Not a generic Bootstrap admin theme.

---

## 2. Architecture Overview

```
┌─────────────────────────┐        ┌──────────────────────────┐
│   Resident Mobile App   │        │      Admin Portal        │
│  React Native + Expo    │        │   React + Vite + TS      │
│       (TypeScript)      │        │      (Tailwind CSS)      │
└────────────┬─────────────┘        └────────────┬─────────────┘
             │            HTTPS / JSON (Axios)    │
             └──────────────────┬─────────────────┘
                                 │
                        ┌────────▼─────────┐
                        │   FastAPI Backend │
                        │  (Python, JWT,    │
                        │   SQLAlchemy,     │
                        │   Alembic)        │
                        └────────┬──────────┘
                                 │
                ┌────────────────┼─────────────────┐
                │                │                 │
       ┌────────▼──────┐ ┌───────▼───────┐ ┌───────▼────────┐
       │  PostgreSQL    │ │  Firebase FCM │ │  Zoho SMTP     │
       │  (Supabase)    │ │  (Push Notif) │ │  (Email)       │
       └────────────────┘ └───────────────┘ └────────────────┘
```

**Pattern:** Feature-based, layered architecture on the backend (routers → services → repositories → models), and feature-folder architecture on both frontends (each domain — auth, complaints, houses, feedback — owns its own components, hooks, and API calls).

**Auth:** JWT access + refresh tokens, role embedded in token claims, verified against DB role on every protected request (never trust the token alone for privilege-sensitive actions).

---

## 3. Folder Structure (Monorepo)

```
EHS-Connect/
├── PROJECT_ROADMAP.md          ← this file, always current
├── docs/                       ← ER diagrams, API contracts, ADRs
│
├── backend/                    ← FastAPI service
│   ├── app/
│   │   ├── api/                ← routers (v1/auth, v1/complaints, ...)
│   │   ├── core/               ← config, security, JWT, settings
│   │   ├── models/              ← SQLAlchemy models
│   │   ├── schemas/             ← Pydantic request/response schemas
│   │   ├── services/            ← business logic
│   │   ├── repositories/        ← DB access layer
│   │   └── main.py
│   ├── alembic/                 ← migrations
│   └── tests/
│
├── admin-portal/                ← React + Vite + TS (web)
│   ├── src/
│   │   ├── features/             ← auth, registrations, complaints, houses...
│   │   ├── components/           ← shared UI primitives
│   │   ├── lib/                  ← axios client, query client
│   │   └── routes/
│   └── public/
│
└── mobile-app/                   ← React Native + Expo (TS)
    ├── app/                       ← expo-router screens
    ├── components/                ← shared UI primitives
    └── assets/
```

*(As of Module 3: `backend/app/core/`, `backend/app/models/`, `backend/app/schemas/`, `backend/app/services/`, `backend/app/repositories/`, `backend/app/api/`, and `backend/alembic/` are all populated and verified, plus `backend/scripts/`. `admin-portal/` and `mobile-app/` remain empty until Modules 4–5.)*

---

## 4. Tech Stack

| Layer | Choice |
|---|---|
| Resident App | React Native, Expo, TypeScript, Expo Router |
| Resident App styling | NativeWind (Tailwind for React Native) — shared design tokens across every screen and platform |
| Resident App state | Zustand (client/UI state) + React Query/TanStack Query (server state, replaces ad-hoc fetch-in-component patterns) |
| Resident App forms | React Hook Form, Zod |
| Resident App motion | React Native Reanimated, Moti, React Native Gesture Handler |
| Resident App — Android testing | Sideloaded dev/debug `.apk` via `eas build --profile development` — free, no Play Console account needed until launch |
| Resident App — iOS testing | Expo Web (`react-native-web`) run as a PWA in Safari, "Add to Home Screen" — free, no Apple Developer account needed. Native iOS build is deferred but must stay reachable with minimal changes if the Apple Developer Program is joined later (see Section 4.2). |
| Admin Portal | React, Vite, TypeScript, Tailwind CSS |
| Admin Portal motion | Framer Motion |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic, JWT (python-jose / pyjwt) |
| Database (prod) | PostgreSQL via Supabase |
| Database (dev) | SQLite |
| Push Notifications | Firebase Cloud Messaging |
| Email | Zoho Mail SMTP |
| Hosting — Backend | Vercel (Python serverless functions, unified with the frontend — see Section 18) |
| Hosting — Frontend(s) | Vercel (same project as backend — one deployment serves both) |
| Hosting — DB | Supabase PostgreSQL |

---

### 4.1 Cross-Platform Build & Testing Strategy

**Decision (confirmed with Ali):** during development and testing, Android and iOS are validated through two different free channels from the *same* Expo codebase — no second codebase, no paid accounts, no unofficial Android-on-iOS runtimes (not viable: no legitimate Android compatibility layer exists for iOS; the only historical attempts required jailbreaking and are dead/unsupported).

| Platform | Testing phase | Cost | What it actually is |
|---|---|---|---|
| Android | Sideload dev `.apk` (`eas build --profile development`, or `expo run:android` locally) | Free | Real native Android build, installed directly, no Play Console account needed yet |
| iOS | Expo web export (`react-native-web`) run as a PWA, "Add to Home Screen" in Safari | Free | Same RN codebase compiled to web; installable, offline-capable, own icon — but not a native binary |

**Implication for Module 4:** screens and features should prefer cross-platform-safe APIs (Expo's camera/image-picker/notifications modules generally have web fallbacks) and any native-only module needs a guarded fallback or graceful degradation on web, since the iOS testing path runs through the web target.

**Post-testing plan:**
- Android → Google Play Console, one-time $25 fee, publish the same `.aab` EAS already builds.
- iOS → deferred. Apple has no free path to real distribution (TestFlight and the App Store both require the $99/year Apple Developer Program), so a native iOS build is only produced if/when that's worth doing. Until then, iPhone users get the PWA.

---

### 4.2 Frontend Platform & UX Standards

**Confirmed with Ali — one Expo codebase targets Android + Web only** (no separate React web project for the admin-facing resident app; the existing separate `admin-portal/` Vite app is unaffected, since it's for desk-bound Housing Office staff, not residents). The web build is a first-class PWA, not a fallback.

**PWA requirements (all mandatory, not optional polish):**
- Installable via "Add to Home Screen", full-screen standalone display, no visible browser chrome
- Web app manifest, real app icons (not the Expo placeholder logo currently in `assets/`), splash screen
- Service worker with sensible offline caching
- Fast initial load; this is measured, not assumed

**iOS Safari specifics to handle explicitly** (not generic "should work"): safe-area insets, the Dynamic Island / notch, the bottom gesture bar, on-screen keyboard behavior pushing content, orientation changes, touch responsiveness, scroll performance. `react-native-safe-area-context` (already installed) covers most of this, but every screen needs to actually use `useSafeAreaInsets`, not just wrap once at the root.

**Android:** should feel fully native — Material-appropriate motion and gestures, fast cold start, correct behavior across phone and tablet screen sizes.

**Animation standard:** Reanimated + Moti for screen transitions, press feedback, card/modal/bottom-sheet motion, skeleton loaders, pull-to-refresh, success/error states, empty states. Smooth and intentional, not decorative for its own sake — matches the "subtle over flashy" motion principle already in Section 5.4.

**Shared component library (new — supersedes the 3 ad-hoc primitives built in Module 4):** Button, Card, TextField, Modal, BottomSheet, StatusChip (maps to the status colors in 5.1), Timeline, Avatar, LoadingSpinner, SkeletonLoader, Toast, EmptyState, ErrorState. Every screen (including the four already built) should consume these rather than one-off styles.

**State management clarification:** Zustand owns client/UI state (form-in-progress data, theme, navigation flags); React Query owns anything that comes from the API. The Module 4 auth flow currently uses React Context for this — see the gap note in Section 14.

**Non-negotiable engineering check, per feature:** (1) does it work on Android, (2) does it work in the Expo Web PWA, (3) does it work on iOS Safari installed as a PWA, (4) is there a platform-specific issue needing a guarded fallback, (5) can one shared implementation cover all three instead of branching. Default to one implementation; branch only when a real platform gap forces it.

**Future-proofing:** even though no native iOS build ships yet, nothing in the architecture should make a future `expo run:ios` / EAS iOS build difficult — nativewind, reanimated, gesture-handler, and expo-router are all as native-compatible as they are web-compatible by design, so this should hold without special effort as long as new native-only modules are avoided.

---

## 5. Design System

### 5.1 Color Palette

**Light Mode**
| Token | Value | Use |
|---|---|---|
| `primary` | Emerald Green `#10B981` | buttons, active states, links |
| `background` | `#FFFFFF` | app background |
| `surface` | Soft Gray `#F5F6F7` | cards |
| `text-primary` | `#111827` | body text |
| `border` | `#E5E7EB` | dividers, card borders |

**Dark Mode**
| Token | Value | Use |
|---|---|---|
| `primary` | Emerald Green `#10B981` | buttons, active states, links |
| `background` | `#121212` | app background |
| `surface` | `#1E1E1E` | cards |
| `text-primary` | `#FFFFFF` | body text |
| `accent` | Soft Green `#34D399` | highlights, badges |

**Status colors** (used consistently across both apps for complaint states):
| State | Color |
|---|---|
| Pending | Amber `#F59E0B` |
| Accepted | Blue `#3B82F6` |
| Assigned | Indigo `#6366F1` |
| In Progress | Cyan `#06B6D4` |
| Resolved | Emerald `#10B981` |
| Reopened | Red `#EF4444` |
| Closed | Gray `#6B7280` |

### 5.2 Typography
Inter or SF Pro–style system font stack. Clear scale: display / heading / body / caption. No more than 2 weights per screen (regular + semibold).

### 5.3 Components (shared design language across both apps)
- Rounded buttons (12–16px radius), emerald primary, subtle press elevation
- Cards with soft shadow (light) / soft border glow (dark)
- Bottom sheets for mobile actions (raise complaint, filters)
- Skeleton loaders (never blank spinners for list screens)
- Floating action button for "New Complaint"
- Status pills/badges using the state color table above
- Glassmorphism reserved for modals/overlays only, used sparingly

### 5.4 Motion Principles
Subtle over flashy. Page transitions ~200–300ms ease-out. Card elevation on press. Pull-to-refresh with a custom emerald ring. Splash screen with a brief logo scale-fade. Haptic feedback on key mobile actions (submit complaint, approve registration). No animation should block user input.

---

## 6. Database Overview

### 6.1 Core Tables

**houses**
- id (PK), house_code (unique, e.g. `EHS-B-026`), block, address_meta, created_at

**residents**
- id (PK), resident_code (e.g. `EHS-B-026-O`, `EHS-B-026-T1`), house_id (FK), full_name, phone, email (nullable), password_hash, resident_type (`owner` / `tenant`), is_employee (bool), employee_number (nullable), owner_name (nullable, for tenants), owner_cnic (nullable), verification_status (`pending`/`approved`/`rejected`), last_login, created_at

**admins**
- id (PK), full_name, email, password_hash, role (`housing_office`/`it_admin`/`super_admin`), created_at

**staff**
- id (PK), full_name, phone, category (electrician/plumber/mason/security/etc.), is_active

**complaints**
- id (PK), complaint_code, resident_id (FK), house_id (FK), category (`general`/`infrastructure`/`internal`), subcategory, description, photo_urls, status (enum, see workflow), assigned_staff_id (FK, nullable), created_at, updated_at, closed_at, close_count (int, enforces "resident can close once")

**complaint_history**
- id (PK), complaint_id (FK), from_status, to_status, changed_by_type (resident/admin/staff), changed_by_id, note, timestamp

**feedback**
- id (PK), complaint_id (FK), resident_id (FK), rating (1-5), comment, created_at

**application_feedback**
- id (PK), resident_id (FK), type (`feature_request`/`suggestion`/`bug_report`), message, created_at

**emergency_contacts**
- id (PK), label (Fire/Ambulance/Security/etc.), phone_number, is_active

**notifications**
- id (PK), recipient_type (resident/admin), recipient_id, title, body, type, is_read, created_at

### 6.2 Key Relationships
- One `house` → many `residents` (1 owner + N tenants)
- One `resident` → many `complaints`
- One `complaint` → many `complaint_history` rows (full audit trail)
- One `complaint` → one `feedback` (optional, only after resolution)

### 6.3 House / Resident ID Generation Rule
- House code format: `EHS-{BLOCK}-{NUMBER}` e.g. `EHS-B-026`
- Owner resident code: `{house_code}-O`
- Tenant resident code: `{house_code}-T{n}` where n auto-increments per house (T1, T2, T3...)
- IDs are generated server-side only **after** Housing Office approval — never client-side, never before verification.

---

## 7. Complaint Workflow (State Machine)

```
Created → Pending → Accepted → Assigned → In Progress → Resolved
                                                              │
                                              ┌───────────────┴───────────────┐
                                              │                               │
                                     Resident: Satisfied            Resident: Not Satisfied
                                              │                               │
                                           Closed                        Reopened
                                                                              │
                                                                     Admin closes only
                                                                              │
                                                                           Closed
```

**Business rules enforced at the service layer (not just UI):**
1. A resident may close a complaint exactly once (`close_count` guard).
2. Once reopened, only an Admin role can transition it to Closed.
3. Every status transition writes a `complaint_history` row (audit trail, never mutate history).
4. Critical complaint subcategories (e.g. Gas Leakage, Main Power Failure) trigger an immediate "Critical Complaint" admin notification regardless of normal queue order.

---

## 8. Planned Modules & Sequencing

| # | Module | Scope | Status |
|---|---|---|---|
| 1 | Project Planning | Architecture, folder structure, roadmap | ✅ Complete |
| 2 | Database Design | ER diagram, SQLAlchemy models, Alembic migrations | ✅ Complete |
| 3 | Authentication | JWT issuing/refresh, RBAC, password hashing, registration/approval flow | ✅ Complete |
| 4 | Resident Mobile App | Expo project setup, navigation, auth screens (complaint screens deferred to Module 6, no backend yet) | ✅ Foundation complete |
| 5 | Admin Portal | Vite project setup, dashboard, registration approval, complaint triage | ⬜ Not started |
| 6 | Complaint System | Full backend CRUD + state machine + history + assignment logic | ⬜ Not started |
| 7 | Notification System | FCM integration (push), in-app notification center, admin alerts | ⬜ Not started |
| 8 | Feedback System | Complaint feedback (stars + comment), app feedback (bugs/suggestions) | ⬜ Not started |
| 9 | Emergency Module | Emergency contacts CRUD + resident-facing quick-dial screen | ⬜ Not started |
| 10 | Testing | Backend unit/integration tests, frontend component tests | ⬜ Not started |
| 11 | Deployment | Render (backend, free tier + keep-alive), Vercel (admin portal + PWA fallback), Supabase (DB), EAS build (mobile) | ⬜ Not started |
| 12 | Future Features | Visitor management, billing, announcements, analytics, heatmaps, AI categorization, OCR, chatbot | ⬜ Backlog |

**Rule:** each module is fully built, verified, and documented before the next one begins. No module starts without explicit confirmation from Ali.

---

## 9. Planned Screens

**Resident Mobile App**
- Splash / Onboarding
- Register (multi-step: basic info → employee/tenant branch → review)
- Pending Verification (waiting screen)
- Login
- Home Dashboard (quick actions, recent complaints, emergency shortcut)
- New Complaint (category → subcategory → description → photo → submit)
- Complaint Detail / Timeline
- My Complaints (list, filter by status)
- Feedback (post-resolution rating)
- Emergency Contacts
- Profile (resident info, house info, logout)
- Notifications Center

**Admin Portal**
- Login
- Dashboard (pending complaints, pending registrations, KPIs)
- Registrations Queue (approve/reject)
- Complaints Queue (filter, assign, bulk actions)
- Complaint Detail (full history, assign staff, close)
- House Directory / House Profile
- Resident Directory / Resident Profile
- Staff Management
- Emergency Contacts Management
- Feedback & App Feedback view
- Notifications Log
- Settings (IT Admin / Super Admin only)

---

## 10. Planned API Surface (v1, high-level — full contracts land in Module 2/3)

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout

GET    /api/v1/registrations/pending          (admin)
POST   /api/v1/registrations/{id}/approve     (admin)
POST   /api/v1/registrations/{id}/reject      (admin)

GET    /api/v1/houses/{house_code}
GET    /api/v1/houses/{house_code}/complaints
GET    /api/v1/residents/{resident_code}

POST   /api/v1/complaints
GET    /api/v1/complaints
GET    /api/v1/complaints/{id}
PATCH  /api/v1/complaints/{id}/status
POST   /api/v1/complaints/{id}/assign         (admin)
POST   /api/v1/complaints/{id}/reopen         (resident)
POST   /api/v1/complaints/{id}/close          (resident/admin, per rule)

POST   /api/v1/feedback/complaint
POST   /api/v1/feedback/application

GET    /api/v1/emergency-contacts

GET    /api/v1/notifications
POST   /api/v1/notifications/mark-read
```

---

## 11. Role Permissions Matrix

| Action | Resident | Housing Office Admin | IT Admin | Maintenance Staff | Super Admin |
|---|---|---|---|---|---|
| Submit complaint | ✅ | – | – | – | ✅ |
| Track complaint | ✅ | ✅ | ✅ | View assigned only | ✅ |
| Give feedback | ✅ | – | – | – | – |
| Close complaint (1st time) | ✅ | – | – | – | ✅ |
| Reopen complaint | ✅ | – | – | – | ✅ |
| Close reopened complaint | – | ✅ | – | – | ✅ |
| Approve/reject registration | – | ✅ | – | – | ✅ |
| Assign complaint to staff | – | ✅ | – | – | ✅ |
| Manage users / reset passwords | – | – | ✅ | – | ✅ |
| Manage app settings | – | – | ✅ | – | ✅ |
| Update complaint status / upload notes | – | – | – | ✅ (assigned only) | ✅ |
| Full system access | – | – | – | – | ✅ |

---

## 12. Non-Functional Requirements
- Responsive UI across phone/tablet/desktop
- PWA-installable admin portal (fallback web access)
- Dark mode + light mode, both fully designed (not an afterthought)
- Fast initial load, optimistic UI where safe
- Secure auth: hashed passwords (bcrypt/argon2), short-lived access tokens, rotated refresh tokens
- Role-Based Access Control enforced server-side on every endpoint
- Feature-based, SOLID, type-safe, no duplicated logic
- Scalable to multiple societies/blocks in the future (house_code namespacing already supports this)

---

## 13. Development Progress Checklist

- [x] Requirements gathered from both spec documents
- [x] Repo skeleton created (`backend/`, `admin-portal/`, `mobile-app/`, `docs/`)
- [x] PROJECT_ROADMAP.md drafted
- [x] Roadmap reviewed & confirmed by Ali
- [x] Module 2: Database Design
- [x] Module 3: Authentication
- [x] Module 4: Resident Mobile App (auth flow foundation)
- [ ] Module 5: Admin Portal
- [ ] Module 6: Complaint System
- [ ] Module 7: Notification System
- [ ] Module 8: Feedback System
- [ ] Module 9: Emergency Module
- [ ] Module 10: Testing
- [ ] Module 11: Deployment
- [ ] Module 12: Future Features (backlog)

---

## 14. Completed Modules

**Module 1 — Project Planning:** Architecture, folder structure, and this roadmap. Confirmed.

**Module 2 — Database Design:**
- `backend/app/core/config.py` — env-driven settings (SQLite dev / PostgreSQL prod via one `DATABASE_URL` var)
- `backend/app/core/database.py` — SQLAlchemy engine, session factory, declarative `Base`
- `backend/app/models/enums.py` — every fixed value set (resident type, verification status, admin role, staff category, complaint category/status, changed-by type, application feedback type, notification recipient type) defined once
- 10 SQLAlchemy models, one file each: `house.py`, `resident.py`, `admin.py`, `staff.py`, `complaint.py`, `complaint_history.py`, `feedback.py`, `application_feedback.py`, `emergency_contact.py`, `notification.py`
- `backend/alembic/` fully wired: `env.py` resolves the DB URL from `app.core.config.Settings` (not hardcoded), imports `app.models` so autogenerate sees the full schema
- First migration generated and applied against a live SQLite DB — all 10 tables created correctly
- Verified end-to-end: inserted a House → Resident → Complaint → ComplaintHistory chain via the ORM, queried it back through relationships, and confirmed the `feedback.rating` CHECK constraint (1–5) rejects invalid values at the DB level
- `docs/ER_DIAGRAM.md` — Mermaid ER diagram generated from the actual models, plus notes on the deliberate design decisions (nullable `resident_code`, polymorphic `changed_by_type`/`changed_by_id` on history, 1:1 Feedback via unique FK)

**Module 3 — Authentication:**
- `backend/app/core/security.py` — password hashing (bcrypt via passlib) and JWT create/decode; the one place either library is touched directly
- `backend/app/models/refresh_token.py` + new migration — durable, revocable refresh tokens (rotation on every `/auth/refresh`, real revocation on `/auth/logout`)
- `backend/app/schemas/auth.py` — `RegisterRequest` encodes the exact employee/tenant branching decision tree from the spec, with a `model_validator` that rejects inconsistent combinations before they ever reach the DB
- `backend/app/services/id_generation.py` — the one place `resident_code` strings are built (`EHS-B-026-O`, `EHS-B-026-T1`, `EHS-B-026-T2`...)
- `backend/app/services/auth_service.py` and `registration_service.py` — registration, login, token issuance/refresh/revocation, and the approve/reject flow that assigns `resident_code` only after admin approval
- `backend/app/api/v1/{auth,registrations,me}.py` + `deps.py` — routers and the RBAC dependency (`require_admin_roles`) that re-checks role against the live DB row, never the JWT claim alone
- `backend/scripts/create_admin.py` — bootstraps the first Super Admin (admins are never self-registered)
- Full details, endpoint table, and the verified test transcript: `docs/MODULE_3_AUTHENTICATION.md`
- **Bug found and fixed:** `passlib==1.7.4` is incompatible with `bcrypt>=4.1`; pinned `bcrypt==4.0.1` in `requirements.txt`

**Module 4 — Resident Mobile App (foundation):**
- Expo SDK 57 + TypeScript project scaffolded with `expo-router`; static web export confirmed working (this is the actual iOS PWA path agreed in Section 4.1, not a theoretical one)
- `lib/api-client.ts` — axios with automatic access-token attachment and transparent refresh-and-retry on 401, calling the same `/auth/refresh` rotation built in Module 3
- `lib/auth-context.tsx`, `lib/token-storage.ts`, `lib/types.ts` (mirrors the backend's Pydantic schemas field-for-field), `lib/theme.ts` (copied from Section 5's palette, not reinvented)
- Screens: routing gate, login, 3-step register (branching logic matches the backend's validator exactly), pending-verification, home dashboard
- **Complaint screens deliberately deferred** — no complaint API exists yet (Module 6); building against a nonexistent backend would mean mocking data, which this project has avoided everywhere else
- Verified: clean `tsc --noEmit`, successful `expo export --platform web`, and a full integration test hitting the live backend with the app's exact request/response shapes — confirmed `resident_code`, `verification_status`, and `full_name` come back correctly for a real register → approve → login → `/residents/me` flow, and that the refresh-token flow works
- Full details: `docs/MODULE_4_MOBILE_APP.md`

**⚠️ Gap against Section 4.2's standards (added after Module 4 shipped):** the frontend platform spec was finalized *after* this module's four screens were built, so they don't yet reflect it. Specifically:
- Styling uses React Native `StyleSheet`, not NativeWind
- Auth state uses React Context, not Zustand
- No Reanimated/Moti animations exist yet (screen transitions, press feedback, skeletons, etc. are all static)
- Only 3 shared primitives exist (`AppButton`, `AppTextField`, `ScreenContainer`) against the 13 now specified in Section 4.2
- No PWA manifest/icons/service worker/splash screen configured beyond `app.json`'s minimal web block
- Safe-area insets are only applied at the screen-container root, not per-component where iOS notch/Dynamic Island/gesture-bar clearance actually matters

This is flagged rather than silently left, per the project's own "roadmap must reflect the current real state, not the aspirational state" rule. Retrofitting this is a real, scoped task — not yet started.

## 15. Remaining Modules
- Modules 5 through 12, as listed in Section 8. (Complaint screens for the mobile app will be added alongside Module 6, once that backend exists.)

## 16. Known Issues
- None open. The `passlib`/`bcrypt` version conflict above was caught and fixed during Module 3, not left latent.

## 17. Future Improvements / Backlog (Module 12)
- Visitor Management
- Maintenance Billing
- Announcements / Society Notices
- Analytics Dashboard
- Complaint Heatmaps
- SMS Notifications
- AI Complaint Categorization
- OCR Support
- Chatbot

## 18. Deployment Plan (high-level, detailed in Module 11)
- **Backend + Admin-facing web frontend:** one unified Vercel project — FastAPI as Python serverless functions under `/api/*`, Expo's web export served as static files for everything else, same domain (see status update below for why this replaced the earlier Render plan)
- **Database:** PostgreSQL via Supabase (session pooler connection string, suited to serverless's short-lived connections)
- **Mobile App:** Expo EAS Build → TestFlight (iOS) and Play Store internal testing (Android) before public release
- **Secrets:** JWT secret, Zoho SMTP credentials, FCM service account, DB URL — all via environment variables, never committed

**Status update (pulled forward from Module 11, ahead of schedule):**
This went through three iterations before landing here, each for a
concrete reason:
1. **Railway first** — dropped once we confirmed its free trial is
   genuinely time/credit-limited (30 days or $5, then paid).
2. **Render second** — genuinely free indefinitely, but hit a real wall:
   Render requires card verification (a $1 refundable authorization, not a
   charge) for many new accounts as anti-abuse policy, and Ali didn't have
   a usable card at the time.
3. **Vercel, unified with the frontend — final decision.** Vercel's Hobby
   plan needs no card at all and has much faster cold starts (~1-2s vs
   Render's 30-60s). Since Vercel doesn't run a persistent server the way
   Render/Railway do, the backend was adapted to serverless: `api/index.py`
   wraps the existing FastAPI app unchanged, and `mobile-app`'s Expo web
   export is served as the static frontend — both under one Vercel
   project, one domain.

The code side is done and verified:
- `vercel.json` (repo root) — defines both builds and the routing between
  them, including an explicit `/health` rule (this doesn't start with
  `/api/`, so without that rule it would have 404'd against the static
  frontend instead of reaching the backend — caught and fixed, not left
  as a latent bug)
- `api/index.py` — thin adapter importing the real FastAPI app; tested
  directly with a real `TestClient` exactly as Vercel's runtime would use
  it — `GET /health` returned `200`, `POST /api/v1/auth/register` wrote a
  real row and returned `201`
- `requirements.txt` (repo root, duplicate of `backend/requirements.txt` —
  Vercel's Python builder needs it there; **must be kept in sync manually**)
- `app/core/database.py` — switches to `NullPool` when Vercel's `VERCEL`
  env var is present (serverless functions shouldn't hold their own local
  connection pool alongside Supabase's external one); verified directly
  that the pool class actually changes with/without that env var
- `mobile-app/package.json`'s `vercel-build` script — verified it actually
  produces `dist/` with all 5 routes, matching what `@vercel/static-build` expects
- Full step-by-step account setup: `docs/DEPLOYMENT_SETUP.md`

**Not yet done — needs Ali's browser, not code:** creating the actual
Vercel project and connecting the (already-pushed) GitHub repo, setting
the environment variables, and running the first real deploy. Migrations
against the real Supabase database also need to be run manually from a
local machine now (documented in the deployment guide) — a genuine
workflow difference from Render/Railway's "runs automatically on deploy"
model, since Vercel's serverless functions have no persistent start
command to hook into.

**Honest caveat:** this sandbox has no network path to Vercel, GitHub, or
Supabase, so every piece was tested individually and end-to-end as far as
this environment allows — but the actual combined Vercel build (two
builders, real routing, a real serverless-to-Supabase connection) hasn't
been exercised by a live deploy yet. This is a newer, less well-trodden
setup than Render's single-service model, so there's a real chance the
first deploy surfaces something.

## 19. Testing Checklist (executed in Module 10)
- [ ] Backend unit tests: auth, complaint state machine, ID generation logic
- [ ] Backend integration tests: registration → approval → login flow; full complaint lifecycle
- [ ] RBAC tests: every endpoint tested against every role, confirming correct 403s
- [ ] Frontend component tests: forms (registration, new complaint), status badges
- [ ] Manual QA: dark/light mode on both apps, offline behavior on mobile, push notification delivery

---

**Next step:** please review Module 4's mobile app foundation (see `docs/MODULE_4_MOBILE_APP.md` for the full scope note and integration test transcript). Once confirmed, Module 5 (Admin Portal — Vite project setup, dashboard, registration approval, complaint triage) begins.
