from typing import Any
import asyncio

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Path, Query

from app.db import get_collection
from app.models import (
    BatchAuthorityRequest,
    BatchAuthorityResponse,
    BeaconsResponse,
)

router = APIRouter(prefix="/records", tags=["records"])

_distinct_values_cache: dict | None = None

def _serialize(doc: dict[str, Any]) -> dict[str, Any]:
    """Convert MongoDB types to JSON-friendly values."""
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc



# ----------------------------
# Return distinct name/beacon_uris 
# ----------------------------
@router.get("/beacons", response_model=BeaconsResponse)
async def get_beacons():
    global _distinct_values_cache

    if _distinct_values_cache is not None:
        return _distinct_values_cache

    col = get_collection()

    pipeline = [
        {
            "$group": {
                "_id": {
                    "beacon_uri": "$beacon_uri",
                    "project": "$NAME",
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "beacon_uri": "$_id.beacon_uri",
                "project": "$_id.project",
            }
        },
        {
            "$sort": {
                "project": 1,
                "beacon_uri": 1,
            }
        },
    ]

    items = []
    async for doc in col.aggregate(pipeline, allowDiskUse=True):
        items.append({
            "beacon_uri": doc.get("beacon_uri"),
            "project": doc.get("project"),
        })

    _distinct_values_cache = {
        "count": len(items),
        "items": items,
    }

    return _distinct_values_cache


# ----------------------------
# Batch query by authority_id
# ----------------------------
@router.post("/by-authority/batch", response_model=BatchAuthorityResponse)
async def get_by_authority_batch(payload: BatchAuthorityRequest):
    """
    Query many authority_ids in one request using $in.
    Supports exclusion list via beacon_uri ($nin).
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

    # Build query
    query: dict[str, Any] = {"authority_id": {"$in": ids}}

    # apply exclusion list: beacon_uri NOT IN exclude_beacon_uris
    if payload.exclude_beacon_uris:
        ex = [u.strip() for u in payload.exclude_beacon_uris if u and u.strip()]
        if ex:
            query["beacon_uri"] = {"$nin": ex}

    cursor = col.find(query)
    docs = [_serialize(d) async for d in cursor]

    # Group results by authority_id (and keep requested order)
    items_by_authority: dict[str, list[dict[str, Any]]] = {aid: [] for aid in ids}
    for d in docs:
        aid = d.get("authority_id")
        if isinstance(aid, str) and aid in items_by_authority:
            items_by_authority[aid].append(d)

    # Optional cap per authority_id (safety against huge responses)
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
    # exclusion list as repeated query parameter:
    # /by-authority/123?exclude_beacon_uris=a&exclude_beacon_uris=b
    exclude_beacon_uris: list[str] = Query(
        default_factory=list,
        description="Exclude rows where beacon_uri is in this list.",
        example=["http://tools.wmflabs.org/persondata/beacon/dewiki.txt"],
    ),
    limit: int = Query(200, ge=1, le=2000),
    skip: int = Query(0, ge=0),
):
    col = get_collection()

    query: dict[str, Any] = {"authority_id": authority_id}

    if exclude_beacon_uris:
        ex = [u.strip() for u in exclude_beacon_uris if u and u.strip()]
        if ex:
            query["beacon_uri"] = {"$nin": ex}

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
