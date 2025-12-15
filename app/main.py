from fastapi import FastAPI
from app.routers.records import router as records_router
from app.db import get_collection

app = FastAPI(title="MongoDB Records API")

app.include_router(records_router)


@app.on_event("startup")
async def startup():
    # Create helpful indexes (safe to call repeatedly)
    col = get_collection()
    await col.create_index("target_id")
    await col.create_index("authority_id")
    await col.create_index("string")
