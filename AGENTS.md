# Phone Accessories project instructions

## 1. Project and stack

Repository: `phone-accessories`.

Goal: a full-featured e-commerce store for electronics and accessories, built as a portfolio/commercial-ready project that can later be transferred to a real client.

Backend:
- Python 3.14
- Django 6
- Django REST Framework
- PostgreSQL 18
- psycopg
- python-dotenv

Frontend:
- Angular
- Tailwind CSS
- SSR/SSG

Infrastructure:
- Docker
- Docker Compose

Current structure:
- `backend/accounts/` — users and authentication
- `backend/catalog/` — catalog
- `backend/config/` — Django configuration
- `web/` — Angular frontend
- `compose.yaml` — db/backend/web
- `.env.example` — environment template
- `.env` — local environment, never committed
- `README.md` — setup commands
- `AGENTS.md` — Codex instructions

## 2. Local development

The primary local workflow uses Docker Compose.

Setup:

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend python manage.py migrate
```

Create a local administrator when needed:

```bash
docker compose exec backend python manage.py createsuperuser
```

Services:
- `db` — PostgreSQL
- `backend` — Django + DRF
- `web` — Angular dev server

Endpoints:
- Backend: `http://127.0.0.1:8000/`
- Frontend: `http://127.0.0.1:4200/`
- Admin: `http://127.0.0.1:8000/admin/`

Health checks:
- `http://127.0.0.1:8000/api/health/`
- `http://127.0.0.1:4200/api/health/`

Both must return:

```json
{"status":"ok"}
```

## 3. Core working rules

- Work strictly within the current task.
- Do not write code based on assumptions.
- If a proposed solution is technically weak, point out the problem and recommend the better option instead of agreeing automatically.
- Do not add unrelated refactoring, optimization, UX changes, architecture changes, entities, or scenarios.
- Do not add fallbacks, broad try/catch blocks, null guards, defensive logic, or alternative flows unless justified by current code, schema, API contract, or runtime behavior.
- If a model, migration, serializer, frontend type, API contract, or runtime verification is missing, identify the missing information first.
- Prefer focused changes over broad rewrites.
- Keep the project extensible and professional without premature overengineering.
- Before implementing significant domain entities, first define tables, fields, relationships, nullable/required rules, unique constraints, indexes, and database constraints.

## 4. Commands and checks

Do not run without explicit user approval:
- `git add`
- `git commit`
- `git push`
- `git pull`
- `git fetch`
- `git merge`
- `git rebase`
- `git checkout`
- `git switch`
- `pip install`
- `python -m pip install`
- `npm install`
- `npm ci`
- `npm update`
- `npm audit fix`
- migrations
- makemigrations
- Docker commands that change container state
- tests or test modifications

Allowed read-only/safe checks:
- `ls`
- `find`
- `grep`
- `rg`
- `cat`
- `sed`
- `git status`
- `git diff`
- `git diff --check`
- `git log`
- `git branch --show-current`
- `docker compose ps`
- `docker compose logs <service> --tail=100`
- `docker compose exec backend python manage.py check`
- health endpoint `curl` checks

Commands that create files inside the backend bind mount, such as `startapp` or `makemigrations`, should be run as the host UID/GID when needed:

```bash
docker compose exec --user "$(id -u):$(id -g)" backend ...
```

This avoids creating root-owned source files on the host.

After changes, briefly report:
- changed files
- what was implemented
- what was checked
- what was not checked

## 5. Backend conventions

Keep Django views thin:

`request -> service/use-case when necessary -> Response`

Do not introduce services/selectors/repositories for trivial CRUD. Add them only when business logic becomes non-trivial.

Rules:
- API endpoints live under `/api/`.
- App routes live in app-level `urls.py`.
- App routes are included from `config/urls.py`.
- Use Django REST Framework.
- Current minimal API response format is DRF `Response`.
- Do not introduce a custom response wrapper without a separate decision.
- Follow the style of neighboring code.

## 6. Users and Admin

The project uses a custom user model:

`accounts.User`

It is based on `AbstractUser`.

Current rules:
- `username` is disabled
- `email` is `USERNAME_FIELD` and login identifier
- `phone` is added
- email is case-insensitive unique
- standard Django Groups and Permissions are used
- do not create separate `Admin`, `Manager`, or `Role` models unless there is a concrete requirement

Configured setting:

```python
AUTH_USER_MODEL = 'accounts.User'
```

Staff and administrators are regular `User` records using:
- `is_staff`
- `is_superuser`
- groups
- permissions

Use Django Admin for internal management.

Do not create a separate Angular admin panel without a specific task.

The custom user schema is defined by `accounts.0001_initial`.

## 7. Database and migrations

Database: PostgreSQL.

Rules:
- Do not modify old migrations that may already have been applied.
- Schema changes require new migrations.
- Before adding a field, check models, migrations, serializers, admin, frontend types, and API usage.
- Do not create duplicate fields under different names.
- Migration files are part of the project schema and must be committed.
- A new developer runs `migrate`, not `makemigrations`.
- Resetting the development database must be an explicit, intentional operation.

## 8. Catalog architecture

Do not create separate `Phone`, `Laptop`, or `Accessory` tables.

The catalog must use a universal product model.

Planned catalog entities:
- `Category`
- `Brand`
- `Product`
- `ProductCategory`
- `ProductVariant`
- `Attribute`
- `AttributeOption`
- `CategoryAttribute`
- `ProductAttributeValue`
- `VariantAttributeValue`
- `ProductMedia`
- `Stock`
- `ProductCompatibility`

Core rules:
- `Product` represents the product model.
- `ProductVariant` represents a concrete sellable SKU.
- Price belongs to `ProductVariant`.
- Stock belongs to `ProductVariant`.
- Do not model product characteristics as fixed columns such as `processor`, `battery`, `material`, etc.
- Use an extensible attribute system.
- Do not store primary filterable characteristics in a single JSON field without a separate architecture decision.
- `Category` must support hierarchy.

Before implementing each group of catalog models, agree on the ER schema first.

## 9. E-commerce direction

The project is intended to become a complete online store.

Future domains include:
- cart
- checkout
- registered customers
- guest checkout
- orders
- addresses
- payments
- delivery/shipping
- discounts/coupons when required

Do not create these entities before their dedicated design stage.

Important domain rules:
- `CartItem` must reference `ProductVariant`.
- `OrderItem` must reference `ProductVariant`.
- Order history must preserve snapshots of important data.
- Later changes to product name, price, variant data, or customer address must not alter historical orders.
- Payment and shipment models must not be coupled to a specific provider before a real provider is selected.

## 10. Files and images

Do not store image binary data in PostgreSQL.

Use Django `ImageField`/`FileField` and the Django Storage abstraction.

Database stores:
- storage path/key
- metadata

Physical files live in storage.

Production direction:
- S3-compatible object storage

Rules:
- Do not rely on direct local filesystem paths.
- Do not use Google Drive URLs as primary production storage.
- Google Drive may be used later only as an import source if required.
- Do not add production S3 configuration without a dedicated task.

## 11. Frontend conventions

Angular conventions:
- standalone components
- `ChangeDetectionStrategy.OnPush`
- signals for local state where appropriate
- reactive forms
- `@if` / `@for`
- strict TypeScript/templates
- Tailwind CSS
- minimal component CSS

Do not introduce UI libraries, design systems, or custom design tokens without a project decision.

Preferred direction:

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

Do not restructure existing code only to match this layout.

## 12. Frontend/backend communication

Angular must call backend APIs through relative `/api/...` paths.

Do not hard-code in Angular application code:
- `http://backend:8000`
- `http://127.0.0.1:8000`
- `localhost:8000`

Development proxy:

```text
web/src/proxy.conf.json
```

Docker proxy target:

```text
http://backend:8000
```

`DJANGO_ALLOWED_HOSTS` must include `backend`.

## 13. Scope control

If a change is outside the current task, mention it separately and do not include it without approval.

When multiple approaches exist:
1. recommend the best option for the current project stage;
2. briefly explain why;
3. do not implement alternatives unless requested.

Balance clean architecture, best practices, and future extensibility without adding unnecessary complexity too early.
