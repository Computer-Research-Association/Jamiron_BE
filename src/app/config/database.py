from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv
import logging
import os

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
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
        connection.close()
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False