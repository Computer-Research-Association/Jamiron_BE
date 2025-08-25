from fastapi import HTTPException, Response
from src.app.session.service import new_token, create_session
from src.app.syllabus.service import SyllabusCollector

def login(body: LoginIn, res: Response):
    collector = SyllabusCollector()
    if not collector.login(body.user_id, body.password.get_secret_value()):
        # 로그인 시도 실패하면 실패 반환
        raise HTTPException (401,"로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.")
    # 로그인 시도 성공하면 아이디만 db에 저장

    # 토큰 발급. 고유한 id
    token = new_token()
    # redis에 user id랑 고유한 토큰 id 전달
    await create_session(token, user_id=body.user_id)
    # 프로그램 환경이라 쿠키 대신 헤더/바디로 토큰을 전달
    return LoginOut(session_token=token)