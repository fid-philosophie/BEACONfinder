from typing import Any
from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from app.db import get_collection

router = APIRouter(prefix="/records", tags=["records"])


def _serialize(doc: dict[str, Any]) -> dict[str, Any]:
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("/by-authority/{authority_id}")
async def get_by_authority_id(
    authority_id: str,
    limit: int = Query(200, ge=1, le=2000),
    skip: int = Query(0, ge=0),
):
    col = get_collection()

    # Filter: exakt authority_id matchen
    query = {"authority_id": authority_id}

    cursor = col.find(query).skip(skip).limit(limit)
    docs = [_serialize(d) async for d in cursor]

    if not docs:
        raise HTTPException(status_code=404, detail="No records for this authority_id")

    return {
        "authority_id": authority_id,
        "count": len(docs),
        "items": docs,
        "skip": skip,
        "limit": limit,
    }
