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
    beacon_uri: Optional[str] = None
    beacon_harvest_timestamp: Optional[datetime] = None
    name: Optional[str] = None
    beacon_name: Optional[str] = None

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
    authority_ids: list[str] = Field(..., min_length=1, max_length=1000)
    limit_per_id: int = Field(default=100, ge=1, le=500)

    # exclusion list
    exclude_beacon_uris: list[str] = Field(
        default_factory=list,
        description="Exclude rows where beacon_uri is in this list.",
    )

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
                    "1209690195",
                    "118526642",
                ],
                "limit_per_id": 50,
                "exclude_beacon_uris": [
                    "http://tools.wmflabs.org/persondata/beacon/dewiki.txt",
                    "http://tools.wmflabs.org/persondata/beacon/dewiki_commons.txt",
                    "http://www.ixtheo.de/docs/ixtheo-beacon.txt",
                ],
            }
        }
    }


class BatchAuthorityResponse(BaseModel):
    requested: int
    returned: int
    missing: list[str]
    items_by_authority: dict[str, list[dict]]


class DistinctItem(BaseModel):
    beacon_uri: Optional[str] = None
    beacon_name: Optional[str] = None


class BeaconsResponse(BaseModel):
    count: int
    items: list[DistinctItem]