# Task API - CRUD Application with SQLite

A simple RESTful API for managing a to-do list, built with **FastAPI** and **SQLite**. This project demonstrates the fundamentals of building a CRUD (Create, Read, Update, Delete) API with persistent data storage.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [Installation](#-installation)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Database](#%EF%B8%8F-database)
- [Testing with curl](#-testing-with-curl)
- [Swagger UI](#-swagger-ui)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Common Issues & Solutions](#-common-issues--solutions)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Author](#-author)
- [Key Observations](#-key-observations)
- [Additional Files](#-additional-files)

---

## ✨ Features

- **Complete CRUD Operations**: Create, Read, Update, and Delete tasks.
- **Persistent Storage**: Data stored in SQLite database (survives server restarts).
- **Auto-generated Documentation**: Interactive Swagger UI at `/docs` and ReDoc at `/redoc`.
- **Input Validation**: Proper validation using Pydantic for create and update operations.
- **Proper HTTP Status Codes**: Returns standard status codes (200, 201, 204, 400, 404, 503).
- **Filtering & Search**: Filter tasks by status or search by title keyword.
- **Statistics**: Get task metrics (total, completed, open tasks).
- **Health Check**: Monitor overall API and database status.
- **Reset Functionality**: Instantly reset the database to default initial tasks.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: SQLite3
- **ASGI Server**: Uvicorn
- **Data Validation**: Pydantic
- **Documentation**: Swagger UI / ReDoc

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher installed
- `pip` (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/todo-api.git
   cd todo-api
   ```

2. **Create and activate a virtual environment**
   - **On Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **On Mac/Linux:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   # Database is automatically initialized when running the server,
   # but you can also initialize it separately:
   python init_db.py
   ```

---

## 🚀 Running the Application

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload
```
*Server will run at:* `http://localhost:8000`

### Production Mode

```bash
uvicorn main:app
```

### Access the API

- **API Root**: [http://localhost:8000](http://localhost:8000)
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 API Endpoints

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | Welcome message | 200 |
| **GET** | `/info` | API information | 200 |
| **GET** | `/health` | Health check | 200, 503 |
| **GET** | `/tasks` | Get all tasks | 200 |
| **GET** | `/tasks/{id}` | Get a single task | 200, 404 |
| **POST** | `/tasks` | Create a new task | 201, 400 |
| **PUT** | `/tasks/{id}` | Update a task | 200, 400, 404 |
| **DELETE** | `/tasks/{id}` | Delete a task | 204, 404 |
| **GET** | `/tasks/filter/` | Filter tasks | 200 |
| **GET** | `/stats` | Get statistics | 200 |
| **POST** | `/reset` | Reset to default tasks | 200 |
| **GET** | `/database/info` | Database information | 200 |

### Request / Response Examples

#### Create a Task
**Request:**
```http
POST /tasks HTTP/1.1
Content-Type: application/json

{
  "title": "Buy groceries"
}
```

**Response (`201 Created`):**
```json
{
  "id": 4,
  "title": "Buy groceries",
  "done": false,
  "created_at": "2024-01-15 10:30:00",
  "updated_at": "2024-01-15 10:30:00"
}
```

#### Update a Task
**Request:**
```http
PUT /tasks/1 HTTP/1.1
Content-Type: application/json

{
  "title": "Buy organic groceries",
  "done": true
}
```

**Response (`200 OK`):**
```json
{
  "id": 1,
  "title": "Buy organic groceries",
  "done": true,
  "created_at": "2024-01-15 09:00:00",
  "updated_at": "2024-01-15 10:35:00"
}
```

---

## 🗄️ Database

### Why SQLite?

- **Zero Configuration**: No complex database server installation required.
- **File-based**: Complete database stored in a single file (`tasks.db`).
- **Lightweight**: Perfect for local development, testing, and small projects.
- **Standard SQL**: Uses standard SQL queries and syntax.
- **Built-in**: Included out-of-the-box with the Python standard library.

### Database Schema

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database File Location
The database file `tasks.db` is created automatically in the project root directory upon application startup.

### Manual Database Exploration

You can inspect and manage the database using:
1. **DB Browser for SQLite (GUI)**: Download from [sqlitebrowser.org](https://sqlitebrowser.org/)
2. **Command Line Interface**:
   ```bash
   sqlite3 tasks.db
   .tables
   SELECT * FROM tasks;
   .quit
   ```

### Example SQL Queries

```sql
-- List all tasks
SELECT * FROM tasks;

-- Show only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- Count all tasks
SELECT COUNT(*) FROM tasks;

-- Mark every task as completed
UPDATE tasks SET done = 1;

-- Delete all completed tasks
DELETE FROM tasks WHERE done = 1;

-- Search tasks by title
SELECT * FROM tasks WHERE title LIKE '%milk%';

-- Get tasks sorted by title
SELECT * FROM tasks ORDER BY title;
```

---

## 🧪 Testing with curl

### Run Endpoints via CLI

```bash
# 1. Health Check
curl -i http://localhost:8000/health

# 2. Get API Info
curl -i http://localhost:8000/info

# 3. Get all tasks
curl -i http://localhost:8000/tasks

# 4. Get single task
curl -i http://localhost:8000/tasks/1

# 5. Create a task
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'

# 6. Update a task
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy organic milk", "done":true}'

# 7. Delete a task
curl -i -X DELETE http://localhost:8000/tasks/4

# 8. Filter tasks (completed)
curl -i "http://localhost:8000/tasks/filter/?done=true"

# 9. Search tasks
curl -i "http://localhost:8000/tasks/filter/?search=FastAPI"

# 10. Get statistics
curl -i http://localhost:8000/stats

# 11. Reset tasks
curl -i -X POST http://localhost:8000/reset

# 12. Database info
curl -i http://localhost:8000/database/info
```

### Sample curl Output

```text
HTTP/1.1 200 OK
content-type: application/json
content-length: 120

{
  "id": 1,
  "title": "Learn FastAPI",
  "done": false,
  "created_at": "2024-01-15 09:00:00",
  "updated_at": "2024-01-15 09:00:00"
}
```

---

## 📚 Swagger UI

The API includes auto-generated Swagger UI documentation available at:  
👉 **`http://localhost:8000/docs`**

![Swagger UI](screenshots/swagger-ui.png)

### Key Features:
- Interactive API documentation for testing live requests directly in the browser ("Try it out").
- Complete request/response schema visualization.
- Organized endpoints grouped by tags with status code details.

---

## 📁 Project Structure

```text
todo-api/
├── main.py                 # Main application file
├── init_db.py              # Database initialization script
├── requirements.txt        # Python dependencies
├── tasks.db               # SQLite database file (auto-created)
├── README.md              # Project documentation
├── screenshots/           # Screenshots directory
│   ├── swagger-ui.png     # Swagger UI screenshot
│   └── database-viewer.png# DB Browser screenshot
├── .gitignore             # Git ignore rules
└── venv/                  # Virtual environment directory
```

---

## 📝 Environment Variables

Create an optional `.env` file in the root directory:

```env
DATABASE_FILE=tasks.db
API_VERSION=1.0.0
DEBUG=True
```

---

## 🔧 Common Issues & Solutions

### Database Locked (`sqlite3.OperationalError: database is locked`)
If you encounter a database lock error:
1. Ensure no other application or terminal instance is writing to `tasks.db`.
2. Close **DB Browser for SQLite** if open in read/write mode.
3. Restart the FastAPI application server.

### Port Already in Use (`OSError: [Errno 98] Address already in use`)
If port `8000` is already in use:
- **Mac/Linux**:
  ```bash
  kill -9 $(lsof -t -i:8000)
  ```
- **Windows**:
  ```bash
  netstat -ano | findstr :8000
  taskkill /PID <PID> /F
  ```

---

## 🚀 Future Improvements

- [ ] Add user authentication (JWT / OAuth2)
- [ ] Add pagination for large task lists
- [ ] Add PostgreSQL / MySQL database support
- [ ] Implement response caching (Redis)
- [ ] Add API rate limiting
- [ ] Add comprehensive unit and integration tests (Pytest)
- [ ] Add Docker containerization (`Dockerfile` & `docker-compose.yml`)
- [ ] Setup CI/CD pipeline with GitHub Actions

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- Backend Development Course Curriculum

---

## 📊 Key Observations

- **Data Persistence**: Data persists seamlessly across server restarts using SQLite, overcoming the limitations of in-memory dictionaries.
- **API Stability**: API endpoint structure and signatures remain consistent during backend implementation changes, maintaining a strict contract between client and server.
- **Decoupling**: Implementation details like database selection are isolated from API consumers.

---

## 📎 Additional Files

### Example `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite
*.sqlite3

# IDE & Editors
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

### Example `init_db.py`

```python
import sqlite3

DATABASE_FILE = "tasks.db"

def init_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert example tasks if table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    
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
        print(f"✅ Database initialized with {len(example_tasks)} tasks.")
    else:
        print(f"ℹ️ Database already contains {count} tasks.")
        
    conn.close()

if __name__ == "__main__":
    init_database()
```

---
