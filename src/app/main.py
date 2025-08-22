from fastapi import FastAPI
from src.app.syllabus.router import router as syllabus_collector
from src.app.classifier.router import router as classifier_router
from src.app.auth.router import router as auth_router

app = FastAPI()
app.include_router(auth_router, tags=["auth"])
app.include_router(classifier_router,  tags=["classifier"])
app.include_router(syllabus_collector, tags=["syllabus"])
@app.get("/")
def root():
    return {"message": "Jamiron classifier server running 🚀"}