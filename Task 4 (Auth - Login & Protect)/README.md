# Secure Auth API with Supabase

A secure REST API with user authentication using **FastAPI** and **Supabase Auth**. Features signup, login, logout, and protected routes with JWT token verification.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [Installation & Running](#-installation--running)
- [API Endpoints](#-api-endpoints)
- [Testing with curl](#-testing-with-curl)
- [Swagger UI](#-swagger-ui)
- [Architecture](#%EF%B8%8F-architecture)
- [Environment Variables](#-environment-variables)
- [Project Structure](#-project-structure)
- [Future Improvements](#-future-improvements)

---

## ✨ Features

- **User Signup**: Create new user accounts.
- **User Login**: Authenticate and receive JWT tokens.
- **User Logout**: Terminate active user sessions.
- **Protected Routes**: Secure endpoints requiring valid JWT authentication.
- **Public Routes**: Open endpoints accessible without authentication.
- **Swagger UI**: Interactive API documentation featuring Bearer Auth support.
- **Middleware/Dependency**: Reusable authentication verification logic.

---

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Auth Provider**: Supabase Auth
- **Token Format**: JWT (JSON Web Tokens)
- **ASGI Server**: Uvicorn
- **Documentation**: Swagger UI / ReDoc

---

## 📦 Installation & Running

### Prerequisites

- Python 3.10+ installed
- Supabase account (free tier)
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <project-folder>
   ```

2. **Create and activate a virtual environment**
   - **On Mac/Linux:**
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - **On Windows:**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and configure your Supabase credentials:
   ```env
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - **API Base**: [http://localhost:8000](http://localhost:8000)
   - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Endpoints

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| **POST** | `/auth/signup` | Create new user account | ❌ No |
| **POST** | `/auth/login` | Login and get access token | ❌ No |
| **POST** | `/auth/logout` | Logout and invalidate session | ✅ Yes |
| **GET** | `/public/info` | Get public information | ❌ No |
| **GET** | `/protected/profile` | Get user profile data | ✅ Yes |
| **GET** | `/protected/dashboard` | Get user dashboard | ✅ Yes |

---

## 🧪 Testing with curl

### 1. Signup

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```
*Response:* `201 Created`

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```
*Response:* `200 OK` with `access_token`

### 3. Access Protected Route

```bash
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
*Response:* `200 OK` with user data

### 4. Invalid Token Test

```bash
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer invalid_token"
```
*Response:* `401 Unauthorized`

### 5. Logout

```bash
curl -i -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
*Response:* `204 No Content`

---

## 📚 Swagger UI

Interactive API documentation available at:  
👉 **`http://localhost:8000/docs`**

![Swagger UI](screenshots/swagger-screenshot.png)

### How to use Swagger Auth:
1. Open `http://localhost:8000/docs` in your browser.
2. Click the **"Authorize"** button (lock icon).
3. Enter your token as: `Bearer YOUR_ACCESS_TOKEN`.
4. Click **"Authorize"**.
5. Test any endpoint under protected routes using **"Try it out"**.

---

## 🏗️ Architecture

### Auth Flow

```text
Client → POST /auth/login → Supabase (verify credentials) → Returns JWT Token
Client → GET /protected/profile (with Bearer Token) → FastAPI → Verify Token with Supabase → Returns Data
Client → POST /auth/logout (with Bearer Token) → FastAPI → Supabase.sign_out()
```

### HTTP Status Codes

| Code | Meaning | Description |
| :--- | :--- | :--- |
| **200** | Success | Request processed successfully |
| **201** | Created | User registered successfully |
| **204** | No Content | Session terminated / Logout completed |
| **400** | Bad Request | Missing or invalid payload fields |
| **401** | Unauthorized | Missing, invalid, or expired JWT token |

---

## 🔐 Authentication Flow

```text
1. User signs up → POST /auth/signup → Supabase creates account
2. User logs in → POST /auth/login → Returns JWT access_token
3. Client sends token → Authorization: Bearer <token>
4. Server verifies token → supabase.auth.get_user(token)
5. Valid token → Access granted to protected routes
6. Invalid/expired token → 401 Unauthorized
```
---

## 🔧 Environment Variables

### `.env` (gitignored - contains real credentials)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_actual_anon_key
```

### `.env.example` (committed - contains placeholder values)
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

---

## 📁 Project Structure

```text
task-4-auth/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (gitignored)
├── .env.example            # Sample environment variables
├── README.md               # Documentation
├── .gitignore              # Git ignore rules
└── screenshots/            # Screenshots directory
    └── swagger-screenshot.png
```

---

## 🚀 Future Improvements

- [ ] Add email confirmation for signup
- [ ] Add password reset functionality
- [ ] Add role-based access control (Admin/User)
- [ ] Add API rate limiting
- [ ] Add refresh token rotation
