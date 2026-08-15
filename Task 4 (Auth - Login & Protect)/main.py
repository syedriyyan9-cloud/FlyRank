from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# ========== Swagger Security Setup ==========
app = FastAPI(
    title="Auth API",
    version="1.0",
    description="Secure API with Supabase Authentication",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

# Security scheme for Swagger
security = HTTPBearer(auto_error=False)

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

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify token from Authorization header"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Access token required")
    
    token = credentials.credentials
    
    if not token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    user = verify_token(token)
    
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

async def get_token_for_logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract token for logout"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Access token required")
    return credentials.credentials

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

@app.get("/public/info", tags=["Public"])
def public_info():
    """Public endpoint - no authentication required"""
    return {"message": "Welcome stranger! This info is public."}

# ========== STAGE 3 & 4: Protected Routes ==========

@app.get("/protected/profile", dependencies=[Depends(security)], tags=["Protected"])
def protected_profile(user: dict = Depends(get_current_user)):
    """Protected endpoint - returns user profile data"""
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
        "message": "This is your secure profile data"
    }

@app.get("/protected/dashboard", dependencies=[Depends(security)], tags=["Protected"])
def protected_dashboard(user: dict = Depends(get_current_user)):
    """Protected endpoint - returns dashboard data"""
    return {
        "user_id": user.id,
        "email": user.email,
        "message": "Welcome to your dashboard!",
        "tasks_count": 5
    }

# ========== STAGE 4: Logout ==========

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(security)], tags=["Auth"])
def logout(token: str = Depends(get_token_for_logout)):
    """Logout - invalidates the session"""
    try:
        supabase.auth.sign_out()
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))