from fastapi import FastAPI
from app.config import settings
from app.routers.records import router as records_router

app = FastAPI(
    title="BEACONfinder API",
    root_path=settings.app_root_path,
    )

app.include_router(records_router)


@app.on_event("startup")
async def startup():
    # Intentionally empty:
    # indexes are created during the import process only
    pass