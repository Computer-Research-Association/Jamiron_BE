# src/app/main.py
from fastapi import FastAPI
from classifier.router import router as classifier_router

app = FastAPI()

# classifier 라우터 등록
app.include_router(classifier_router, prefix="/classifier")

@app.get("/")
def root():
    return {"message": "Jamiron classifier server running 🚀"}
