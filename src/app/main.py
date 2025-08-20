from fastapi import FastAPI
from .login.router import router as login_router
from .classifier.router import router as classifier_router

app = FastAPI()
app.include_router(login_router, prefix="/api/login", tags=["Authentication"])
app.include_router(classifier_router, prefix="/api/classifier")
@app.get("/")
def root():
    return {"message": "Jamiron classifier server running 🚀"}
