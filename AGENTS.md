# AGENTS.md

Notes for coding agents working in this repo. See README.md for setup and layout.

## Commands

- `npm run check` must pass before you call work done (lint, typecheck, tests, generated API files up to date).
- Backend only: `cd backend && python -m pytest`. Frontend only: `npm test -w frontend`.
- The Python commands need the virtual environment in `backend/.venv` to be active.

## Conventions

- API contracts come from the DRF serializers. After adding or changing one, run `npm run gen:api` and commit
  `openapi.yaml` and `frontend/src/api/schema.d.ts`. Never edit those two files by hand.
- One Django app per report. One view per panel, registered in that app's `urls.py`, each starting with
  `_report_window(request)`, which validates the query, checks agency access and resolves the date window.
- Queries live in the report's `queries.py` and aggregate in the database (`.values().annotate()`). Never pull raw
  alert rows into Python.
- Call `assert_agency_access(request, agency)` before any query that takes an agency.
- Frontend components never call `fetch`; add a typed function to `frontend/src/lib/api.ts` and load it with
  `useApiData`.
- Never read, print or paste the contents of `backend/.env`.
