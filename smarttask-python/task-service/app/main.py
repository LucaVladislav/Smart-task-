from fastapi import FastAPI, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List

from .database import Base, engine, get_db
from . import models, schemas

app = FastAPI(title="Task Service")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Task Service running"}


def get_current_user_id(x_user_id: str = Header(..., alias="X-User-Id")) -> int:
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid X-User-Id header")


@app.get("/tasks", response_model=List[schemas.TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    tasks = db.query(models.Task).filter(models.Task.owner_id == user_id).all()
    return tasks


@app.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: schemas.TaskCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    task = models.Task(
        title=task_in.title,
        description=task_in.description,
        owner_id=user_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.owner_id == user_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # === FIXUL AICI: folosim doar câmpurile care au fost trimise ===
    update_data = task_in.dict(exclude_unset=True)  # magic line

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    task = (
        db.query(models.Task)
        .filter(models.Task.id == task_id, models.Task.owner_id == user_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return None