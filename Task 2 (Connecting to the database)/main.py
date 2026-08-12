from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import sqlite3
from contextlib import contextmanager
from datetime import datetime

app = FastAPI(
    title="Task API",
    description="A simple CRUD API for managing tasks with SQLite persistence",
    version="1.0.0"
)

# Database setup
DATABASE_FILE = "tasks.db"

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database with the tasks table and example data if empty"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create tasks table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if the table is empty
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]
        
        # Insert example tasks only if the table is empty
        if count == 0:
            example_tasks = [
                ("Learn FastAPI", 0),
                ("Build CRUD API", 0),
                ("Write documentation", 1)
            ]
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                example_tasks
            )
            conn.commit()
            print(f"Database initialized with {len(example_tasks)} example tasks")
        else:
            print(f"Database already contains {count} tasks")

# Initialize database on startup
init_database()

# Pydantic models for request validation
class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# Helper function to get task from database
def get_task_from_db(task_id: int):
    """Retrieve a task from the database by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return cursor.fetchone()

# Helper function to convert Row to dict
def row_to_dict(row):
    """Convert sqlite3.Row to dictionary"""
    if row is None:
        return None
    return dict(row)

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
        "endpoints": ["/tasks", "/tasks/{id}", "/health", "/info"],
        "database": "SQLite",
        "database_file": DATABASE_FILE
    }

@app.get("/health", tags=["Root"])
def health_check():
    """Check if the server is running and database is accessible"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

# ============== STAGE 1: Read Endpoints with Database ==============

@app.get("/tasks", tags=["Tasks"])
def get_all_tasks():
    """Get all tasks from the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY id")
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]

@app.get("/tasks/{task_id}", tags=["Tasks"])
def get_task(task_id: int):
    """Get a single task by its ID from the database"""
    task = get_task_from_db(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    return row_to_dict(task)

