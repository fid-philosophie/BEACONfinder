# BEACONfinder_PRIVATE
Findbuch service that exposes BEACONaggregator output via a small FastAPI API backed by MongoDB.

## What this repo contains
- `app/`: FastAPI app with MongoDB access and REST endpoints.
- `scripts/import_parquet.py`: one-off importer from a merged BEACON Parquet file into MongoDB.
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

# importer defaults (optional)
MONGODB_URI=mongodb://appuser:apppass@localhost:27017/mydb?authSource=mydb
MONGODB_DB=mydb
MONGODB_COLLECTION=records
PARQUET_FILE=data/beacons_merged_latest.parquet

# docker-compose defaults
MONGO_ROOT_USER=root
MONGO_ROOT_PASSWORD=example
MONGO_APP_DB=mydb
MONGO_APP_USER=appuser
MONGO_APP_PASSWORD=apppass
MONGO_APP_COLLECTION=records
```

## Getting started
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Importing BEACONaggregator output
1. Place the merged Parquet file in `data/` (recommended).
2. Set `PARQUET_FILE` in `.env` if the filename differs.
3. Run the importer:
   ```bash
   python scripts/import_parquet.py
   ```
The importer loads the Parquet file in batches and creates an index on `authority_id`.

## Run the API
```bash
python -m uvicorn app.main:app --reload
```

## Docker
### Build and run (API + MongoDB)
```bash
docker compose up --build
```

### Import data in Docker
Run the importer service against the Docker MongoDB (profiled):
```bash
docker compose --profile import run --rm importer
```

## Test the API
Open the Swagger UI at:
```
http://127.0.0.1:8000/docs
```
