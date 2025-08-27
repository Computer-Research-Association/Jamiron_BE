from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.app.classifier.service import get_user_syllabuses
from src.app.classifier.service import classify_with_rule_and_ml  # service 함수 임포트
from src.app.config.database import get_db
from sqlalchemy.orm import Session
from typing import List, Dict, Any,Optional

router = APIRouter()

class FileData(BaseModel):
    file_name: str
    ml_content: str
    rule_based_content: str
    label: Optional[str] = None

@router.post("/classify")
async def classify_files(
    files: List[FileData],
    user_id: str,
    year: str,
    semester: str,
    db: Session = Depends(get_db)
):

    file_dicts = [file.dict() for file in files]
    syllabuses = get_user_syllabuses(db, user_id, year, semester)
    if not syllabuses:
        raise HTTPException(
            status_code=404,
            detail=f"User ID '{user_id}', Year '{year}', Semester '{semester}'에 대한 강의 계획서를 찾을 수 없습니다."
        )

    result = classify_with_rule_and_ml(
        file_dicts,
        db=db,
        syllabus_list=syllabuses
    )

    # 3. 응답 반환
    simplified_result = [
        {"file_name": item["file_name"], "label": item.get("label")}
        for item in result
    ]

    # 4. 응답 반환
    return {
        "status": 200,
        "message": "파일 분류 성공.",
        "file_data_list": simplified_result
    }
