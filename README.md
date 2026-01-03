Finanlytics
===================

**High-performance financial data engine with RESTful endpoints that:** 
- **Delivers clean, fast, intuitive analytics across each user’s statements via well-structured APIs** 
- **Turns uploaded PDFs/text into actionable insights using AI-powered extraction** 
- **Lets users post their own transactions with predefined categories and add custom categories when needed**



Performance & Architecture
--------------------------
- **Sub-second response times** via async PostgreSQL operations
- **Zero-downtime authentication** with JWT bearer tokens
- **Intelligent document processing** supporting both PDF and text formats
- **Real-time transaction validation** with automatic data normalization
- **RESTful API design** across all endpoints for clear, consistent integration
- **FastAPI + Pydantic v2**: Type-safe API with automatic validation and serialization
- **Async SQLAlchemy + PostgreSQL**: Non-blocking database operations for maximum throughput
- **AI for NLP**: State-of-the-art language model for financial document understanding
- **JWT Authentication**: Stateless, scalable security with OAuth2 compliance
- **ORM Pythonic functions**: dynamic & safety first Object Relational Modelling preventing malware attacks via native sql injections.
- **Async PDF Processing**: Concurrent document parsing with `pdfplumber` optimization
- **Smart Document Ingestion**: Handles multiple formats (.pdf, .txt) with automatic format detection
- **Scalable Processing**: Async architecture handles multiple concurrent uploads without performance degradation
- **RESTful API design** with pagination best practices on collection endpoints for consistent, predictable integration

Project layout
--------------
```
src/backend/
  main.py                         # FastAPI app factory and router wiring

  routers/                        # Route handlers
    user_router.py                # Register, login, profile, logout
    transaction_router.py         # Upload, summaries, manual input, monthly views
    category_router.py            # List/create categories
    
  services/                       # Domain logic
    user_service.py               # Auth,JWT handling, users CRUD
    transaction_service.py        # Upload/extract, create, summaries & aggregates

  schemas/                        # Pydantic schemas for requests/responses
    user_schema.py
    transaction_schema.py
    categories_schema.py

  database/
    database_connection/          # Async engine/session and init hook
      database_config.py
      database_client.py
      
    models/                       # SQLAlchemy models
      user_model.py
      transaction_model.py
      categories_model.py


```

Getting started
---------------
1) Prerequisites: Python 3.11+, Poetry, and a reachable PostgreSQL instance (default URL points to `postgresql+asyncpg://.../finanlytics` on port 5433).  
2) Install dependencies:
```
poetry install
```
3) Run the API (from the `backend` directory):
```
poetry run uvicorn backend.main:app --reload --app-dir src
```
4) Browse interactive docs at `http://localhost:8000/docs`.

Packaging & reuse
-----------------
- Managed with Poetry (`pyproject.toml` + `poetry.lock`) for reproducible installs, publishing, and deployment.
- `poetry export` can generate a `requirements.txt` for container or CI use; `poetry run` keeps tooling scoped to the project virtualenv.
- The service is a clean Python package (`backend`) under `src/`, so it can be imported, extended, or run in other contexts without path hacks.


Database Schema & ORM Models
-----------------------------
**SQLAlchemy entity relationships:**

```
User
 ├── categories (one-to-many) → Category.owner
 └── transactions (one-to-many) → Transaction.user

Category
 ├── owner (many-to-one) → User
 └── transactions (one-to-many) → Transaction.category

Transaction
 ├── user (many-to-one) → User
 └── category (many-to-one) → Category
```

**Key constraints:**
- Users own categories and transactions
- Categories are user-scoped (isolation via foreign key)
- Transactions link to both user and category for efficient querying and validation


Authentication flow
-------------------
- Register: `POST /users/register` with JSON `{"email": "...", "password": "...", "first_name": "...", "last_name": "..."}`.
- Login: `POST /users/login` (form-encoded `username` = email, `password`) returns `{"access_token": "...", "token_type": "bearer"}`.
- Authenticated requests: include `Authorization: Bearer <token>`.
- Get current user: `GET /users/me`.
- Logout: `POST /users/logout` (client-side token discard).


Example usage
-------------
Register:
```
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"Secret123!","first_name":"Demo","last_name":"User"}'
```
Login:
```
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo@example.com&password=Secret123!"
```
Get current user:
```
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer TOKEN"
```
Logout (client should discard the token):
```
curl -X POST http://localhost:8000/users/logout \
  -H "Authorization: Bearer TOKEN"
```
Upload a statement (replace TOKEN and PATH):
```
curl -X POST http://localhost:8000/transactions/upload \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@/path/to/statement.pdf"
```
Manually input a transaction:
```
curl -X POST http://localhost:8000/transactions/input_transactions \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"date":"2024-03-15","amount":120.50,"transaction_type":"EXPENSE","category":"Food & Groceries","to_from":"Store","description":"Groceries run"}'
```
List user transactions:
```
curl -X GET http://localhost:8000/transactions/user_transactions \
  -H "Authorization: Bearer TOKEN"
```
Income summary:
```
curl -X GET http://localhost:8000/transactions/income_summary \
  -H "Authorization: Bearer TOKEN"
```
Expense summary:
```
curl -X GET http://localhost:8000/transactions/expense_summary \
  -H "Authorization: Bearer TOKEN"
```
Spending by category summary:
```
curl -X GET http://localhost:8000/transactions/spending_category_summary \
  -H "Authorization: Bearer TOKEN"
```
Get your categories (default + user-created):
```
curl -X GET http://localhost:8000/categories/user_categories \
  -H "Authorization: Bearer TOKEN"
```
Create a custom category:
```
curl -X POST http://localhost:8000/categories/create_category \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category_name":"Travel"}'
```
