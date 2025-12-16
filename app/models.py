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

# GET single authority_id
class QueryRequest(BaseModel):
    id: str
    strings: list[str] = Field(default_factory=list)
    # easy toggle: which field to match for the id
    id_field: str = Field(default="target_id")  # or "authority_id"
    limit: int = Field(default=100, ge=1, le=500)


class QueryResponse(BaseModel):
    count: int
    items: list[Record]


# POST batch authority_id
class BatchAuthorityRequest(BaseModel):
    authority_ids: list[str]
    limit_per_id: int = 100

    model_config = {
        "json_schema_extra": {
            "example": {
                "authority_ids": [
                    "111116961",
                    "129958212",
                    "118559796",
                    "116233680",
                    "11652538X",
                    "2091666-8",
                ],
                "limit_per_id": 50,
            }
        }
    }

class BatchAuthorityResponse(BaseModel):
    requested: int
    returned: int
    missing: list[str]
    items_by_authority: dict[str, list[dict]]