from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import auth_controller, surat_controller, signature_controller, verification_controller

app = FastAPI(
    title="Agridesk API",
    description="Academic Letter Workflow System",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_controller.router)
app.include_router(surat_controller.router)
app.include_router(signature_controller.router)
app.include_router(verification_controller.router)


@app.get("/")
def root():
    return {"message": "Agridesk API is running"}
