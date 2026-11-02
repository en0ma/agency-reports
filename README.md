# agency-reports

Agency-facing reports for Smart Roadways data, replacing the Tableau dashboards agencies use today. A React app and a
Django REST Framework API, reading the Smart Roadways gold tables.

The first report is **CMV Traffic Alerts**: how many alerts commercial motor vehicles received on an agency's
instrumented road segments. It has one panel so far, "Alerts per day".

> All data in this repo is synthetic. Locally, the Databricks SQL warehouse is replaced by a SQLite file built from
> the CSV files in `data/warehouse/`.

## Setup

Requires Python 3.10+ (3.12 recommended) and Node 22+.

PowerShell, from the repo root:

```powershell
npm install
npm run setup                      # creates backend/.env from backend/.env.example
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python manage.py load_warehouse    # builds data/warehouse.sqlite3 from the CSVs
cd ..
npm run dev
```

macOS / Linux: the same, with `source .venv/bin/activate` instead of `.venv\Scripts\Activate.ps1`.

`npm run dev` starts the API on :8000 and the web app on http://localhost:5173. Run it, and the other `npm` scripts that
touch the backend, from a shell where the virtual environment is active.

Pick who you're viewing as in the top-right corner. Agency users see one agency; the internal support user sees all of
them.

## Layout

```
backend/                  Django project
  agency_reports/           settings, URLs, validated env config (env.py)
  core/                     identity (stand-in sign-in), agency isolation, errors, request logging, report ranges
  warehouse/                read-only models over the gold tables + `load_warehouse` command
  cmv_alerts/               the CMV Traffic Alert report: queries.py, serializers.py, views.py, urls.py
  tests/                    pytest; runs the real queries against tests/fixtures/warehouse
frontend/                 React app (Vite)
  src/api/                  schema.d.ts is GENERATED from the backend; types.ts gives it friendly names
  src/lib/                  API client, data-loading hook, URL-backed filters, identity
  src/pages/                one page per report
data/warehouse/           schema.sql plus one folder of CSV part files per table
openapi.yaml              GENERATED from the Django serializers
```

## API

All data endpoints are read-only `GET`s under `/api/<report>/<panel>`, filtered by query parameters, and need an
`X-Demo-User` header (the stand-in for real sign-in).

- `GET /api/health`
- `GET /api/me`: the caller and the agencies they may see
- `GET /api/cmv-alerts/daily-alerts?agency=IN-DOT&range=30d`
- `GET /api/docs`: Swagger UI for the OpenAPI schema

```powershell
curl.exe -H "X-Demo-User: indiana.analyst" "http://localhost:8000/api/cmv-alerts/daily-alerts?agency=IN-DOT&range=7d"
```

## Commands

Run from the repo root, with the virtual environment active.

```sh
npm run dev         # API + web app with reload
npm test            # pytest + Vitest
npm run lint        # Biome (frontend) + Ruff (backend); npm run lint:fix to apply fixes
npm run typecheck   # tsc
npm run gen:api     # regenerate openapi.yaml and frontend/src/api/schema.d.ts after changing a serializer
npm run check       # everything above, and fails if the generated API files are out of date
```

After changing anything under `data/warehouse/`, rebuild the local warehouse with
`python manage.py load_warehouse` (from `backend/`).
