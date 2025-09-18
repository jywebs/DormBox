# Copilot Instructions for DormBox

This file guides GitHub Copilot suggestions for the DormBox repository.  
DormBox is a FastAPI plus MongoDB app for tracking boxes, bundles, and items for college move-in.  
Use Python 3.11 or newer. Avoid blocking I/O. Prefer async patterns.

---

## Repo Structure

```
DormBox/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # env vars, Mongo connection
│   ├── models/              # Pydantic schemas
│   ├── db/                  # db init and helpers
│   ├── routes/              # API routers (boxes, items, bundles)
│   └── services/            # business logic (qr, enrichment, etc.)
├── tests/                   # pytest tests
├── requirements.txt
├── docker-compose.yml       # optional for local dev
├── copilot-instructions.md
└── README.md
```

---

## Tech Choices and Libraries

- Framework: FastAPI
- DB driver: Motor (async MongoDB)
- Validation: Pydantic models
- HTTP client: httpx for outbound calls
- QR code: qrcode
- Auth: to be added with JWT later

When Copilot generates code, always:
- Use async functions for endpoints and DB operations.
- Use type hints and docstrings.
- Validate and sanitize all user inputs.
- Return JSON with correct HTTP status codes.
- Keep modules small and cohesive.

---

## Configuration and Mongo Connection

Place configuration in `app/config.py`. Use environment variables. Provide a singleton Motor client and database accessor.

```python
# app/config.py
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import os

class Settings(BaseModel):
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db: str = os.getenv("MONGODB_DB", "dormbox")

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

_client: AsyncIOMotorClient | None = None

def get_db():
    global _client
    st = get_settings()
    if _client is None:
        _client = AsyncIOMotorClient(st.mongodb_uri, uuidRepresentation="standard")
    return _client[st.mongodb_db]
```

Use `app.state` or a dependency to access the DB inside routes. Prefer dependency functions.

---

## Models

Place Pydantic schemas in `app/models`. Keep create and response models distinct.

```python
# app/models/box.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BoxCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = None
    tags: List[str] = []
    status: str = Field("planned", pattern="^(planned|packed|shipped|arrived)$")

class Box(BaseModel):
    id: str
    qrSlug: str
    createdAt: datetime
    updatedAt: datetime
    # inherit fields for response
    name: str
    description: Optional[str] = None
    tags: List[str] = []
    status: str
```

Add similar files for `item` and `bundle` that mirror the PRD fields.

---

## Routers

Create one router per entity inside `app/routes`. Use dependency injection for DB and common utilities.

```python
# app/routes/boxes.py
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import uuid
from app.models.box import Box, BoxCreate
from app.config import get_db

router = APIRouter()

@router.post("/", response_model=Box, status_code=status.HTTP_201_CREATED)
async def create_box(payload: BoxCreate, db = Depends(get_db)):
    slug = str(uuid.uuid4())
    now = datetime.utcnow()
    doc = {
        "name": payload.name,
        "description": payload.description,
        "tags": payload.tags,
        "status": payload.status,
        "qrSlug": slug,
        "createdAt": now,
        "updatedAt": now,
    }
    result = await db["boxes"].insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc

@router.get("/", response_model=list[Box])
async def list_boxes(db = Depends(get_db), q: str | None = None, status_filter: str | None = None, skip: int = 0, limit: int = 25):
    filt: dict = {}
    if q:
        filt["name"] = {"$regex": q, "$options": "i"}
    if status_filter:
        filt["status"] = status_filter
    cursor = db["boxes"].find(filt).skip(skip).limit(min(limit, 100))
    items = []
    async for d in cursor:
        d["id"] = str(d["_id"])
        items.append(d)
    return items
```

Register routers in `app/main.py`.

```python
# app/main.py
from fastapi import FastAPI
from app.routes import boxes

app = FastAPI(title="DormBox API")
app.include_router(boxes.router, prefix="/api/v1/boxes", tags=["boxes"])

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## Services

Business logic belongs in `app/services`.

- `qr_service.py`: functions to generate QR images and return a URL or base64 content.
- `enrichment_service.py`: fetch title and image from Amazon URL using httpx and Open Graph tags. Validate hostnames and use timeouts.

Example interface:

```python
# app/services/enrichment_service.py
import httpx
from bs4 import BeautifulSoup

async def enrich_amazon_url(url: str) -> dict:
    # validate url hostname and scheme
    timeout = httpx.Timeout(5.0, connect=2.0)
    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "DormBox/1.0"}) as client:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = soup.find("meta", property="og:title")
    image = soup.find("meta", property="og:image")
    return {
        "title": title["content"] if title and title.has_attr("content") else None,
        "imageUrl": image["content"] if image and image.has_attr("content") else None,
        "asin": extract_asin(url),
    }

def extract_asin(url: str) -> str | None:
    # parse common Amazon patterns and return ASIN if found
    return None
```

Note: add `beautifulsoup4` to requirements if using this approach.

---

## Error Handling

Use FastAPI `HTTPException` for predictable errors. Return a consistent error envelope.

```python
from fastapi import HTTPException, status

def bad_request(message: str):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"error": {"code": "bad_request", "message": message}},
    )
```

For unhandled exceptions rely on FastAPI default handler. Add logging middleware later.

---

## Pagination and Query

- Accept `skip` and `limit` in list endpoints. Cap `limit` at 100.
- Offer simple search via regex on `name` and `title` fields.
- Add status filters that match PRD enums.

---

## Security

- All endpoints behind HTTPS.
- Input validation on query and body.
- Rate limit enrichment endpoints. Use simple per IP throttling at first.
- Prepare to add JWT later. Keep endpoints structured to add `Depends(auth_guard)` when ready.

---

## Testing

Use `pytest` in `tests`. Include happy path and basic failure tests per route.

```python
# tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

Mock Motor for unit tests that need DB interaction or spin a test container in CI.

---

## Linting and Formatting

- Use ruff or flake8 for linting.
- Use black for formatting.
- Keep imports sorted. Avoid wildcard imports.

---

## Commit Messages and PRs

- Use concise, imperative subject lines. Example: Add items router with create and list.
- Include a short body that explains why and how.
- Require CI to run tests and lints.

---

## API Contract Snapshot

Base path: `/api/v1`

- Boxes
  - POST `/boxes`
  - GET `/boxes`
  - GET `/boxes/{id}`
  - PATCH `/boxes/{id}`
  - DELETE `/boxes/{id}`
  - GET `/boxes/qr/{slug}`

- Items
  - POST `/items`
  - GET `/items`
  - GET `/items/{id}`
  - PATCH `/items/{id}`
  - PATCH `/items/{id}/move`
  - DELETE `/items/{id}`

- Bundles
  - POST `/bundles`
  - GET `/bundles`
  - GET `/bundles/{id}`
  - PATCH `/bundles/{id}`
  - DELETE `/bundles/{id}`

- Enrichment
  - POST `/enrich/amazon` body `{ url }` returns `{ title, imageUrl, asin }`

Keep response shapes aligned with Pydantic response models.

---

## Do and Do Not

Do
- Write small, testable functions.
- Use dependency injection for DB and services.
- Handle errors with helpful messages.

Do not
- Hardcode secrets.
- Mix DB logic inside routers.
- Use blocking I/O inside async endpoints.

---

## Ready to Generate

Copilot can safely scaffold:
- Models for boxes, items, bundles.
- Routers with CRUD endpoints.
- Services for QR generation and enrichment.
- Tests for health and basic CRUD.
- Dockerfile and docker-compose for local dev.
