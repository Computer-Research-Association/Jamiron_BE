from fastapi import FastAPI
from src.app.auth.router import router as auth_router
from src.app.syllabus.router import router as syllabus_router
from src.app.classifier.router import router as classifier_router
from src.app.user.router import router as user_router
from src.app.config.database import engine, test_connection
from src.app.model import Base  # models에서 Base import
#import logging

app = FastAPI()
#logging.basicConfig(level=logging.INFO)

app.include_router(auth_router)
app.include_router(syllabus_router, prefix="/api/login")
app.include_router(user_router, prefix="/api/user")
app.include_router(classifier_router, prefix="/api/classifier")


# 앱 시작시 연결 테스트
@app.on_event("startup")
async def startup_event():
    #logging.info("🚀 Starting Jamiron classifier server...")
    if test_connection():
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
    else:
        print("❌ Failed to connect to database")

@app.get("/")
def root():
    return {"message": "Jamiron classifier server running 🚀"}

# 연결 테스트를 위한 엔드포인트
@app.get("/health/db")
def database_health():
    '''testtest'''
    if test_connection():
        return {"status": "healthy", "database": "connected"}
    else:
        return {"status": "unhealthy", "database": "disconnected"}