from pathlib import Path

import httpx
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from .deps import get_current_user

USER_SERVICE_URL = "http://user-service:8000"
TASK_SERVICE_URL = "http://task-service:8000"

app = FastAPI(title="API Gateway")

# CORS pentru frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pentru demo; poți restricționa mai târziu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    app.state.client = httpx.AsyncClient(timeout=10.0)


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.client.aclose()


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Servește index.html din folderul frontend."""
    html_path = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


# ---------- Auth proxy ----------


@app.post("/auth/register")
async def register_proxy(request: Request):
    data = await request.json()
    client: httpx.AsyncClient = request.app.state.client

    resp = await client.post(f"{USER_SERVICE_URL}/register", json=data)

    # Încercăm să retransmitem JSON-ul; dacă nu e JSON, trimitem textul.
    try:
        content = resp.json()
    except Exception:
        content = {"detail": resp.text}

    return JSONResponse(status_code=resp.status_code, content=content)


@app.post("/auth/login")
async def login_proxy(request: Request):
    data = await request.json()
    client: httpx.AsyncClient = request.app.state.client

    resp = await client.post(f"{USER_SERVICE_URL}/login", json=data)

    try:
        content = resp.json()
    except Exception:
        # dacă user-service returnează o eroare non-JSON
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Login failed: {resp.text}",
        )

    if resp.status_code != 200:
        # propagăm detaliul de eroare
        raise HTTPException(
            status_code=resp.status_code, detail=content.get("detail", "Login failed")
        )

    # aici content ar trebui să fie {access_token, token_type}
    return content


# ---------- Task proxy (JWT -> X-User-Id) ----------


@app.get("/tasks")
async def list_tasks(current_user=Depends(get_current_user), request: Request = None):
    client: httpx.AsyncClient = request.app.state.client
    headers = {"X-User-Id": str(current_user["user_id"])}

    resp = await client.get(f"{TASK_SERVICE_URL}/tasks", headers=headers)

    try:
        content = resp.json()
    except Exception:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Task service error: {resp.text}",
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=content.get("detail", "Cannot fetch tasks"),
        )

    return content


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,
    current_user=Depends(get_current_user),
):
    client: httpx.AsyncClient = request.app.state.client
    data = await request.json()
    headers = {"X-User-Id": str(current_user["user_id"])}

    resp = await client.post(f"{TASK_SERVICE_URL}/tasks", json=data, headers=headers)

    try:
        content = resp.json()
    except Exception:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Task service error: {resp.text}",
        )

    if resp.status_code != status.HTTP_201_CREATED:
        raise HTTPException(
            status_code=resp.status_code,
            detail=content.get("detail", "Cannot create task"),
        )

    return content
