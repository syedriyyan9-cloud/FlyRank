from fastapi import FastAPI
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Auth API", version="1.0")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

@app.get("/")
def root():
    return {"message": "Server running and connected to Supabase"}

@app.get("/health")
def health():
    return {"status": "ok"}