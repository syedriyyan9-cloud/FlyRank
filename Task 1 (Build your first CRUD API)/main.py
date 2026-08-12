from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks",
    version="1.0.0"
)

# In-memory database (resets on server restart)
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Write documentation", "done": True}
]
next_id = 4

# Pydantic models for request validation
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

# Helper function to find a task by ID
def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None

# ============== STAGE 0 & 1: Root and Health Endpoints ==============

@app.get("/", tags=["Root"])
def read_root():
    """Welcome message for the API"""
    return {"message": "Hello World"}

@app.get("/info", tags=["Root"])
def get_api_info():
    """Get API information and available endpoints"""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/tasks/{id}", "/health", "/info"]
    }

@app.get("/health", tags=["Root"])
def health_check():
    """Check if the server is running"""
    return {"status": "ok"}

# ============== STAGE 2: Read Endpoints ==============

@app.get("/tasks", tags=["Tasks"])
def get_all_tasks():
    """Get all tasks"""
    return tasks

@app.get("/tasks/{task_id}", tags=["Tasks"])
def get_task(task_id: int):
    """Get a single task by its ID"""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return task

# ============== STAGE 3: Create Endpoint ==============

@app.post("/tasks", status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(task: TaskCreate):
    """Create a new task"""
    global next_id
    
    # Validate title
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )
    
    # Create the new task
    new_task = {
        "id": next_id,
        "title": task.title.strip(),
        "done": False
    }
    tasks.append(new_task)
    next_id += 1
    return new_task

