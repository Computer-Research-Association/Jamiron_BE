from fastapi import APIRouter
from pydantic import BaseModel
from ..login.service import SyllabusCollector

router = APIRouter()

# 요청 데이터의 유효성을 검사할 모델
class LoginRequest(BaseModel):
    user_id: str
    password: str
    year: int
    semester: str

@router.post("/")
async def login(credentials: LoginRequest):
    # 요청마다 SyllabusCollector 인스턴스를 새로 생성
    collector = SyllabusCollector()
    
    try:
        # Selenium 로그인 로직 실행
        success = collector.login(credentials.user_id, credentials.password)
        
        if success:
            return {"message": 200}
        else:
            return {"message": 401}
            
    except Exception as e:
        return {"error": 404}
        
    finally:
        # 작업 완료 후 드라이버를 반드시 종료
        collector.close()