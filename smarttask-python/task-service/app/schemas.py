from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class TaskOut(TaskBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
