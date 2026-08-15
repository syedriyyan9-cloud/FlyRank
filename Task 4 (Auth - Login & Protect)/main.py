from fastapi import FastAPI, HTTPException, status
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

@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}

@app.get("/health")
def health():
    return {"status": "ok"}

# ========== STAGE 1: Signup & Login ==========

@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(auth: AuthRequest):
    # Validate input
    if not auth.email or not auth.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Register user with Supabase
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
    # Validate input
    if not auth.email or not auth.password:
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Login with Supabase
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