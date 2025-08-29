from fastapi import HTTPException
from src.app.auth.session_factory import generate_session_id, create_session
from sqlalchemy.orm import Session
from src.app.model import UserName
from src.app.syllabus.service import SyllabusCollector


def authenticate_and_create_session(
        req,
        db: Session,
        collector: SyllabusCollector
):
    if not collector.login(req.username, req.password.get_secret_value()):
        raise HTTPException(401, "로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.")

    save_user(req.username, db)
    session_id = generate_session_id()
    create_session(session_id, user_name=req.username)

    return session_id


def save_user(username: str, db: Session):
    existing_user = db.query(UserName).filter(UserName.user_id == username).first()
    if existing_user:
        return existing_user

    new_user = UserName(user_name=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
