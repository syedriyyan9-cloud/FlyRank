from fastapi import FastAPI, HTTPException, status, Request
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

# ========== Helper: Extract & Verify Token ==========

def verify_token(token: str):
    """Verify JWT token with Supabase"""
    try:
        # Get user from token
        response = supabase.auth.get_user(token)
        
        if response.user is None:
            return None
        
        return response.user
    except Exception as e:
        return None

def get_current_user(request: Request):
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

# ========== STAGE 3: Protected Profile with Verification ==========

@app.get("/protected/profile")
def protected_profile(request: Request):
    """Protected endpoint - verifies token and returns user data"""
    user = get_current_user(request)
    
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "message": "This is your secure profile data"
    }