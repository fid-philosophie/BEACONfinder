from typing import Any

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Path, Query

from app.db import get_collection
from app.models import (
    BatchAuthorityRequest,
    BatchAuthorityResponse,
)

router = APIRouter(prefix="/records", tags=["records"])


def _serialize(doc: dict[str, Any]) -> dict[str, Any]:
    """Convert MongoDB types to JSON-friendly values."""
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc


# ----------------------------
# Batch query by authority_id
# ----------------------------
@router.post("/by-authority/batch", response_model=BatchAuthorityResponse)
async def get_by_authority_batch(payload: BatchAuthorityRequest):
    """
    Query many authority_ids in one request using $in.
    Returns items grouped by authority_id and a list of missing IDs.
    """
    col = get_collection()

    # de-duplicate while preserving order; trim whitespace; drop empty
    seen: set[str] = set()
    ids: list[str] = []
    for raw in payload.authority_ids:
        x = raw.strip()
        if not x:
            continue
        if x not in seen:
            seen.add(x)
            ids.append(x)

    if not ids:
        raise HTTPException(status_code=400, detail="authority_ids must not be empty")

    # One query for the whole batch
    query = {"authority_id": {"$in": ids}}

    cursor = col.find(query)
    docs = [_serialize(d) async for d in cursor]

    # Group results by authority_id (and keep requested order)
    items_by_authority: dict[str, list[dict[str, Any]]] = {aid: [] for aid in ids}
    for d in docs:
        aid = d.get("authority_id")
        if isinstance(aid, str) and aid in items_by_authority:
            items_by_authority[aid].append(d)

    # Optional cap per authority_id (safety against huge responses)
    if payload.limit_per_id:
        for aid in items_by_authority:
            items_by_authority[aid] = items_by_authority[aid][: payload.limit_per_id]

    missing = [aid for aid in ids if len(items_by_authority[aid]) == 0]
    returned = sum(len(v) for v in items_by_authority.values())

    return BatchAuthorityResponse(
        requested=len(ids),
        returned=returned,
        missing=missing,
        items_by_authority=items_by_authority,
    )


# ----------------------------
# Single query by authority_id
# ----------------------------
@router.get("/by-authority/{authority_id}")
async def get_by_authority_id(
    authority_id: str = Path(
        ...,
        description="Authority identifier (e.g. GND).",
        example="11652538X",
    ),
    limit: int = Query(200, ge=1, le=2000),
    skip: int = Query(0, ge=0),
):
    col = get_collection()
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


# ----------------------------
# Generic fetch by id field
# ----------------------------
@router.get("/{record_id}")
async def get_by_id(
    record_id: str,
    id_field: str = Query("target_id", description="Which field to match: target_id or authority_id"),
):
    """
    Fetch a single record by a string ID field (default: target_id).
    """
    if id_field not in {"target_id", "authority_id"}:
        raise HTTPException(status_code=400, detail="id_field must be target_id or authority_id")

    col = get_collection()
    doc = await col.find_one({id_field: record_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Record not found")

    return _serialize(doc)
