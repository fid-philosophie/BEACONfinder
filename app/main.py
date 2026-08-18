from fastapi import FastAPI, Request
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

@app.get("/debug/client-ip")
async def debug_client_ip(request: Request):
    return {
        "client_host": request.client.host if request.client else None,
        "x_forwarded_for": request.headers.get("x-forwarded-for"),
        "x_real_ip": request.headers.get("x-real-ip"),
        "forwarded": request.headers.get("forwarded"),
    }