from fastapi import HTTPException
from src.app.auth.session_factory import new_token, create_session
from src.app.login.service import SyllabusCollector

def login(req):
    collector = SyllabusCollector()
    if not collector.login(req.username, req.password.get_secret_value()):
        # 로그인 시도 실패하면 실패 반환
        raise HTTPException (401,"로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.")
    # 로그인 시도 성공하면 아이디만 db에 저장
    save_db(req.username)

    # 토큰 발급. 고유한 id
    token = new_token()

    # redis에 세션 저장
    create_session(token, user_id=req.user_id)
    return token

def save_db(username):
    pass