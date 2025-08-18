from fastapi import FastAPI
from src.app.presentation.routers import user_router

app = FastAPI(title="Jamiron Backend")

# 라우터 등록
app.include_router(user_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to Jamiron!"}
