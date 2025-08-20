from fastapi import APIRouter
from service import ClassifierManager

router = APIRouter()

@router.post("/classify")
async def classify_files(files: list[dict]):
    manager = ClassifierManager(...)
    result = manager.run_pipeline(files)
    return {"classified_files": result}
