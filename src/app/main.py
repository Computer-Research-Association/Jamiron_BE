from fastapi import FastAPI
from .login.router import router as auth_router
from .classifier.router import router as classifier_router

app = FastAPI()
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(classifier_router, prefix="/classifier")
@app.get("/")
def root():
    return {"message": "Jamiron classifier server running 🚀"}
