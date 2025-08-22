# src/app/classifier/router.py

from fastapi import APIRouter
from typing import List, Dict

# service.py에서 classify_with_ml 함수를 직접 임포트합니다.
from .service import classify_with_ml

router = APIRouter()

@router.post("/api/classify")
async def classify_files(files: List[Dict]):
    """
    파일 분류를 위한 API 엔드포인트입니다.
    service 레이어의 classify_with_ml 함수를 직접 호출하여 분류를 수행합니다.
    """
    result = classify_with_ml(files)
    
    return {"classified_files": result}