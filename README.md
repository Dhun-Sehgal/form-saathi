<div align="center">

<img src="frontend/public/favicon.svg" width="72" alt="FormSaathi logo" />

# FormSaathi

**Never Miss an Opportunity You Deserve.**

An AI-assisted opportunity discovery and application assistant for Indian students — and, next, job seekers and citizens.

**Discover → Check eligibility → Understand requirements → Prepare documents → Apply → Track**

[Live preview](https://anjalikokare.github.io/formsaathi/) · [Deploy the full app](#deploy-the-full-app) · [Architecture](docs/ARCHITECTURE.md) · [Database](docs/DATABASE.md) · [Design](docs/DESIGN.md)

</div>

---

## Two ways to see it

| | What it is | Data |
|---|---|---|
| **[Live preview (GitHub Pages)](https://anjalikokare.github.io/formsaathi/)** | The complete Vue app running **entirely in your browser** — a built-in mock of the API stores everything in `localStorage`/IndexedDB. Every page works: sign up, onboarding, discovery, eligibility, tracker, documents, calendar, admin panel. | Demo data only. Nothing leaves your browser. Saathi AI chat is off (no server). Admin login: `admin@formsaathi.demo` / `admin1234`. |
| **Full app (Flask + PostgreSQL)** | The real product: Flask REST API, PostgreSQL, secure cookie auth, private file storage, Saathi AI (with an API key), email (with SMTP). | Your database. Deploy with one click — see below. |

## Features

- **Discovery engine** — search, filters (category, education, state, income, deadline, my status, data origin), sorting, pagination, compare up to 3.
- **Explainable recommendations** — rule-based scoring with "why recommended" reasons; never recommends closed or not-eligible opportunities.
- **Eligibility engine** — deterministic, rule-by-rule check of admin-entered criteria: *Eligible / Possibly eligible / Not eligible*, with the official wording for each rule and what information is missing. **Rules decide, AI only explains.**
- **Saathi AI** — conversational guide in English, Hindi and Marathi, grounded in the opportunity's verified record, with chat history and suggested prompts. Clearly labelled *AI guidance — not official advice*.
- **Document vault** — private uploads (PDF/JPG/PNG/WebP, magic-byte checked), expiry tracking, per-opportunity checklists, downloadable checklists.
- **Application tracker** — board and list views, 8 statuses, user-confirmed history timeline, notes, reminders, application date and reference number.
- **Calendar** — deadlines, important dates, applied dates and reminders.
- **Notifications** — deadline, missing-document, status check-in and reminder notifications (deduplicated), in-app and email, with preferences.
- **Admin panel** — analytics, opportunity editor with structured eligibility-rule builder, verification workflow (verify → publish, audit log), corrections queue, categories, users & roles, announcements, featured listings, feedback.
- **Trust labels everywhere** — *Verified* / *Demo* / *Pending verification* / *Expired* / *AI guidance*. The **database itself** refuses to mark demo data as verified.
- **Polish** — responsive (tested at 360/390/768/1024/1440 px), dark mode, English/हिन्दी/मराठी UI, skeletons, empty and error states, toasts, accessible labels and focus states.
- **Privacy** — optional sensitive fields stay optional and are never sent to the AI; export all your data as JSON; delete your account and files.

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | Vue 3, Vite, Vue Router, Pinia, Bootstrap 5 (SCSS-themed), Lucide icons, vue-i18n |
| Backend | Python, Flask (Blueprints), SQLAlchemy 2, Flask-Migrate (Alembic), Marshmallow |
| Auth & security | Flask-JWT-Extended (HttpOnly cookies + CSRF), Argon2id, Flask-Limiter, security headers/CSP |
| Database | PostgreSQL (SQLite supported for quick local dev) |
| AI | Anthropic Claude via server-side adapter (`LLM_API_KEY`), structured outputs for explanations |
| Jobs | APScheduler worker / `flask run-jobs` |
| Tests | pytest (51 tests, run on SQLite **and** PostgreSQL), Vitest |
| Deploy | Docker → Render (blueprint), GitHub Pages (preview), GitHub Actions CI |

## Run it locally

**Requirements:** Python 3.12+ and Node 20+. PostgreSQL is optional for local development.

```bash
git clone https://github.com/anjalikokare/formsaathi.git
cd formsaathi

# 1) Backend
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows Git Bash: source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env                 # edit values; SQLite works out of the box
export FLASK_APP=wsgi.py             # PowerShell: $env:FLASK_APP="wsgi.py"
flask db upgrade                     # create tables
flask seed-reference                 # states, categories, document types
flask seed-demo                      # clearly-labelled DEMO opportunities
flask create-admin                   # prompts for an admin email + password
flask run                            # API on http://127.0.0.1:5000

# 2) Frontend (new terminal)
cd frontend
npm install
npm run dev                          # http://localhost:5173 (proxies /api to Flask)
```

Other useful commands:

```bash
python -m pytest                     # backend tests (set TEST_DATABASE_URL to test on PostgreSQL)
npm test                             # frontend unit tests
npm run build                        # production build, served by Flask from frontend/dist
npm run build:preview                # browser-only preview build (GitHub Pages)
flask run-jobs                       # expire past deadlines + generate notifications
python -m app.worker                 # run those jobs every 30 minutes
flask purge-demo                     # remove all demo opportunities before a real launch
```

## Configuration

All secrets come from environment variables — see [`backend/.env.example`](backend/.env.example).

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL URL (`postgres://…` is accepted) or `sqlite:///file.db` |
| `SECRET_KEY`, `JWT_SECRET_KEY` | Long random strings. Production refuses to start without them. |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | Optional: admin account created on startup |
| `LLM_API_KEY` (`LLM_MODEL`) | Enables Saathi AI and AI-written eligibility explanations. Without it, AI features say "not configured" and eligibility uses rule-based explanations. |
| `SMTP_*`, `MAIL_FROM` | Enables email. Without it, emails are logged and the UI says email isn't configured. |
| `FRONTEND_URL` | Base URL used in password-reset emails |
| `UPLOAD_DIR`, `MAX_UPLOAD_MB` | Private document storage location and size limit |
| `COOKIE_SECURE` | `true` behind HTTPS (default in production) |
| `SEED_DEMO` | Docker start script loads demo data when `true` (default) |

## Deploy the full app

The repository includes a Dockerfile and a [Render Blueprint](render.yaml) (one web service + one PostgreSQL database).

1. Open **https://render.com/deploy?repo=https://github.com/anjalikokare/formsaathi** and sign in to Render (you can sign in with GitHub).
2. Fill in `ADMIN_EMAIL` and `ADMIN_PASSWORD` (your admin login). Optionally add `LLM_API_KEY` for Saathi AI, and set `FRONTEND_URL` to your service URL once you know it.
3. Click **Apply**. Render builds the Docker image, creates the database, runs migrations, loads reference + demo data and creates your admin account.

Notes on free hosting plans: free web services sleep when idle (the first request takes a little while), free databases have plan limits — check Render's current terms — and the container's disk is not persistent, so **uploaded documents are lost on redeploy/restart**. For real users, attach a persistent disk or object storage (see `app/services/storage.py`) and add a cron service that runs `flask run-jobs`.

The same Docker image runs on any container host (Railway, Fly.io, a VPS). It needs `DATABASE_URL`, `SECRET_KEY` and `JWT_SECRET_KEY`.

## Data accuracy policy

- Real opportunities enter only through the admin editor with an **official source URL**, stay *Pending verification* until a reviewer verifies them, and must be verified before they can be published.
- All sample listings are **Demo** data: fictional organisations, `example.org` links, never verifiable (a database CHECK constraint enforces this).
- Opportunities past their deadline are automatically marked expired and never recommended.
- No scraping. The footer and About page link to official portals (National Scholarship Portal, myScheme, National Career Service, …) as links only.
- AI output is always labelled and never presented as official advice.

## Project structure

```
backend/      Flask API — app/api (blueprints), app/models, app/services (eligibility, catalog, llm, notify, storage, mailer),
              app/seed, migrations/, tests/
frontend/     Vue app — src/views (public, auth, app, admin, shared), src/components, src/layouts,
              src/api (HTTP client + browser-only preview server), src/stores, src/i18n, src/styles
shared/       reference.json + demo_data.json used by both the backend seed and the preview build
docs/         ARCHITECTURE.md, DATABASE.md, DESIGN.md
```

## Known limitations

- The UI chrome (navigation, key headings, buttons) is translated into Hindi and Marathi. Long-form page copy and opportunity content are in English; Saathi AI can explain them in Hindi or Marathi.
- Saathi AI and email need their keys configured; the preview build has no AI.
- Legal pages are plain-language templates and should be reviewed by a lawyer before a public launch.
- In-memory rate limiting is per process; use Redis (`RATELIMIT_STORAGE_URI`) when running several instances.

## Disclaimer

FormSaathi is an independent guide and is not affiliated with any government body. Always confirm details on the official source before applying.
