from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import ensure_indexes
from app.routers import upload, readings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ensure_indexes()
    yield


app = FastAPI(title="Sensor Temp/Humidity Monitor API", lifespan=lifespan)

# Cho phép Angular dev server (http://localhost:4200) gọi API.
# Khi deploy thật, nên thay "*" bằng domain cụ thể của frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(readings.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
