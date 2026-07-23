# Module 4 — Resident Mobile App (foundation)

## Scope actually delivered

Per the roadmap's own sequencing rule ("each module fully built and verified
before the next begins"), this module covers **project setup, navigation,
and the complete auth flow** end to end against the real backend.
**Complaint screens are intentionally deferred** — there is no complaint
API yet (that's Module 6). Building complaint UI against a nonexistent
backend would mean either mocking data (which we've avoided everywhere
else in this project) or building twice. They'll be added once Module 6
ships, reusing the navigation/theming/API-client foundation built here.

## What's in `mobile-app/`

- Expo SDK 57, TypeScript, `expo-router` for file-based navigation
- `lib/api-client.ts` — axios instance with an interceptor that attaches
  the access token and, on a 401, transparently calls `/auth/refresh` and
  retries the original request once — mirroring the backend's refresh
  rotation from Module 3 exactly (concurrent 401s are coalesced into a
  single refresh call, not one per failed request)
- `lib/auth-context.tsx` — `register` / `login` / `logout`, backed by
  `lib/token-storage.ts` (AsyncStorage, works identically on native and
  the web/PWA build)
- `lib/types.ts` — TypeScript types mirroring
  `backend/app/schemas/*.py` and `backend/app/models/enums.py` field-for-field
- `lib/theme.ts` — the design tokens from `PROJECT_ROADMAP.md` Section 5,
  copied exactly (not reinvented) so mobile and admin portal will visually agree
- `components/{AppButton,AppTextField,ScreenContainer}.tsx` — shared primitives
- Screens: `index.tsx` (routing gate), `login.tsx`, `register.tsx`
  (3-step, branching logic mirrors the backend's `RegisterRequest`
  validator exactly — employee ⇒ employee_number required; tenant ⇒ all
  four owner fields required), `pending.tsx`, `home.tsx`

## Verified, not just written

1. `npx tsc --noEmit` — clean, zero errors, across the whole app.
2. `npx expo export --platform web` — succeeded, statically rendered all 5
   routes (`/`, `/login`, `/register`, `/pending`, `/home`) with no runtime
   errors. This is the exact build path for the iOS PWA testing strategy
   agreed in Section 4.1 — proving that path works, not just assuming it.
3. **Full integration test against the live FastAPI backend**, using the
   *exact* request/response shapes the app's own code sends and reads
   (not hand-picked happy-path JSON):
   - `POST /auth/register` with the exact `RegisterRequest` fields `lib/types.ts` defines
   - Admin approval (reusing Module 3's flow)
   - `POST /auth/login` with the exact `LoginRequest` shape from `auth-context.tsx`
   - `GET /residents/me` — asserted that `resident_code`, `verification_status`,
     and `full_name` (the exact fields `home.tsx` and `index.tsx` read) come back
     correctly: `resident_code` was `EHS-D-777-O`, `verification_status` was `approved`
   - An invalid token correctly got rejected with `401` (the case the
     interceptor's refresh logic exists to handle)
   - `POST /auth/refresh` returned a fresh access + refresh token pair

## Design decisions worth flagging

1. **No `.env` is committed** (`.env.example` is, with instructions). Every
   developer must set `EXPO_PUBLIC_API_BASE_URL` to their own machine's LAN
   IP — `localhost` silently fails on a physical phone or in the PWA on a
   different device, so the api-client warns loudly at startup if it's unset.
2. **AsyncStorage, not SecureStore**, for tokens. `expo-secure-store` has no
   web implementation, and the iOS testing path *is* web (the PWA). This is
   a reasonable dev/testing-phase tradeoff, worth revisiting for the
   production release milestone in Module 11.
3. **Registration is a single form component with step-based rendering**,
   not separate route screens per step. This keeps one `react-hook-form`
   instance (and one Zod schema) as the single source of truth for
   validation across all three steps, rather than passing partial state
   between routes.
4. **The routing gate (`index.tsx`) queries `/residents/me` on every app
   open**, not just once at login, so a resident whose status changes
   between sessions (e.g. approved after the pending screen was last seen)
   gets routed correctly without needing to log out and back in.
