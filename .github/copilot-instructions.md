# Copilot instructions for Daily News

## Repository shape

The active application is a full-stack news aggregator:

- `backend/` contains the FastAPI application. `backend/app/main.py` creates the app, configures CORS and global error responses, initializes the database during lifespan startup, and mounts the versioned router.
- `backend/app/api/v1/` contains thin HTTP route modules for auth, news, bookmarks, preferences, profile, health, and protected internal refresh endpoints.
- `backend/app/db/models/` contains SQLAlchemy 2.x models and enums. `backend/app/db/repositories/` owns database queries and persistence.
- `backend/app/services/` contains business workflows: authentication, news-provider adapters, Gemini analysis, ingestion, and recommendations.
- `backend/app/schemas/` contains the Pydantic request and response contracts used by the API.
- `api/index.py` is the Vercel Python entrypoint; it adds `backend/` to `sys.path` and imports `app.main:app`.
- `frontend/` is a React 19 + TypeScript + Vite app. UI components live under `frontend/src/components`, shared state under `frontend/src/context`, API wrappers under `frontend/src/services/api`, and shared contracts under `frontend/src/types`.
- `vercel.json` rewrites `/api/*` to `api/index.py`, serves the built frontend from `frontend/dist`, and schedules `/api/v1/internal/refresh-news` every 15 minutes.

The root `README.md` describes an older Django/template-based layout. For current implementation work, use the checked-in `backend/`, `api/`, `frontend/`, and `vercel.json` structure as the source of truth.

## Build, test, and lint commands

Run backend commands from `backend\` with the backend virtual environment active:

```powershell
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
python -m pytest
python -m pytest tests\test_example.py -k test_name
ruff check app tests
mypy app
```

There are currently no tracked test modules under `backend/tests/`; the targeted pytest form above is the pattern to use when tests are added. Backend settings are loaded from `backend/.env` through Pydantic Settings. Required runtime integrations include a PostgreSQL-compatible `DATABASE_URL` or database component variables, a news-provider key, Gemini configuration, JWT/session secrets, and CORS settings; use `.env.example` as the variable reference and never commit real values.

Run frontend commands from `frontend\`:

```powershell
npm ci
npm run dev
npm run build
npm run lint
```

The frontend currently has no test runner script or tracked frontend tests. `npm run build` performs TypeScript project compilation (`tsc -b`) before the Vite production build. ESLint ignores `dist/`.

## Architecture and request flow

The frontend calls `/api/v1` by default through `frontend/src/services/api/client.ts`; `VITE_API_BASE_URL` can override that base. The client reads the access token from `localStorage` key `daily_news_token`, sends it as a Bearer token, and normalizes non-2xx responses into an `ApiError`. Keep endpoint paths and response types aligned between the API wrappers and `backend/app/api/v1/` schemas.

FastAPI routes depend on `get_db()` from `backend/app/db/session.py`. Each request gets an async SQLAlchemy session, commits on success, rolls back on exceptions, and closes in `finally`. Route handlers should validate input and coordinate a repository or service rather than embedding query logic. Add database reads/writes to the appropriate repository and use Pydantic response models with `from_attributes` for ORM results.

Authentication uses Argon2 password hashes and signed access/refresh JWTs from `backend/app/core/security.py`. Use `get_current_user_id` for required access-token routes, `get_optional_user_id` for public routes that personalize results, and `require_cron_secret` for maintenance endpoints. Do not expose password hashes, token contents, provider keys, or internal exception details in API responses.

News ingestion is an adapter pipeline: the configured provider from `settings.NEWS_API_PROVIDER` is created by `get_news_provider()`, raw articles are normalized to `RawNewsArticle`, URLs and external IDs are checked for duplicates, Gemini enriches each article (with a deterministic fallback when unavailable), and `NewsArticle` plus `RefreshLog` records are persisted. Provider-specific category mappings belong in the provider adapter; cross-provider normalization belongs in the common base/service layer.

## Codebase conventions

- Preserve the async boundary: use `AsyncSession`, async repository methods, `httpx.AsyncClient`, and `await` throughout backend request, provider, and ingestion paths.
- Keep API versioning and router registration centralized in `backend/app/api/v1/__init__.py`; add new route modules there with an explicit prefix and tag.
- Use `settings`/`get_settings()` for environment configuration instead of reading `os.environ` directly. Add new variables to both `backend/app/core/config.py` and `.env.example` when appropriate.
- Keep external API integrations behind service/provider classes. Normalize provider payloads before they reach persistence or API response code.
- Use the existing centralized exception handlers in `backend/app/main.py`; raise `HTTPException` for expected HTTP failures and let unexpected failures be logged and converted to the standard internal-error response.
- Reuse the repository layer for database access and preserve the session transaction behavior. Model changes should maintain UUID identifiers, timezone-aware datetimes, SQLAlchemy relationships, uniqueness constraints, and useful indexes.
- Keep article category and sentiment values consistent with the enums in `backend/app/db/models/` and the corresponding Pydantic schemas. Clamp or validate bounded scores through schema/model constraints rather than ad hoc frontend checks.
- Keep frontend API calls in `frontend/src/services/api/`, shared API shapes in `frontend/src/types/`, and presentational behavior in components. Avoid duplicating fetch/token/error handling inside individual components.
- Follow the existing frontend design system: compose the primitives under `frontend/src/components/ui/`, use the `ThemeContext` and `ToastContext` providers for cross-cutting UI state, and use Tailwind utility classes alongside the existing CSS variables/classes rather than introducing a second styling system.
- TypeScript is configured with strict unused-code checks (`noUnusedLocals`, `noUnusedParameters`) and bundler resolution. Keep imports type-only where appropriate and ensure new code passes `npm run build` and `npm run lint`.
- Internal refresh routes are protected by `X-Cron-Secret` or `cron_secret` and are the target of the Vercel cron. Preserve that protection when changing scheduled ingestion behavior.
