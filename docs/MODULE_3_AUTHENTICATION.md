# Module 3 — Authentication

Everything below was executed against a running server, not just written.
See the test transcript summary at the bottom.

## Endpoints

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/api/v1/auth/register` | none | Resident self-registration. Always results in `verification_status=pending`. |
| POST | `/api/v1/auth/login` | none | Resident login by phone or email. Fails if not yet approved. |
| POST | `/api/v1/auth/admin/login` | none | Admin login by email. |
| POST | `/api/v1/auth/refresh` | refresh token (body) | Rotates the refresh token; old `jti` is revoked. |
| POST | `/api/v1/auth/logout` | refresh token (body) | Revokes that refresh token's `jti`. Always "succeeds" from the client's view. |
| GET | `/api/v1/registrations/pending` | admin (Housing Office / Super Admin) | List residents awaiting verification. |
| POST | `/api/v1/registrations/{id}/approve` | admin (Housing Office / Super Admin) | Generates `resident_code`, sets `approved`. |
| POST | `/api/v1/registrations/{id}/reject` | admin (Housing Office / Super Admin) | Sets `rejected`. |
| GET | `/api/v1/residents/me` | resident (Bearer access token) | Smoke-test route for the resident auth dependency. |
| GET | `/api/v1/admins/me` | admin (Bearer access token) | Smoke-test route for the admin auth dependency. |

## Registration request shape

```json
{
  "full_name": "Ali Khan",
  "house_number": "B-026",
  "mobile_number": "03001234567",
  "email": "ali@example.com",
  "password": "password123",
  "is_awc_employee": false,

  "is_tenant": true,
  "owner_house_number": "B-026",
  "owner_name": "Owner Name",
  "owner_cnic": "12345-6789012-3",
  "owner_mobile_number": "03000000000"
}
```

`resident_type` is never sent by the client — it's derived server-side from
`is_awc_employee` / `is_tenant`, and the request is rejected (422) if the
combination is inconsistent (e.g. an employee also claiming to be a
tenant, or a non-tenant sending owner fields).

## Design decisions worth flagging

1. **`house_number` format assumption.** The spec's example house code is
   `EHS-B-026`. I assumed residents submit the raw `"B-026"` part at
   registration and the server prepends `EHS-` and derives the block
   (`"B"`) from it — this wasn't fully spelled out in the roadmap, so flag
   it if house numbering in the real society doesn't follow `<BLOCK>-<NUMBER>`.
2. **Stateful refresh tokens, not pure stateless JWT.** A `refresh_tokens`
   table (new in this module, tracked in its own migration) stores each
   issued refresh token's `jti`. This is what makes `/auth/logout` and
   token rotation actually mean something — a bare JWT's signature can't
   be revoked before its natural expiry. Verified: reusing an
   already-rotated or already-logged-out refresh token now returns 401.
3. **Role re-checked from the DB on every protected request**, not trusted
   from the JWT claim alone (roadmap Section 2's explicit requirement).
   `require_admin_roles(...)` and `refresh_token_pair` both re-read the
   live role/status from the database.
4. **Staff have no login in this module.** Per the roadmap's own module
   scope and the `Staff` model's docstring, maintenance staff are managed
   by admins and don't authenticate directly in v1 — only Resident and
   Admin get JWT-based auth here.
5. **Admins can't self-register.** `scripts/create_admin.py` bootstraps
   the first Super Admin from the command line — there is intentionally no
   public "become an admin" endpoint.

## Verified end-to-end (via live HTTP requests against `uvicorn`)

- ✅ Owner registration → login blocked while pending → admin approves →
  `resident_code = EHS-B-026-O` generated → login now succeeds
- ✅ `GET /residents/me` returns the correct resident via a real Bearer token
- ✅ A resident token hitting an admin-only route correctly gets `403`
- ✅ Refresh rotates the token pair; the *old* refresh token is rejected
  on reuse (`401`)
- ✅ Logout revokes the refresh token; using it afterward is rejected (`401`)
- ✅ Registering an employee without `employee_number`, or a tenant without
  owner details, is rejected at the schema level (`422`) before touching the DB
- ✅ Two tenants registered against the same house and approved in order
  received `EHS-B-026-T1` and `EHS-B-026-T2` respectively
- ✅ A second owner registered against a house that already has an
  approved owner is correctly blocked at approval time (`409`)
- 🐛 **Found and fixed a real dependency bug**: `passlib==1.7.4` breaks
  under `bcrypt>=4.1` (`AttributeError: module 'bcrypt' has no attribute
  '__about__'`). Pinned `bcrypt==4.0.1` in `requirements.txt`.
