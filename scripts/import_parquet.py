import os
from pathlib import Path

import duckdb
from pymongo import MongoClient, InsertOne, ASCENDING

PARQUET = os.getenv("PARQUET_FILE", default="")
PARQUET_FOLDER = os.getenv("PARQUET_FOLDER", default="data")
MONGO_URI = os.getenv("MONGODB_URI", default = "mongodb://localhost:27017")
DB = os.getenv("MONGODB_DB", default = "mydb")
COLL = os.getenv("MONGODB_COLLECTION", default = "mycollection")

BATCH = 50_000  # tune: 10k–200k depending on row width / RAM

client = MongoClient(MONGO_URI)


collection = client[DB][COLL]

# flush existing records
collection.drop()

con = duckdb.connect()
con.execute("PRAGMA threads=4")  # optional

# Determine which parquet file to import
if PARQUET:
    parquet_path = Path(PARQUET)

    if not parquet_path.is_file():
        raise FileNotFoundError(
            f"PARQUET_FILE points to a file that does not exist: {parquet_path}"
        )
else:
    parquet_folder = Path(PARQUET_FOLDER)

    if not parquet_folder.is_dir():
        raise NotADirectoryError(
            f"PARQUET_FOLDER does not exist or is not a directory: {parquet_folder}"
        )

    parquet_files = sorted(parquet_folder.glob("*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(
            f"No .parquet files found in PARQUET_FOLDER: {parquet_folder}"
        )

    # alphabetically last parquet file
    parquet_path = parquet_files[-1]

print(f"Using parquet file: {parquet_path}")

con.execute(f"CREATE VIEW v AS SELECT * FROM read_parquet('{parquet_path.as_posix()}')")

# Give some feedback on which files and how many rows will be imported
print(f"PARQUET_FILE env: {PARQUET!r}")
print(f"PARQUET_FOLDER env: {PARQUET_FOLDER!r}")
print(f"Selected parquet file: {parquet_path.resolve()}")
total = con.execute("SELECT COUNT(*) FROM v").fetchone()[0]
print(f"About to import {total:,} rows")

inserted = 0
while True:
    # Fetch a chunk. ORDER BY is optional but helps deterministic paging.
    rel = con.sql(f"SELECT * FROM v LIMIT {BATCH} OFFSET {inserted}")
    rows = rel.fetchall()
    if not rows:
        break

    cols = [d[0] for d in rel.description]
    # convert batch to list[dict] for MongoDB
    docs = [dict(zip(cols, r)) for r in rows]

    # bulk write is faster than insert_many in many cases
    collection.bulk_write([InsertOne(d) for d in docs], ordered=False)

    inserted += len(rows)
    print(f"Inserted {inserted:,} rows")


mongo_count = collection.count_documents({})
print(f"MongoDB now contains: {mongo_count:,} documents")

# Give some feedback so people know what's happening + that the script is not dead
print(f"Finished importing rows, now creating the index...")

# single-field indexing
collection.create_index([("authority_id", ASCENDING)], name="authority_id_idx")
print("authority_id_idx created.")

# indexing for distinct beacons
collection.create_index([("beacon_uri", ASCENDING)], name="beacon_uri_idx")
print("beacon_uri_idx created.")
collection.create_index([("NAME", ASCENDING)], name="name_idx")
print("project_idx created.")

print("All indexes created.")