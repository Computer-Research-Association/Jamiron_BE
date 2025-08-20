# src/app/config/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import logging

# 로깅 설정으로 SQLAlchemy 연결 상태 확인
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

DATABASE_URL = "mysql+mysqlconnector://root:1234@localhost:3306/jamiron"

# 연결 옵션 추가
engine = create_engine(
    DATABASE_URL,
    echo=True,  # SQL 쿼리 로깅
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=3600,   # 연결 재사용 시간
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 연결 테스트 함수
def test_connection():
    try:
        connection = engine.connect()
        print("✅ Database connection successful!")
        connection.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False