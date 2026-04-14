# IssueVault

IssueVault is a production-structured starter MVP for issue intelligence and reusable resolution memory. It is designed so Streamlit handles presentation only while services/repositories encapsulate backend logic that can later be moved to FastAPI.

## Tech Stack

- Python 3.11+
- Streamlit
- Oracle Database
- `oracledb` (python-oracledb)
- Pandas
- Plotly
- scikit-learn

## Architecture

- `pages/`: Streamlit UI pages only
- `services/`: business rules and orchestration
- `repositories/`: database access only
- `models/`: enums and typed schemas
- `db/`: Oracle connection pooling
- `utils/`: validation, security, session and storage helpers
- `sql/`: Oracle schema and seed scripts

## Project Tree

```text
IssueVault/
├── .env.example
├── app.py
├── config.py
├── README.md
├── requirements.txt
├── db/
│   ├── oracle_pool.py
│   └── __init__.py
├── models/
│   ├── enums.py
│   ├── schemas.py
│   └── __init__.py
├── pages/
│   ├── 1_Submit_Issue.py
│   ├── 2_Search_Issues.py
│   ├── 3_My_Issues.py
│   ├── 4_Support_Desk.py
│   ├── 5_Dashboard.py
│   └── 6_Admin.py
├── repositories/
│   ├── analytics_repository.py
│   ├── attachment_repository.py
│   ├── base_repository.py
│   ├── comment_repository.py
│   ├── issue_repository.py
│   ├── resolution_repository.py
│   ├── user_repository.py
│   └── __init__.py
├── services/
│   ├── admin_service.py
│   ├── auth_service.py
│   ├── dashboard_service.py
│   ├── issue_service.py
│   ├── resolution_service.py
│   ├── search_service.py
│   ├── similarity_service.py
│   └── __init__.py
├── sql/
│   ├── schema.sql
│   └── seed_data.sql
└── utils/
    ├── exceptions.py
    ├── file_storage.py
    ├── security.py
    ├── session.py
    ├── validators.py
    └── __init__.py
```

## Local Setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` from template:
   ```bash
   cp .env.example .env
   ```
   On Windows PowerShell:
   ```powershell
   Copy-Item .env.example .env
   ```
4. Update Oracle credentials in `.env`.
5. Run DB scripts in order:
   - `sql/schema.sql`
   - `sql/seed_data.sql`
6. Start the app:
   ```bash
   streamlit run app.py
   ```

## Seeded Users

- `end_user_1`
- `support_1`
- `consultant_1`
- `manager_1`
- `admin_1`

Password for all seeded users: `Password@123`

## Oracle Notes

- Normalized tables with identity primary keys.
- Required indexes implemented for title/error/module/severity/status/created/assigned filters.
- Status history, comments, links, attachments, resolutions, feedback, and knowledge memory entities included.

## MVP Highlights

- Structured issue submission with attachment upload (local disk + Oracle metadata)
- Similar issue detection (TF-IDF + structured boosts)
- Full issue lifecycle status history
- Resolution memory with root cause/workaround/final fix/steps
- Role-based access controls (end_user, support_analyst, consultant, manager, admin)
- Search/filter and dashboard analytics via repository queries
