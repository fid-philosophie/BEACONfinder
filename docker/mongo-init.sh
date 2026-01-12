#!/usr/bin/env bash
set -euo pipefail

: "${MONGO_APP_DB:=mydb}"
: "${MONGO_APP_USER:=appuser}"
: "${MONGO_APP_PASSWORD:=apppass}"

mongosh --username "$MONGO_INITDB_ROOT_USERNAME" \
  --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase "admin" <<EOF
db = db.getSiblingDB("$MONGO_APP_DB");

if (db.getUser("$MONGO_APP_USER") == null) {
  db.createUser({
    user: "$MONGO_APP_USER",
    pwd: "$MONGO_APP_PASSWORD",
    roles: [{ role: "readWrite", db: "$MONGO_APP_DB" }],
  });
} else {
  print("User $MONGO_APP_USER already exists in DB $MONGO_APP_DB, skipping");
}
EOF