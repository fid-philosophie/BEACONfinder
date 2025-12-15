from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class Record(BaseModel):
    # MongoDB _id is optional here; we return it as a string when present
    id: Optional[str] = Field(default=None, alias="_id")

    target_uri: Optional[str] = None
    authority_uri: Optional[str] = None
    target_parent_uri: Optional[str] = None
    authority_file_uri: Optional[str] = None
    target_id: Optional[str] = None
    authority_id: Optional[str] = None
    type: Optional[str] = None
    role: Optional[str] = None
    string: Optional[str] = None
    project: Optional[str] = None
    source_date: Optional[date] = None
    date_of_export: Optional[datetime] = None

    class Config:
        populate_by_name = True


class QueryRequest(BaseModel):
    id: str
    strings: list[str] = Field(default_factory=list)
    # easy toggle: which field to match for the id
    id_field: str = Field(default="target_id")  # or "authority_id"
    limit: int = Field(default=100, ge=1, le=500)


class QueryResponse(BaseModel):
    count: int
    items: list[Record]
