from typing import Any
from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.db import get_collection
from app.models import Record, QueryRequest, QueryResponse

router = APIRouter(prefix="/records", tags=["records"])


def _serialize(doc: dict[str, Any]) -> dict[str, Any]:
    # Convert MongoDB ObjectId to string for JSON
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("/{record_id}", response_model=Record)
async def get_by_id(record_id: str, id_field: str = "target_id"):
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


@router.post("/query", response_model=QueryResponse)
async def query_records(payload: QueryRequest):
    """
    Query by:
      - payload.id against payload.id_field
      - payload.strings against 'string' field using $in
    """
    if payload.id_field not in {"target_id", "authority_id"}:
        raise HTTPException(status_code=400, detail="id_field must be target_id or authority_id")

    col = get_collection()

    query: dict[str, Any] = {payload.id_field: payload.id}
    if payload.strings:
        query["string"] = {"$in": payload.strings}

    cursor = col.find(query).limit(payload.limit)
    docs = [ _serialize(d) async for d in cursor ]
    return QueryResponse(count=len(docs), items=docs)
