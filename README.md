# BEACONfinder_PRIVATE
Findbuch service that exposes BEACONaggregator output via a small FastAPI API backed by MongoDB.

## What this repo contains
- `app/`: FastAPI app with MongoDB access and REST endpoints.
- `import_parquet.py`: one-off importer from a merged BEACON Parquet file into MongoDB.
- `requirements.txt`: runtime dependencies.

## Prerequisites
- Python 3.10+
- MongoDB server (local or remote)
- `mongosh` (optional, but useful for inspecting the database)

## MongoDB setup
You can use any MongoDB instance. Example setup used by this project:
- database: `mydb`
- collection: `records`
- app user with read/write on `mydb`: `appuser` / `apppass`

### `mongosh` on Ubuntu/WSL (optional)
```bash
mongosh --version
sudo apt update
sudo apt install -y mongodb-mongosh
```

## Environment variables
Create a `.env` file in the repo root:
```
mongodb_uri=mongodb://appuser:apppass@localhost:27017/mydb?authSource=mydb
mongodb_db=mydb
mongodb_collection=records
```

## Getting started
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Importing BEACONaggregator output
1. Place the merged Parquet file in a data directory (recommended: `data/`).
2. Update `PARQUET` in `import_parquet.py` to point to that file.
3. Run the importer:
   ```bash
   python import_parquet.py
   ```
The importer loads the Parquet file in batches and creates an index on `authority_id`.

## Run the API
```bash
python -m uvicorn app.main:app --reload
```

## Test the API
Open the Swagger UI at:
```
http://127.0.0.1:8000/docs
```
