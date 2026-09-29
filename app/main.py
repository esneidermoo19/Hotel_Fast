from fastapi import FastAPI

from app.config import settings
from app.controllers import auth, habitaciones

app = FastAPI(title=settings.app_name)
app.include_router(auth.router)
app.include_router(habitaciones.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
