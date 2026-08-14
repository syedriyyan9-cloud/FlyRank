from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Task API", description="CRUD API with PostgreSQL", version="1.0.0")

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "ok", "database": "connected"}
    except:
        raise HTTPException(status_code=503, detail="Database unavailable")

@app.get("/tasks")
def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM tasks ORDER BY id")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    conn.close()
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "INSERT INTO tasks (title) VALUES (%s) RETURNING *",
        (task.title.strip(),)
    )
    new_task = cursor.fetchone()
    conn.commit()
    conn.close()
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    update_fields = []
    values = []
    
    if task_update.title is not None:
        if not task_update.title.strip():
            conn.close()
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        update_fields.append("title = %s")
        values.append(task_update.title.strip())
    
    if task_update.done is not None:
        update_fields.append("done = %s")
        values.append(task_update.done)
    
    if not update_fields:
        conn.close()
        return existing
    
    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = %s RETURNING *"
    cursor.execute(query, values)
    updated = cursor.fetchone()
    conn.commit()
    conn.close()
    return updated

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
    deleted = cursor.fetchone()
    conn.commit()
    conn.close()
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return None