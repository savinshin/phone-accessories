# Phone Accessories project instructions

## Project

* Repository: `phone-accessories`
* Product type: promotional website + online catalog for mobile phone accessories.
* This is not an online store.
* MVP does not include cart, checkout, online payments, customer accounts, delivery management, Android application, iOS application, or Telegram bot.

## Stack

* Backend:

  * Python 3.14
  * Django 6
  * Django REST Framework
  * PostgreSQL 18
  * psycopg
  * python-dotenv
* Frontend:

  * Angular
  * Tailwind CSS
  * SSR/SSG enabled
* Infrastructure:

  * Docker
  * Docker Compose

## Repository structure

```text
phone-accessories/
├── backend/              # Django + DRF backend
│   ├── catalog/
│   ├── config/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── manage.py
│   └── requirements.txt
├── web/                  # Angular frontend
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── angular.json
│   ├── package.json
│   └── package-lock.json
├── compose.yaml
├── .env.example
├── .gitignore
├── AGENTS.md
└── README.md
```

## Local development

The project is expected to run through Docker Compose.

Main setup commands:

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend python manage.py migrate
```

Current services:

* `db` — PostgreSQL
* `backend` — Django + DRF
* `web` — Angular dev server

The backend is available on:

```text
http://127.0.0.1:8000/
```

The frontend is available on:

```text
http://127.0.0.1:4200/
```

Current health check:

```text
/api/health/
```

Backend direct check:

```bash
curl http://127.0.0.1:8000/api/health/
```

Frontend proxy check:

```bash
curl http://127.0.0.1:4200/api/health/
```

Both should return:

```json
{"status":"ok"}
```

## Core working rules

* Work strictly according to the task.
* Do not write code by assumption.
* Do not add refactoring, cleanup, optimizations, UX improvements, or architecture changes unless explicitly requested.
* Do not add defensive checks, fallbacks, broad try/catch blocks, null-guards, or alternative flows unless confirmed by current code, schema, API contract, or runtime behavior.
* If confidence is insufficient, first identify what file, model, migration, API contract, schema, or runtime check is missing.
* Prefer small focused changes over large rewrites.
* Keep the solution aligned with the current project stage and MVP scope.

## Git rules

Do not run these commands unless explicitly asked:

* `git add`
* `git commit`
* `git push`
* `git pull`
* `git fetch`
* `git merge`
* `git rebase`
* `git checkout`
* `git switch`
* branch creation or deletion commands

Allowed read-only Git commands:

* `git status`
* `git diff`
* `git diff --check`
* `git log --oneline -n ...`
* `git branch --show-current`

## Commands allowed without additional confirmation

Read-only inspection commands are allowed when needed:

```bash
ls
find
grep
rg
cat
sed -n
git status
git diff
git diff --check
git log --oneline -n ...
git branch --show-current
docker compose ps
docker compose logs <service> --tail=100
```

Safe targeted checks are allowed:

```bash
docker compose exec backend python manage.py check
curl http://127.0.0.1:8000/api/health/
curl http://127.0.0.1:4200/api/health/
```

## Commands that require explicit confirmation

Ask before running commands that change dependencies, database state, containers, cache, or generated output:

```bash
docker compose up
docker compose up -d
docker compose up -d --build
docker compose down
docker compose down -v
docker compose build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py createsuperuser
python manage.py migrate
python manage.py makemigrations
pip install ...
python -m pip install ...
npm install
npm ci
npm update
npm audit fix
npm run build
npm test
ng test
ng build
```

Do not create, modify, or run tests unless the task explicitly requires it.

## Backend conventions

* Keep Django views thin.
* API views should handle request/response only.
* Put business logic into services/selectors/repositories when logic becomes non-trivial.
* Follow nearby Django/DRF style before introducing new patterns.
* API routes should live under `/api/`.
* App-level routes should be placed in the app `urls.py` and included from `config/urls.py`.
* Use Django REST Framework for API endpoints.
* Do not invent a custom API response wrapper unless the project explicitly introduces one.
* Current minimal API response style uses DRF `Response`.

## Backend environment

* Root `.env` is used for local environment variables.
* `.env` must not be committed.
* `.env.example` must stay safe to commit.
* Backend reads environment variables from the root `.env`.
* In local non-Docker mode, PostgreSQL host may be `localhost`.
* In Docker Compose, backend uses `POSTGRES_HOST=db`.
* `DJANGO_ALLOWED_HOSTS` must include `backend` because the Angular dev proxy calls Django through the Docker service name.

## Database and migrations

* Database is PostgreSQL.
* Do not edit old migrations that may already be applied.
* Create new migrations only when schema changes are required.
* Before adding a field, check whether it already exists in models, migrations, serializers, admin, frontend interfaces, or API usage.
* Do not add duplicate fields under new names.
* Do not run migrations without explicit confirmation.

## Files and images

* Product images and uploaded files should be designed with future S3-compatible storage in mind.
* Do not hard-code local-only file assumptions.
* Do not build file/image logic around direct local filesystem paths unless explicitly confirmed.
* Prefer Django storage abstraction for file-related code.
* Do not add production media/storage configuration without a specific task.

## Frontend conventions

* Use Angular standalone components.
* Prefer `ChangeDetectionStrategy.OnPush`.
* Prefer signals for local state where appropriate.
* Prefer reactive forms for forms.
* Use Angular control flow syntax such as `@if` and `@for`.
* Keep TypeScript and templates strict.
* Use Tailwind CSS for layout and styling.
* Do not introduce custom design tokens, UI libraries, or global styling systems without confirmation.
* Keep component styles minimal unless the component really needs local styling.

## Frontend architecture

Preferred structure for future features:

```text
web/src/app/
├── core/
├── features/
│   └── <feature>/
│       ├── data-access/
│       ├── ui/
│       └── pages/
└── shared/
```

Use this as a direction, but do not restructure the project unless the task requires it.

## Frontend/backend communication

* Frontend should call backend through relative `/api/...` URLs.
* Do not hard-code `http://backend:8000` or `http://127.0.0.1:8000` in Angular application code.
* In development, Angular uses `web/src/proxy.conf.json`.
* Docker target for the proxy is:

```text
http://backend:8000
```

## MVP scope

The MVP may include:

* promotional landing page
* product catalog
* product detail page
* product categories
* product availability
* product images
* contact/social links
* admin management through Django Admin

The MVP does not include:

* shopping cart
* checkout
* online payments
* customer registration
* customer account
* delivery management
* complex CRM/admin dashboard
* Android application
* iOS application
* Telegram bot

## Before finishing a task

Always provide:

* changed files
* short summary of changes
* checks that were run
* checks that were not run, if relevant
* any assumptions or missing confirmations