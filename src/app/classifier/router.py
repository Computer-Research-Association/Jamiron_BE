# src/app/classifier/router.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

# service.py에서 classify_with_ml 함수를 정상적으로 가져올 수 있게 됩니다.
from .service import classify_with_ml 

router = APIRouter()

class FileData(BaseModel):
    file_name: str
    label: str
    content: str # 예시로 content 필드를 추가했습니다.

@router.post("/classify")
def classify_files(file_data_list: List[FileData]):
    # Pydantic 모델을 딕셔너리 리스트로 변환
    data_for_classification = [file_data.dict() for file_data in file_data_list]
    
    # classify_with_ml 함수를 호출하여 분류를 수행합니다.
    classified_data = classify_with_ml(data_for_classification)
    
    return {"message": "Files classified successfully", "classified_data": classified_data}