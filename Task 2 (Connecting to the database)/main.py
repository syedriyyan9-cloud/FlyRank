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

# ============== STAGE 2: Create Endpoint with Database ==============

@app.post("/tasks", status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(task: TaskCreate):
    """Create a new task in the database"""
    # Validate title
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task.title.strip(), 0)
        )
        conn.commit()
        
        # Get the newly created task
        task_id = cursor.lastrowid
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        new_task = cursor.fetchone()
        
    return row_to_dict(new_task)

# ============== STAGE 3: Update and Delete Endpoints with Database ==============

@app.put("/tasks/{task_id}", tags=["Tasks"])
def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task in the database"""
    # Check if task exists
    existing_task = get_task_from_db(task_id)
    if existing_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    # Build update query dynamically
    update_fields = []
    values = []
    
    if task_update.title is not None:
        if not task_update.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty"
            )
        update_fields.append("title = ?")
        values.append(task_update.title.strip())
    
    if task_update.done is not None:
        update_fields.append("done = ?")
        values.append(1 if task_update.done else 0)
    
    if not update_fields:
        # No fields to update, return existing task
        return row_to_dict(existing_task)
    
    # Add updated_at timestamp
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(task_id)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        
        # Get updated task
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        updated_task = cursor.fetchone()
        
    return row_to_dict(updated_task)

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: int):
    """Delete a task from the database"""
    # Check if task exists
    existing_task = get_task_from_db(task_id)
    if existing_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    
    return None

# ============== EXTRA: Stretch Goals with Database ==============

@app.get("/tasks/filter/", tags=["Tasks"])
def filter_tasks(done: Optional[bool] = None, search: Optional[str] = None):
    """Filter tasks by done status and/or search by title using SQL"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build query dynamically
        conditions = []
        values = []
        
        if done is not None:
            conditions.append("done = ?")
            values.append(1 if done else 0)
        
        if search:
            conditions.append("title LIKE ?")
            values.append(f"%{search}%")
        
        query = "SELECT * FROM tasks"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id"
        
        cursor.execute(query, values)
        rows = cursor.fetchall()
        return [row_to_dict(row) for row in rows]

@app.get("/stats", tags=["Tasks"])
def get_stats():
    """Get statistics about tasks using SQL COUNT"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total tasks
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total = cursor.fetchone()[0]
        
        # Completed tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
        done = cursor.fetchone()[0]
        
        # Open tasks
        open_tasks = total - done
        
        return {
            "total": total,
            "done": done,
            "open": open_tasks
        }

@app.post("/reset", status_code=status.HTTP_200_OK, tags=["Tasks"])
def reset_tasks():
    """Reset tasks to the default examples"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Delete all tasks
        cursor.execute("DELETE FROM tasks")
        
        # Insert example tasks
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
        
        # Get reset tasks
        cursor.execute("SELECT * FROM tasks ORDER BY id")
        rows = cursor.fetchall()
        
    return {
        "message": "Tasks reset to default",
        "tasks": [row_to_dict(row) for row in rows]
    }

@app.get("/database/info", tags=["Database"])
def get_database_info():
    """Get information about the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [{"name": row[1], "type": row[2]} for row in cursor.fetchall()]
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM tasks")
        row_count = cursor.fetchone()[0]
        
        return {
            "database_file": DATABASE_FILE,
            "table_name": "tasks",
            "columns": columns,
            "row_count": row_count
        }