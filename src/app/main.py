from fastapi import FastAPI
from .login.router import router as login_router
from .classifier.router import router as classifier_router
from .config.database import engine, test_connection
from .model import Base  # models에서 Base import
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
# 앱 시작시 연결 테스트
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Jamiron classifier server...")
    if test_connection():
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    else:
        print("❌ Failed to connect to database")

app.include_router(login_router, prefix="/api/login")
app.include_router(classifier_router, prefix="/api/classifier")

@app.get("/")
def root():
    return {"message": "Jamiron classifier server running 🚀"}

# 연결 테스트를 위한 엔드포인트
@app.get("/health/db")
def database_health():
    if test_connection():
        return {"status": "healthy", "database": "connected"}
    else:
        return {"status": "unhealthy", "database": "disconnected"}