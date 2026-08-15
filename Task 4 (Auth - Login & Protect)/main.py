from fastapi import FastAPI, HTTPException, status, Request, Depends
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Auth API", version="1.0")

# Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Request models
class AuthRequest(BaseModel):
    email: str
    password: str

# ========== Auth Dependency (Middleware) ==========

def verify_token(token: str):
    """Verify JWT token with Supabase"""
    try:
        response = supabase.auth.get_user(token)
        if response.user is None:
            return None
        return response.user
    except Exception as e:
        return None

async def get_current_user(request: Request):
    """Extract and verify token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(status_code=401, detail="Access token required")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use: Bearer <token>")
    
    token = auth_header.split(" ")[1]
    
    if not token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    user = verify_token(token)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

def get_token_from_request(request: Request):
    """Extract token for logout"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access token required")
    return auth_header.split(" ")[1]

# ========== ROOT & HEALTH ==========

@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ========== STAGE 1: Signup & Login ==========

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(auth: AuthRequest):
    if not auth.email or not auth.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    try:
        response = supabase.auth.sign_up({
            "email": auth.email,
            "password": auth.password
        })
        
        if response.user is None:
            raise HTTPException(status_code=400, detail="Signup failed")
        
        return {"user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
def login(auth: AuthRequest):
    if not auth.email or not auth.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth.email,
            "password": auth.password
        })
        
        if response.session is None:
            raise HTTPException(status_code=401, detail="Invalid login credentials")
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

# ========== STAGE 2: Public Route ==========

@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

# ========== STAGE 3 & 4: Protected Routes with Middleware ==========

@app.get("/protected/profile")
def protected_profile(user: dict = Depends(get_current_user)):
    """Protected endpoint - uses dependency for auth"""
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "message": "This is your secure profile data"
    }

@app.get("/protected/dashboard")
def protected_dashboard(user: dict = Depends(get_current_user)):
    """Another protected endpoint using the same middleware"""
    return {
        "user_id": user.id,
        "email": user.email,
        "message": "Welcome to your dashboard!",
        "tasks_count": 5  # Placeholder
    }

# ========== STAGE 4: Logout ==========

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, token: str = Depends(get_token_from_request)):
    """Logout - invalidates the session"""
    try:
        # Sign out with Supabase
        supabase.auth.sign_out()
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))