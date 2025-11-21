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

from .deps import get_current_user  # assumes this returns {"user_id": int, ...}

USER_SERVICE_URL = "http://user-service:8000"
TASK_SERVICE_URL = "http://task-service:8000"

app = FastAPI(title="API Gateway")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
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
    """Serve index.html from the frontend folder."""
    html_path = Path(__file__).resolve().parent.parent / "frontend" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


# ---------- Auth proxy ----------
@app.post("/auth/register")
async def register_proxy(request: Request):
    data = await request.json()
    resp = await request.app.state.client.post(f"{USER_SERVICE_URL}/register", json=data)

    try:
        content = resp.json()
    except Exception:
        content = {"detail": resp.text}

    return JSONResponse(status_code=resp.status_code, content=content)


@app.post("/auth/login")
async def login_proxy(request: Request):
    data = await request.json()
    resp = await request.app.state.client.post(f"{USER_SERVICE_URL}/login", json=data)

    try:
        content = resp.json()
    except Exception:
        raise HTTPException(status_code=resp.status_code, detail=f"Login failed: {resp.text}")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=content.get("detail", "Login failed"),
        )
    return content


# ---------- Task proxy ----------
@app.get("/tasks")
async def list_tasks(current_user=Depends(get_current_user)):
    headers = {"X-User-Id": str(current_user["user_id"])}
    resp = await app.state.client.get(f"{TASK_SERVICE_URL}/tasks", headers=headers)

    if resp.status_code != 200:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return resp.json()


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(request: Request, current_user=Depends(get_current_user)):
    data = await request.json()
    headers = {"X-User-Id": str(current_user["user_id"])}
    resp = await app.state.client.post(
        f"{TASK_SERVICE_URL}/tasks", json=data, headers=headers
    )

    if resp.status_code != status.HTTP_201_CREATED:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return resp.json()


# NEW: Update task
@app.put("/tasks/{task_id}")
async def update_task(
    task_id: int,
    request: Request,
    current_user=Depends(get_current_user),
):
    data = await request.json()
    headers = {"X-User-Id": str(current_user["user_id"])}
    resp = await app.state.client.put(
        f"{TASK_SERVICE_URL}/tasks/{task_id}",
        json=data,
        headers=headers,
    )

    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return resp.json()


# NEW: Delete task
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, current_user=Depends(get_current_user)):
    headers = {"X-User-Id": str(current_user["user_id"])}
    resp = await app.state.client.delete(
        f"{TASK_SERVICE_URL}/tasks/{task_id}",
        headers=headers,
    )

    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return None  # 204 No Content