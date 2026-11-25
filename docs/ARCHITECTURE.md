# FormSaathi — Product & System Architecture (Phase 1)

> **Tagline:** Never Miss an Opportunity You Deserve.
> **Core loop:** Discover → Check Eligibility → Understand Requirements → Prepare Documents → Complete Application → Track Progress.

This document is the single source of truth for *what* we are building and *how the pieces fit*.
Database details live in [DATABASE.md](DATABASE.md); visual language lives in [DESIGN.md](DESIGN.md).

---

## 1. Product principles (these drive every technical decision)

| # | Principle | What it means in code |
|---|-----------|------------------------|
| P1 | **Truth over volume** | Every opportunity carries `source_url`, `organization`, `last_verified_at`, `verification_status`, `data_origin`. Nothing is shown as "verified" unless an admin verified it. |
| P2 | **Rules decide, AI explains** | Eligibility is computed by a deterministic rule engine over *structured, admin-entered* criteria. The LLM only explains the result in plain language and answers follow-ups. It never invents rules. |
| P3 | **Three labels, always visible** | `Verified` (admin-checked official data) · `Demo` (sample data for showcasing UI) · `AI guidance` (generated text, not official advice). |
| P4 | **Minimum personal data** | Sensitive fields (income, social category, disability) are optional, explained, and only used for matching. Documents are private, never publicly addressable. |
| P5 | **User confirms reality** | The tracker never claims "Applied/Approved" on its own. Status changes are user-confirmed (or come from an authorised integration, flagged as such). |
| P6 | **No dead buttons** | Any unconfigured service (LLM, SMTP) shows an honest "not configured" state instead of pretending. |

---

## 2. System architecture

```
                         ┌──────────────────────────────────────────────┐
                         │        Browser — Vue 3 SPA (Vite build)      │
                         │  Router · Pinia stores · Bootstrap 5 + tokens│
                         │  i18n (en / hi / mr) · Lucide icons          │
                         └───────────────┬──────────────────────────────┘
                                         │  HTTPS, JSON
                                         │  JWT in HttpOnly cookies + CSRF header
                         ┌───────────────▼──────────────────────────────┐
                         │          Flask API  (/api/v1/...)            │
                         │  Blueprints: auth · profile · opportunities  │
                         │  eligibility · ai · documents · applications │
                         │  notifications · admin · meta                │
                         │  ── middleware: rate limit, validation,      │
                         │     error handler, request logging           │
                         ├──────────────────────────────────────────────┤
                         │  Services layer (pure Python, unit-testable) │
                         │  EligibilityEngine · RecommendationService   │
                         │  LLMClient (provider adapter) · Mailer       │
                         │  FileStorage · NotificationService           │
                         └──┬──────────────┬──────────────┬─────────────┘
                            │              │              │
               ┌────────────▼───┐  ┌───────▼───────┐  ┌───▼──────────────┐
               │ PostgreSQL 16  │  │ Private file  │  │ External APIs    │
               │ (SQLAlchemy 2, │  │ storage       │  │ LLM API (env key)│
               │  Alembic)      │  │ (local dir or │  │ SMTP (env creds) │
               └────────▲───────┘  │  S3-compatible)│  └──────────────────┘
                        │          └───────────────┘
               ┌────────┴──────────────────────┐
               │ Worker process (APScheduler)  │
               │ deadline reminders · expiry   │
               │ sweeps · email digests        │
               └───────────────────────────────┘
```

### Key decisions

| Decision | Choice | Why |
|----------|--------|-----|
| API style | Flask **Blueprints** + REST, versioned `/api/v1` | Simple, beginner-readable, no extra abstraction layer. |
| ORM / migrations | SQLAlchemy 2.0 + Flask-Migrate (Alembic) | Industry standard; schema changes are reviewable migration files. |
| Validation | **Marshmallow** schemas per endpoint | Declarative input validation + consistent error JSON. |
| Auth | **flask-jwt-extended**, tokens in **HttpOnly, Secure, SameSite=Lax cookies**, built-in double-submit **CSRF** | Tokens are not readable by JS (XSS-resistant); CSRF protected; works for SPA. Access 15 min, refresh 14 days, revocation table on logout. |
| Passwords | Argon2id (`argon2-cffi`) | Current best practice; bcrypt fallback not needed. |
| Roles | `user`, `admin` on the `users` table | One identity table; admins are users with a role (no duplicate "AdminUsers" accounts). Role checked by a `@role_required` decorator. |
| Rate limiting | Flask-Limiter (memory in dev, Redis in prod) | Stricter limits on login, password reset, AI chat, uploads. |
| Background jobs | **APScheduler in a separate worker process** (`python -m app.worker`) | No Redis/Celery needed to start; swap to Celery later if load demands. |
| File storage | Private directory outside web root, random UUID filenames, served only through an authorised endpoint | Documents are never publicly addressable. Adapter allows S3 later. |
| LLM | Provider adapter (`LLMClient`) with Anthropic Claude as default; key + model from env | Keys never reach the frontend. When `LLM_API_KEY` is absent the AI endpoints return `503 ai_not_configured` and the UI says so. |
| Email | SMTP via env vars; when unset, emails are logged to console and UI marks email as "not configured" | Honest dev experience. |
| Search | Phase 4: `ILIKE` + filters (portable). Postgres: GIN `pg_trgm` index for fast fuzzy title search. | Good enough for thousands of records; no Elasticsearch needed. |
| Dev DB | PostgreSQL is the target. `DATABASE_URL` may point to SQLite for quick local runs and tests | The migration and full test suite are verified on both. |
| Frontend | Vue 3 + Vite + Vue Router + Pinia + Bootstrap 5 (SCSS, themed) + `lucide-vue-next` + `vue-i18n` | As specified; Bootstrap is themed via SCSS variables so it doesn't look "default Bootstrap". |

---

## 3. Repository layout

```
formsaathi/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md        ← this file
│   ├── DATABASE.md            ← schema, ERD, constraints
│   └── DESIGN.md              ← brand + design system
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── wsgi.py                ← entry point (flask run / gunicorn)
│   ├── migrations/            ← Alembic (Flask-Migrate)
│   ├── app/
│   │   ├── __init__.py        ← create_app() factory
│   │   ├── config.py          ← Dev / Test / Prod config from env
│   │   ├── extensions.py      ← db, migrate, jwt, limiter, ma
│   │   ├── models/            ← SQLAlchemy models (Phase 1 ✅)
│   │   ├── schemas/           ← Marshmallow validation (Phase 3+)
│   │   ├── api/               ← Blueprints, one file per domain
│   │   ├── services/          ← eligibility, recommendation, llm, mail, storage
│   │   ├── utils/             ← decorators, errors, pagination
│   │   ├── seed/              ← demo data + reference data loaders
│   │   └── worker.py          ← scheduled jobs
│   └── tests/
└── frontend/                  ← Phase 2
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/            ← routes + auth/role guards
        ├── stores/            ← Pinia: auth, profile, opportunities, tracker, ui
        ├── api/               ← axios client + per-domain modules
        ├── layouts/           ← PublicLayout, AppLayout (sidebar), AdminLayout
        ├── views/             ← pages (see sitemap)
        ├── components/        ← ui/ (design system) + feature components
        ├── i18n/              ← en.json, hi.json, mr.json
        └── styles/            ← _tokens.scss, bootstrap overrides, utilities
```

---

## 4. Sitemap

### Public (no login)
| Route | Page | Notes |
|-------|------|-------|
| `/` | Landing | Navbar, hero + smart search, trust strip, how it works, categories, featured (demo-labelled), why FormSaathi, FAQ, footer |
| `/explore` | Explore opportunities | Public browse with filters; eligibility check & save prompt login |
| `/opportunities/:slug` | Opportunity detail | Full verified details; "Check my eligibility" CTA |
| `/how-it-works` | How it works | Expanded 6-step journey |
| `/about` | About | Mission, data-accuracy policy |
| `/help` | Help centre | FAQs, how verification works |
| `/privacy`, `/terms` | Legal | Plain-language summaries |
| `/contact` | Contact | Feedback form (stored in `feedback`) |
| `/login`, `/register` | Auth | |
| `/forgot-password`, `/reset-password/:token` | Password reset | |

### Authenticated user (`AppLayout` with collapsible sidebar; bottom tab bar on mobile)
| Route | Page |
|-------|------|
| `/onboarding` | 5-step onboarding wizard (forced on first login until complete or skipped) |
| `/app` | Dashboard |
| `/app/discover` | Discovery engine (personalised filters + "Recommended for you") |
| `/app/opportunities/:slug` | Detail + eligibility panel + required-docs checklist |
| `/app/eligibility/:slug` | Eligibility report + follow-up questions |
| `/app/compare?ids=1,2,3` | Side-by-side comparison (max 3) |
| `/app/saved` | Saved opportunities & collections |
| `/app/tracker` | Application tracker (board on desktop, grouped list on mobile) |
| `/app/tracker/:id` | Application detail: status timeline, notes, reminders |
| `/app/calendar` | Deadline & reminder calendar |
| `/app/documents` | Document vault + per-opportunity checklists |
| `/app/saathi` | Saathi AI chat (with history) |
| `/app/notifications` | Notification centre |
| `/app/profile` | Profile & completion |
| `/app/settings` | Language, theme, notification preferences, privacy (export / delete account) |

### Admin (`AdminLayout`, `role = admin`)
| Route | Page |
|-------|------|
| `/admin` | Analytics overview |
| `/admin/opportunities` | List + filters by verification/publication status |
| `/admin/opportunities/new`, `/:id/edit` | Editor: details, eligibility criteria builder, required documents, dates, sources |
| `/admin/verification` | Verification queue (pending, stale >30 days, deadline passed) |
| `/admin/corrections` | User-submitted correction reports |
| `/admin/categories` | Categories CRUD |
| `/admin/users` | Users: search, deactivate, change role |
| `/admin/featured` | Featured ordering |
| `/admin/announcements` | Announcements CRUD |

---

## 5. User journeys

### J1 — First-time student (core journey)
1. Lands on `/` → searches "scholarship for engineering students" in hero search → `/explore` with results.
2. Clicks **Check eligibility** → prompted to sign up (return URL preserved).
3. Registers → verification email (if SMTP configured) → **Onboarding**: ① Basics (name, DOB) ② Location ③ Education (level, institution, course, year, marks) ④ Optional context (income range, category — with "why we ask" explainers and a *Skip* that genuinely skips) ⑤ Interests & language.
4. Lands on **Dashboard**: "Recommended for you" populated by rule-based matching; profile-completion ring shows what's missing and how it improves matches.
5. Opens an opportunity → **Eligibility panel** shows *Eligible / Possibly eligible / Not eligible* with criterion-by-criterion ✓ / ✗ / ? and the official source excerpt for each rule.
6. Clicks **Track this** → added to tracker as *Interested*; required-documents checklist is generated and cross-checked against the document vault.
7. Uploads missing documents → checklist ticks over → status suggestion: "All documents ready — mark as *Ready to apply*?"
8. Opens official link (external, clearly labelled) → applies on the official portal → returns and confirms **Applied** with date + reference number.
9. Receives reminders (in-app + email) before deadlines and to update status.

### J2 — Returning user
Login → dashboard shows upcoming deadlines (≤14 days), pending documents, new matches since last visit, unread notifications → one-click actions.

### J3 — Confused applicant using Saathi AI
Opens opportunity → "Ask Saathi about this" → chat preloaded with that opportunity's verified record as context → asks "What is a domicile certificate?" in Hindi → answer in Hindi, with a footer: *AI guidance, not official advice. Always confirm on the official source.* Suggested prompts: "Make my checklist", "Explain eligibility simply", "What does 'non-creamy layer' mean?".

### J4 — Admin adds and verifies an opportunity
Admin → New opportunity → fills details from the official notification → adds structured eligibility criteria (each with a quoted source excerpt) → adds required docs and dates → saves as **Draft / Pending verification** → reviewer opens source URL, confirms → **Verified** (writes a `source_verification_logs` row, sets `last_verified_at`) → **Publish**. Nightly job marks past-deadline opportunities **Expired** and removes them from recommendations.

### J5 — User reports an error
On an opportunity page → "Report a correction" → selects field + message → admin sees it in the corrections queue → accepts (edits record, re-verifies) or rejects with a note → user is notified.

### J6 — Privacy
Settings → download my data (JSON) · delete a document (file removed from storage, row soft-deleted then purged) · delete account (cascades all personal data).

---

## 6. Eligibility engine (design)

```
Opportunity.eligibility_criteria  (structured, admin-entered, each with source_excerpt)
            │
            ▼
EligibilityEngine.evaluate(profile, criteria)  ── deterministic, unit-tested
            │   per criterion → MET | NOT_MET | UNKNOWN (profile field missing)
            │                   | NEEDS_REVIEW (criterion_type = custom / free text)
            ▼
Overall verdict:
   any mandatory NOT_MET            → NOT_ELIGIBLE
   else any UNKNOWN / NEEDS_REVIEW  → POSSIBLY_ELIGIBLE (lists exactly what's needed)
   else                             → ELIGIBLE
            │
            ▼
LLM (optional) receives ONLY: verdict + per-criterion results + source excerpts
→ returns structured JSON {summary, per_criterion_explanations[], next_steps[]}
→ validated against a schema; on failure we fall back to template text.
```

No percentages are shown. Results are stored in `eligibility_checks` with a hash of the profile fields used, so a profile change invalidates the cache.

## 7. Recommendation engine (design)
Phase 4, rule-based and explainable: candidate set = published + verified-or-demo + not expired → hard filter via eligibility engine (drop `NOT_ELIGIBLE`) → score by interest-category match, deadline proximity, recency, profile-fit count → each card shows "Why recommended" chips (e.g. *Matches your state*, *For B.Tech students*).

## 8. API surface (v1, summary)

| Blueprint | Key endpoints |
|-----------|---------------|
| `auth` | `POST /auth/register` · `POST /auth/login` · `POST /auth/logout` · `POST /auth/refresh` · `GET /auth/me` · `POST /auth/forgot-password` · `POST /auth/reset-password` · `POST /auth/verify-email` |
| `profile` | `GET/PUT /profile` · `GET /profile/completion` · `PUT /profile/onboarding/:step` · `GET /profile/export` · `DELETE /account` |
| `opportunities` | `GET /opportunities` (q, category, education, state, income, deadline_before, status, sort, page) · `GET /opportunities/:slug` · `GET /opportunities/featured` · `GET /opportunities/recommended` · `GET /opportunities/compare?ids=` · `POST /opportunities/:id/corrections` |
| `saved` | `GET/POST/DELETE /saved` · CRUD `/collections` |
| `eligibility` | `POST /eligibility/:opportunity_id/check` · `POST /eligibility/:opportunity_id/ask` |
| `ai` | `GET/POST /ai/sessions` · `GET /ai/sessions/:id` · `POST /ai/sessions/:id/messages` · `DELETE /ai/sessions/:id` · `GET /ai/status` |
| `documents` | `GET /documents` · `POST /documents` (multipart) · `GET /documents/:id/file` (auth'd stream) · `PATCH/DELETE /documents/:id` · `GET /documents/checklist/:opportunity_id` · `GET /documents/checklist/:opportunity_id.pdf` |
| `applications` | CRUD `/applications` · `PATCH /applications/:id/status` · `GET /applications/:id/history` · CRUD `/applications/:id/notes` · CRUD `/reminders` · `GET /calendar?from=&to=` |
| `notifications` | `GET /notifications` · `POST /notifications/:id/read` · `POST /notifications/read-all` · `GET/PUT /notifications/preferences` |
| `meta` | `GET /meta/categories` · `GET /meta/states` · `GET /meta/document-types` · `GET /meta/announcements` · `POST /feedback` · `GET /health` |
| `admin` | `GET /admin/stats` · CRUD `/admin/opportunities` (+ `/criteria`, `/documents`, `/dates`) · `POST /admin/opportunities/:id/verify` · `POST .../status` · CRUD `/admin/categories` · `GET/PATCH /admin/users` · `GET/PATCH /admin/corrections` · CRUD `/admin/announcements` · `PUT /admin/featured` |

Error format (everywhere): `{ "error": { "code": "validation_error", "message": "...", "fields": {...} } }`.

## 9. Security checklist (implemented across phases)
- Argon2id hashing; account lockout after repeated failures; generic login error messages.
- JWT in HttpOnly cookies + CSRF double-submit; short-lived access tokens; revocation on logout.
- Role decorator on every admin route; ownership checks on every user-owned resource (`WHERE user_id = current_user`).
- Marshmallow validation for all input; SQLAlchemy parameterised queries only (no string SQL).
- Uploads: extension + MIME + magic-byte check (PDF/JPEG/PNG/WebP), 5 MB limit, random filenames, stored outside static, `Content-Disposition` + `X-Content-Type-Options: nosniff` on download.
- Flask-Limiter on auth, AI, upload routes. Security headers (CSP, HSTS in prod, frame-deny).
- Secrets only via env vars; `.env` git-ignored; LLM key never sent to frontend.
- Structured logging without PII (no passwords, tokens, document contents).
- Password reset tokens stored hashed, single-use, 30-minute expiry.

## 10. Phase plan

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Architecture, sitemap, journeys, schema (models + initial migration), design direction | ✅ Done |
| 2 | Design system (SCSS tokens, components), logo/favicon, responsive landing page | ✅ Done |
| 3 | Auth (register/login/logout/refresh/reset/change password), RBAC, onboarding wizard | ✅ Done |
| 4 | Dashboard, discovery engine, detail page, saved/collections, compare, recommendations, demo seed | ✅ Done |
| 5 | Eligibility engine + Saathi AI (LLM adapter, structured explanations, chat history) | ✅ Done |
| 6 | Document vault + checklists, application tracker, calendar, reminders | ✅ Done |
| 7 | Admin panel: editor with rule builder, verification workflow + audit log, corrections, categories, users, announcements, featured, feedback | ✅ Done |
| 8 | Notifications + email + worker, security headers, tests (pytest on SQLite & PostgreSQL, Vitest, headless UI smoke test), Docker, Render blueprint, CI, GitHub Pages preview | ✅ Done |

### Preview build
`npm run build:preview` produces a browser-only build for GitHub Pages: `src/api/preview/server.js` implements the same
REST endpoints against `localStorage`/IndexedDB (with a JS mirror of the eligibility engine), routing uses hash URLs, and a
banner says so on every page. The normal build talks to Flask.

## 11. Data accuracy policy (enforced)
- **Real opportunities** enter the system only through the admin editor with an official `source_url`; they stay `pending_verification` until a reviewer verifies them.
- **Live data** is `shared/opportunities.json`: real opportunities checked against official sources (last on 25 Nov 2026), loaded with `flask seed-opportunities`. Sample data survives only as a test fixture and is never shown to users; `flask purge-demo` removes sample rows from older installs.
- The seed may include a directory of **official portals** (e.g. National Scholarship Portal, myScheme, National Career Service) as links only — no invented deadlines, amounts or eligibility.
- Opportunities whose deadline has passed are auto-marked `expired` and excluded from recommendations.
- We do not scrape; data comes from manual admin entry or officially permitted feeds.
