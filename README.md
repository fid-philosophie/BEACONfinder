# BEACONfinder
Findbuch service that exposes BEACONaggregator output via a small FastAPI API backed by MongoDB.

## What this repo contains
- `app/`: FastAPI app with MongoDB access and REST endpoints.
- `scripts/import_parquet.py`: one-off importer from a merged BEACON Parquet file into MongoDB.
- `requirements.txt`: runtime dependencies.
- optionally [MongoDB](https://github.com/mongodb/mongo) (if you don't have a MongoDB yet) and/or [BunkerWeb](https://github.com/bunkerity/bunkerweb) (for safety measures)



## Environment variables
Create a `.env` file in the repo root (or use the `.env.example`):
There are 4 different setups you can choose from.
- setup 1: just the BEACONfinder API (if you already have an instance of MongoDB running)
- setup 2: adding MongoDB only
- setup 3: adding BunkerWeb only
- setup 4: adding a MongoDB instance and BunkerWeb
You can choose a setup via uncommenting the chosen setup and commenting out the others.
Depending on the chosen setup you will need to configure different variables (e.g. for connecting MongoDB).

```
### App
APP_HOST=0.0.0.0
CONTAINER_PORT=8000
HOST_PORT=8000

## Empty locally; e.g. use /api when exposed below /api via reverse proxy
APP_ROOT_PATH=

## Required for setups using BunkerWeb (setups 3 & 4)
DNS_ALIAS=<DNS_ALIAS>

# -----------------------------------------------------------------------------

### Importer
PARQUET_FILE=data/beacons_merged_latest.parquet

# -----------------------------------------------------------------------------

### Debugging
ENABLE_DEBUG_ENDPOINTS=false

# -----------------------------------------------------------------------------

### Compose setup

## Base only (setup 1)
COMPOSE_FILE=compose.yaml

## Local MongoDB (setup 2)
# COMPOSE_FILE=compose.yaml:compose.mongodb.yaml

## BunkerWeb (setup 3)
# COMPOSE_FILE=compose.yaml:compose.bunkerweb.yaml

## Local MongoDB + BunkerWeb (setup 4)
# COMPOSE_FILE=compose.yaml:compose.mongodb.yaml:compose.bunkerweb.yaml

# -----------------------------------------------------------------------------

### MongoDB

## Mongo - local Docker setup (setups 2 & 4)
MONGO_ROOT_USER=root
MONGO_ROOT_PASSWORD=example

MONGO_APP_USER=appuser
MONGO_APP_PASSWORD=apppass
MONGO_APP_DB=mydb
MONGO_APP_COLLECTION=records
MONGO_HOST_PORT=27017
MONGO_CONTAINER_PORT=27017

## Mongo - existing server DB (setups 1 & 3)
MONGODB_URI=mongodb://<ADMIN_USER>:<ADMIN_PASSWORD>@host.docker.internal:27017/<DB_NAME>?authSource=admin
MONGODB_DB=<DB_NAME>
MONGODB_COLLECTION=records
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
- if you changed the port in `.env` you should change it here, too
- if you changed app root in `.env` you should change/add it here, too (e.g. http://127.0.0.1:8000/api/docs)