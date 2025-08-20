# src/app/main.py

from fastapi import FastAPI
from .login.router import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Jamiron_BE API."}