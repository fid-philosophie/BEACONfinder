# BEACONfinder
Findbuch service that exposes BEACONaggregator output via a small FastAPI API backed by MongoDB.

## What this repo contains
- `app/`: FastAPI app with MongoDB access and REST endpoints.
- `scripts/import_parquet.py`: one-off importer from a merged BEACON Parquet file into MongoDB.
- `requirements.txt`: runtime dependencies.




## Environment variables
Create a `.env` file in the repo root (or use the `.env.example`):
```
# Mongo - local Docker setup
MONGO_ROOT_USER=root
MONGO_ROOT_PASSWORD=example

MONGO_APP_USER=appuser
MONGO_APP_PASSWORD=apppass
MONGO_APP_DB=mydb
MONGO_APP_COLLECTION=records
MONGO_HOST_PORT=27017
MONGO_CONTAINER_PORT=27017

# Mongo - existing server DB
MONGODB_URI=mongodb://XXXADMIN:XXXPW@host.docker.internal:27017/XXXDB?authSource=admin
MONGODB_DB=XXXDB
MONGODB_COLLECTION=records

# Importer
PARQUET_FILE=data/beacons_merged_latest.parquet

# App
APP_HOST=0.0.0.0
CONTAINER_PORT=8000
HOST_PORT=8000
APP_ROOT_PATH=
```

## Getting started - via Docker (recommended)
(from within the project folder / your repo clone)

### Copy the `.env.example`

#### (Git Bash / macOS / Linux)
```bash
cp -n .env.example .env
```

#### (Windows PowerShell)
```bash
if (-Not (Test-Path .env)) {
    Copy-Item .env.example .env
}
```


### Get the newest aggregation (Parquet-file) and put it in `data/beacons_merged_latest.parquet`
```bash
...placeholder... (will update this when there is a stable url)
```

### Start MongoDB via Docker


#### Build and run (API + MongoDB)
```bash
docker compose up --build
```

#### Import data in Docker
Run the importer service against the Docker MongoDB (profiled):
```bash
docker compose --profile import run --rm importer
```

#### If you want to see the API logs
```bash
docker compose logs -f api
```

#### If you want to stop it
```bash
docker compose down
```

### Already got a MongoDB running somewhere?

Make sure to configure the .env accordingly!

#### Build and run (API + MongoDB)
```bash
docker compose -f docker-compose.server.yml up -d --build api
```

#### Import data in Docker
Run the importer service against the Docker MongoDB (profiled):
```bash
docker compose -f docker-compose.server.yml --profile import run --rm importer
```

#### If you want to see the API logs
```bash
docker compose -f docker-compose.server.yml logs -f api
```

#### If you want to see the status
```bash
docker compose -f docker-compose.server.yml ps
```

#### If you want to stop it
```bash
docker compose -f docker-compose.server.yml down
```


### Test the API locally
Open the Swagger UI at:
```
http://127.0.0.1:8000/docs
```
(if you changed the port in `.env` you should change it here, too)