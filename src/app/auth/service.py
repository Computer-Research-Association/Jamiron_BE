from fastapi import HTTPException, Depends
from src.app.auth.session_factory import generate_session_id, create_session
from src.app.syllabus.service import SyllabusCollector, get_syllabus_collector


def authenticate_and_create_session(req, collector: SyllabusCollector = Depends(get_syllabus_collector)):
    if not collector.login(req.username, req.password.get_secret_value()):
        # 로그인 시도 실패하면 실패 반환
        raise HTTPException (401,"로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.")
    # 로그인 시도 성공하면 아이디만 db에 저장
    save_user(req.username)

    # 세션 id 발급
    session_id = generate_session_id()
    print(session_id)

    # redis에 세션 저장
    create_session(session_id, user_id=req.username)
    return session_id

def save_user(username):
    pass