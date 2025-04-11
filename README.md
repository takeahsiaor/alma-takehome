# alma-takehome

This is a FastAPI-based backend application for managing lead intake and resume submissions. It supports:

- Public lead form submissions
- Email notifications to prospects and attorneys
- Internal API with user authentication and lead management
- SQLite-backed persistence
- User authentication via hashed passwords
- Automatic seeding and migrations via Makefile

---

## Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/takeahsiaor/alma-takehome.git
cd alma-takehome
```

### 2. Install & Run
```bash
make install       # Set up virtual environment, install deps, run migrations, seeds the DB with a default internal user
make run           # Start the FastAPI server at http://localhost:8000
```
Then visit http://localhost:8000/docs for the Swagger UI.

## Make Commands

|Command       | Description |
| make install | Creates a venv/alma virtual environment, installs packages, and runs DB migrations |
| make run     | Runs the FastAPI app using Uvicorn (http://localhost:8000)|
| make migrate |    Applies any new Alembic database migrations|
| make seed-users|  Seeds the database with a hardcoded internal user (attorney)|
| make uninstall |  Deletes the SQLite DB and removes the virtual environment|
| make test | Runs tests|


## Internal User Access
After seeding users, you can authenticate against the internal API using:

Email: attorney1@alma.com
Password: supersecure

Use the /internal/token endpoint to retrieve a JWT access token.

## Tech Stack
- FastAPI
- SQLite (via SQLAlchemy ORM)
- Alembic (for migrations)
- Passlib (for password hashing)
- Uvicorn (ASGI server)
- Make (for developer convenience)
- Pytest for testing

## Directory Overview
```bash
.
├── app/                # Application code
├── scripts/            # Dev scripts like seed_users.py
├── alembic/            # Migrations
├── venv/               # Virtual environment (auto-created)
├── leads.db            # SQLite database
├── Makefile            # Commands for local development
└── requirements.txt    # Python dependencies
```

## Run tests
```bash
make test
```

## Uninstall Everything
To remove your local environment and DB, run:

```bash
make uninstall
```