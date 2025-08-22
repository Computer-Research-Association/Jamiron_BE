from fastapi import APIRouter
from pydantic import BaseModel
router = APIRouter()

class LoginInput(BaseModel):


@router.post("api/login")
