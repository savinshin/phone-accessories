# Phone Accessories

## ENV

```bash
cp .env.example .env
```

## Docker

```bash
docker compose up -d --build
```

```bash
docker compose exec backend python manage.py migrate
```

## Admin

```bash
docker compose exec backend python manage.py createsuperuser
```

## Chech backend:

http://127.0.0.1:8000/

## Chech frontend:

http://127.0.0.1:4200/

## Chech health endpoints:

Backend:

http://127.0.0.1:8000/api/health/

Frontend:

http://127.0.0.1:4200/api/health/

## Codex tools

### Angular CLI MCP:

```bash
codex mcp list
```

### Impeccable:

```bash
npx impeccable install --providers=codex --scope=project
```

### Playwright CLI:

```bash
npm install -g @playwright/cli@latest
playwright-cli install --skills=agents
playwright-cli install-browser chrome
```
