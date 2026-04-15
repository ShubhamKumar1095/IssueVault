# ResolveHub

ResolveHub is a modular issue-intelligence MVP built with Streamlit and SQLite.  
It keeps UI, business logic, and persistence separated so services can be moved to FastAPI later.

## Tech Stack

- Python 3.11+
- Streamlit
- SQLite
- Pandas
- Plotly
- scikit-learn

## Architecture

- `pages/`: Streamlit presentation layer
- `services/`: business logic
- `repositories/`: SQL/data access only
- `models/`: enums and schema dataclasses
- `db/`: SQLite connection + bootstrap
- `utils/`: validation, auth, session, file storage helpers
- `sql/`: SQLite schema + seed scripts

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Create `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
4. Run app:
   ```powershell
   python -m streamlit run app.py
   ```

The app auto-initializes `SQLITE_DB_PATH` on first run and executes:
- `sql/schema.sql`
- `sql/seed_data.sql`

## Seed Login

- `end_user_1`
- `support_1`
- `consultant_1`
- `manager_1`
- `admin_1`

Password for all: `Password@123`

## Performance Improvements Included

- SQLite tuned with WAL + optimized PRAGMAs
- Automatic local DB bootstrap (no external DB/network latency)
- Streamlit data caching on metadata, queues, issue detail bundles, and dashboard payloads
- Query limits and indexed filter paths for faster search and page loads
