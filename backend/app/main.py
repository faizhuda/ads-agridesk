from fastapi import FastAPI
from app.controllers import surat_controller
from app.controllers import auth_controller

app = FastAPI(title="Agridesk API")

@app.get("/")
def root():
    return {"message": "Agridesk API is running"}

app.include_router(auth_controller.router)
app.include_router(surat_controller.router)