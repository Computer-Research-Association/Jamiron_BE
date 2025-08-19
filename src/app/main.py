from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .classifier.router import router as classifier_router

app = FastAPI()

# CORS 미들웨어는 정적 파일을 제공할 때는 필요 없지만, API 통신을 위해 유지합니다.
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# classifier_router를 마운트합니다.
app.include_router(classifier_router, prefix="/api/v1")

# 'static' 디렉터리를 '/static' 경로로 마운트하여 정적 파일을 제공합니다.
app.mount("/static", StaticFiles(directory="static"), name="static")

# 기본 경로(http://127.0.0.1:8000/)에 접속하면 index.html을 반환하는 엔드포인트를 추가합니다.
@app.get("/")
def serve_html():
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# 기존의 API 라우터는 그대로 유지됩니다.
# @app.get("/")
# def read_root():
#     return {"message": "Welcome to the file classification API"}