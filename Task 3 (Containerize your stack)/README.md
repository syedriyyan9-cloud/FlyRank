# Task API - CRUD Application with PostgreSQL & Docker

A RESTful API for managing a to-do list, built with **FastAPI**, **PostgreSQL**, and **Docker**. Data persists across container restarts using Docker volumes.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [Installation & Running](#-installation--running)
- [API Endpoints](#-api-endpoints)
- [Database](#%EF%B8%8F-database)
- [Testing with curl](#-testing-with-curl)
- [Swagger UI](#-swagger-ui)
- [Docker Architecture](#-docker-architecture)
- [Persistence Proof](#-persistence-proof)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Architecture Note](#-architecture-note)
- [Common Issues & Solutions](#-common-issues--solutions)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- **Complete CRUD Operations**: Create, Read, Update, and Delete tasks.
- **Persistent Storage**: Data stored in PostgreSQL with Docker volume (survives container restarts).
- **Containerized**: Entire stack runs with one `docker-compose up` command.
- **Auto-generated Documentation**: Interactive Swagger UI at `/docs` and ReDoc at `/redoc`.
- **Input Validation**: Proper validation using Pydantic for create and update operations.
- **Proper HTTP Status Codes**: Returns standard status codes (200, 201, 204, 400, 404, 503).
- **Health Check**: Monitor overall API and database status.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15 (running in Docker)
- **Container**: Docker & Docker Compose
- **ASGI Server**: Uvicorn
- **Data Validation**: Pydantic
- **Documentation**: Swagger UI / ReDoc

---

## 📦 Installation & Running

### Prerequisites

- Docker Desktop installed and running
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/syedriyyan9-cloud/FlyRank
   cd "Task 3 (Containerize your stack)"
   ```

2. **Create `.env` file (copy from `.env.example`)**
   ```bash
   cp .env.example .env
   ```

3. **Start everything with one command**
   ```bash
   docker-compose up --build
   ```

4. **Access the API** at [http://localhost:8000](http://localhost:8000)

### Useful Docker Commands

```bash
# Start services in detached mode (background)
docker-compose up -d

# Stop services
docker-compose down

# Stop and delete volume (data lost)
docker-compose down -v

# View logs
docker-compose logs -f

# Rebuild and start
docker-compose up --build
```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | Welcome message | 200 |
| **GET** | `/health` | Health check | 200, 503 |
| **GET** | `/tasks` | Get all tasks | 200 |
| **GET** | `/tasks/{id}` | Get a single task | 200, 404 |
| **POST** | `/tasks` | Create a new task | 201, 400 |
| **PUT** | `/tasks/{id}` | Update a task | 200, 400, 404 |
| **DELETE** | `/tasks/{id}` | Delete a task | 204, 404 |

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

### Why PostgreSQL?

- **Production-ready**: Industry-standard relational database used in real applications.
- **Dockerized**: Runs in container with persistent volume.
- **Data Persistence**: Docker volume ensures data survives container restarts.
- **ACID Compliant**: Reliable transactions and data integrity.

### Database Schema

```sql
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database File Location
Data is stored in a Docker volume `postgres_data` (not a file on your local machine).

### Manual Database Exploration

```bash
# Access PostgreSQL inside container
docker exec -it todo_db psql -U postgres -d tasks_db

# Run SQL queries inside PostgreSQL
SELECT * FROM tasks;
SELECT COUNT(*) FROM tasks;
\q
```

### Example SQL Queries

```sql
-- List all tasks
SELECT * FROM tasks;

-- Show only completed tasks
SELECT * FROM tasks WHERE done = TRUE;

-- Count all tasks
SELECT COUNT(*) FROM tasks;

-- Mark every task as completed
UPDATE tasks SET done = TRUE;

-- Delete all completed tasks
DELETE FROM tasks WHERE done = TRUE;
```

---

## 🧪 Testing with curl

### Run Endpoints via CLI

```bash
# 1. Health Check
curl -i http://localhost:8000/health

# 2. Get all tasks
curl -i http://localhost:8000/tasks

# 3. Get single task
curl -i http://localhost:8000/tasks/1

# 4. Create a task
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'

# 5. Update a task
curl -i -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy organic milk", "done":true}'

# 6. Delete a task
curl -i -X DELETE http://localhost:8000/tasks/4
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


### Key Features:
- Interactive API documentation for testing live requests directly in the browser ("Try it out").
- Complete request/response schema visualization.
- Organized endpoints grouped by tags with status code details.

---

## 🐳 Docker Architecture

### Services Defined in `docker-compose.yml`

1. **`db`** - PostgreSQL database
   - **Image**: `postgres:15`
   - **Persistent volume**: `postgres_data`
   - **Initialized with**: `init.sql`
   - **Port**: `5432`
2. **`app`** - FastAPI application
   - **Builds from**: `Dockerfile`
   - **Depends on**: `db` service
   - **Uses**: `.env` for connection string
   - **Port**: `8000`

### How It Works

```bash
docker-compose up --build   # Start both services
docker-compose down         # Stop containers (data persists)
docker-compose down -v      # Stop and delete volume (data lost)
```

### Data Flow

```text
Client Request → FastAPI App (container) → PostgreSQL (container) → Volume (persistent)
```

---

## 💾 Persistence Proof

To verify data survives container restarts:

1. **Create a task via API**:
   ```bash
   curl -X POST http://localhost:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title":"Test persistence"}'
   ```

2. **Stop containers**:
   ```bash
   docker-compose down
   ```

3. **Start again**:
   ```bash
   docker-compose up -d
   ```

4. **Verify data still exists**:
   ```bash
   curl http://localhost:8000/tasks
   ```

**Result**: All tasks still present ✅ - proving PostgreSQL with Docker volume persists data across container restarts.

---

## 📁 Project Structure

```text
Task 3 (Containerize your stack)/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── init.sql               # Database initialization script
├── docker-compose.yml     # Services definition
├── Dockerfile             # App container build
├── .env                   # Environment variables (gitignored)
├── .env.example           # Sample environment variables (committed)
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
```

---

## 📝 Environment Variables

### `.env` (gitignored - contains real values)
```env
DATABASE_URL=postgresql://postgres:postgres123@db:5432/tasks_db
```

### `.env.example` (committed - contains placeholder values)
```env
DATABASE_URL=postgresql://postgres:your_password@db:5432/tasks_db
```

---

## 🏗️ Architecture Note

Only the **repository layer** changed across assignments:

| Assignment | Storage Layer | Technology |
| :--- | :--- | :--- |
| **Assignment 1** | In-memory list | Python list |
| **Assignment 2** | SQLite | SQLite database file |
| **Assignment 3** | PostgreSQL | PostgreSQL in Docker container |

All service logic and route handlers remain **unchanged**, proving:
- Proper separation of concerns (API layer vs Data layer)
- Storage is an interchangeable implementation detail
- Clients don't need to know where data is stored

---

## 🔧 Common Issues & Solutions

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

### `.env` file not found
Create `.env` file in project root:
```bash
echo "DATABASE_URL=postgresql://postgres:postgres123@db:5432/tasks_db" > .env
```

### Database connection refused
Ensure PostgreSQL container is running:
```bash
docker ps
docker-compose logs db
```

### Version warning in `docker-compose`
Remove `version: '3.8'` from first line of `docker-compose.yml` (it's obsolete).

---
