import duckdb
from pymongo import MongoClient, InsertOne

PARQUET = "beacons_merged_20251215-1848.parquet"
MONGO_URI = "mongodb://localhost:27017"
DB, COLL = "mydb", "mycollection"

BATCH = 50_000  # tune: 10k–200k depending on row width / RAM

client = MongoClient(MONGO_URI)
collection = client[DB][COLL]

con = duckdb.connect()
con.execute("PRAGMA threads=4")  # optional

# DuckDB can read parquet directly; no pandas dataframe involved
con.execute(f"CREATE VIEW v AS SELECT * FROM read_parquet('{PARQUET}')")

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
