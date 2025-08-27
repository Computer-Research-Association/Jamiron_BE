from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

from src.app.classifier.service import classify_with_rule_and_ml  # service 함수 임포트
from src.app.config.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends


router = APIRouter()

class FileData(BaseModel):
    file_name: str
    all_content: str
    first_content: str
    title: str
    author: str

@router.post("/classify")
async def classify_files(
    files: List[FileData],
    db: Session = Depends(get_db)
):

    file_dicts = [file.dict() for file in files]

    result = classify_with_rule_and_ml(file_dicts, db=db)

    return {"classified_files": result}