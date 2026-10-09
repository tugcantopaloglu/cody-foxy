# Cody Foxy

Cody Foxy is a FastAPI and Next.js application for scanning source archives and GitHub repositories with Semgrep and Bandit. It stores findings in PostgreSQL and can add AI explanations and SARIF exports.

## Run locally

```bash
cp .env.example .env
docker compose up --build -d
```

Configure a long random `SECRET_KEY` in `.env` before using accounts. Without an explicit key, development generates a process-local value and tokens become invalid after restart. Use one worker for that development mode. Production requires a stable shared secret and private PostgreSQL and Redis services.

The dashboard is available at `http://localhost:3000`. Use Sign In to create an account or sign in before creating scans. API endpoints are documented at `http://localhost:8000/docs`.

## Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1
```

Set `DATABASE_URL` to a PostgreSQL async URL and provide `SECRET_KEY` before starting the API. The current application creates its schema during startup. Review database changes before using an existing installation.

```bash
cd frontend
npm ci
npm run dev
```

The frontend uses Next.js 15 and the existing React 18 component structure. AI and GitHub OAuth require their own credentials. The test suite does not contact those external services.

## Scan access

Scan creation, details, findings, listing, and SARIF require Bearer authentication. Lists are restricted to the current owner. Missing, foreign-owner, and legacy anonymous scans return the same 404 response to an authenticated caller. Legacy anonymous records do not become public or automatically acquire an owner.

Team and project details require ownership or membership. Live scan subscriptions require authentication and owner access; broadcasts are scoped to the scan owner's connections. WebSocket clients can send a Bearer header or a token query parameter. Avoid logging token-bearing URLs.

Uploads accept ZIP and gzip-compressed TAR archives. Uploaded and expanded content is limited by `MAX_FILE_SIZE`. Unsafe archive paths are rejected. GitHub clones accept HTTPS URLs on `github.com`; credentials are not retained in the clone's origin URL. Operate only on code you are authorized to inspect.

## Verification

```bash
cd backend
python -m pytest tests -q
python -m bandit -r app -lll
```

```bash
cd frontend
npm run build
npm test -- --runInBand
```

Backend regressions use SQLite to verify owner isolation, anonymous denial, project access, account registration/login, archive upload, and WebSocket scoping. Frontend tests and a production build verify the existing components and sign-in page compilation. CI also builds container images without deploying them.

The Python dependencies were audited after the JWT migration. The frontend still has high and moderate dependency advisories requiring further compatibility work; a passing test/build or high severity Python gate does not establish that the whole application is vulnerability-free. Live PostgreSQL migrations, GitHub OAuth, external AI, scanner binaries, and production deployment require separate acceptance.
