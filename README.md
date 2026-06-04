# Library Catalog API

REST API for managing a library book catalog.  
Built with FastAPI, SQLAlchemy (async), PostgreSQL, and JWT authentication.

## Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.136 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt |
| HTTP client | httpx |
| Validation | Pydantic v2 |
| Build | Poetry / pip |

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (for the database)

## Setup

### Option A — Poetry (recommended)

```bash
# Install Poetry if you don't have it
pip install poetry

# Install all dependencies (including dev)
poetry install

# Activate the virtual environment
poetry shell
```

### Option B — pip

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install from the pinned lockfile
pip install -r requirements.txt
# or as an editable install with dev extras
pip install -e ".[dev]"
```

### After installing

```bash
# Start PostgreSQL
docker-compose up -d

# Copy and fill in the environment file
cp .env.example .env
```

### `.env` variables

```dotenv
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/library_catalog
JWT_SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running

```bash
# Apply migrations
alembic upgrade head

# Start the development server
make run
# or manually:
uvicorn library_catalog.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive docs: `http://localhost:8000/docs`

## API

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Obtain JWT access token |

### Books

| Method | Path | Description | Auth required |
|---|---|---|---|
| `GET` | `/api/v1/books/` | List books (filters + pagination) | — |
| `GET` | `/api/v1/books/{id}` | Get book by ID | — |
| `POST` | `/api/v1/books/` | Create book (enriched via Open Library) | User |
| `PATCH` | `/api/v1/books/{id}` | Partially update book | User |
| `DELETE` | `/api/v1/books/{id}` | Delete book | Admin |

#### Query parameters for `GET /api/v1/books/`

| Parameter | Type | Description |
|---|---|---|
| `title` | string | Case-insensitive partial match |
| `author` | string | Case-insensitive partial match |
| `genre` | string | Exact match |
| `year` | integer | Exact match |
| `available` | boolean | Filter by availability |
| `page` | integer | Page number (default: 1) |
| `page_size` | integer | Items per page, 1–100 (default: 20) |

## Authentication

```
POST /api/v1/auth/register  →  { id, email }
POST /api/v1/auth/login     →  { access_token, token_type }

Authorization: Bearer <access_token>
```

Roles: `user` (default) · `admin` (can delete books).

## Tests

```bash
# Run all tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=src/library_catalog
```

Tests use mocked repositories and services — **no real database required**.

## Project Structure

```
.
├── pyproject.toml              # Package metadata, Poetry deps & tool config
├── requirements.txt            # Pinned lockfile for deployment
├── docker-compose.yml
├── alembic/                    # Database migrations
└── src/library_catalog/
    ├── api/
    │   ├── dependencies.py     # FastAPI dependency injection
    │   └── v1/
    │       ├── routers/        # books, auth, health
    │       └── schemas/        # Pydantic request/response models
    ├── core/
    │   ├── config.py           # Settings (pydantic-settings)
    │   ├── database.py         # SQLAlchemy engine & session
    │   ├── exceptions.py       # AppException hierarchy
    │   └── security.py         # JWT helpers, password hashing
    ├── data/
    │   ├── models/             # SQLAlchemy ORM models
    │   └── repositories/       # Data access layer
    ├── domain/
    │   ├── exceptions.py       # Domain-specific exceptions
    │   ├── mappers/            # ORM → DTO converters
    │   └── services/           # Business logic
    ├── external/
    │   └── openlibrary/        # Open Library API client
    └── utils/
        └── helpers.py
```
