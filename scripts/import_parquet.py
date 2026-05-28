import os
from pathlib import Path

import duckdb
from pymongo import MongoClient, InsertOne, ASCENDING

PARQUET = os.getenv("PARQUET_FILE", default = "data/beacons_merged_latest.parquet")
MONGO_URI = os.getenv("MONGODB_URI", default = "mongodb://localhost:27017")
DB = os.getenv("MONGODB_DB", default = "mydb")
COLL = os.getenv("MONGODB_COLLECTION", default = "mycollection")

BATCH = 50_000  # tune: 10k–200k depending on row width / RAM


# uri = "mongodb://root:example@localhost:27017/?authSource=admin"
# client = MongoClient(
#     host="localhost",
#     port=27017,
#     username="root",
#     password="example",
#     authSource="admin",
# )

client = MongoClient(MONGO_URI)


collection = client[DB][COLL]

# flush existing records
collection.drop()

#client = MongoClient(MONGO_URI)
#collection = client[DB][COLL]

con = duckdb.connect()
con.execute("PRAGMA threads=4")  # optional

# DuckDB can read parquet directly; no pandas dataframe involved
parquet_path = Path(PARQUET)
con.execute(f"CREATE VIEW v AS SELECT * FROM read_parquet('{parquet_path.as_posix()}')")

# Give some feedback on how many rows will be imported
total = con.execute("SELECT COUNT(*) FROM v").fetchone()[0]
print(f"About to import {total:,} rows")

offset = 0
while True:
    # Fetch a chunk. ORDER BY is optional but helps deterministic paging.
    rel = con.sql(f"SELECT * FROM v LIMIT {BATCH} OFFSET {offset}")
    rows = rel.fetchall()
    if not rows:
        break

    cols = [d[0] for d in rel.description]
    # convert batch to list[dict] for MongoDB
    docs = [dict(zip(cols, r)) for r in rows]

    # bulk write is faster than insert_many in many cases
    collection.bulk_write([InsertOne(d) for d in docs], ordered=False)

    offset += BATCH
    print(f"Inserted {offset:,} rows")

# Give some feedback so people know what's happening + that the script is not dead
print(f"Finished importing rows, now creating the index...")

# single-field indexing
collection.create_index([("authority_id", ASCENDING)], name="authority_id_idx")
print("authority_id_idx created.")

# indexing for distinct beacons
# collection.create_index([("beacon_uri", ASCENDING)], name="beacon_uri_idx")
# print("beacon_uri_idx created.")
# collection.create_index([("NAME", ASCENDING)], name="name_idx")
# print("project_idx created.")
collection.create_index(
    [("beacon_uri", ASCENDING), ("NAME", ASCENDING)],
    name="beacon_uri_name_idx",
)

print("All indexes created.")