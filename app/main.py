from fastapi import FastAPI

from app.src.api.routers import router as api_router


app = FastAPI(title="Media Censorship Service")

# 🔥 Healthcheck endpoint
@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router, prefix="/process")
