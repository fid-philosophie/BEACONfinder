FROM python:3.11.18-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# get certificates up to date
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# update pip
RUN python -m pip install --no-cache-dir \
    "pip>=26.2.2"

# get dependencies
COPY requirements.txt /app/
RUN python -m pip install --no-cache-dir -r requirements.txt

# check versions
RUN python -m pip check \
    && python -m pip --version \
    && python --version

# copy app & scripts into workdir
COPY app /app/app
COPY scripts/import_parquet.py /app/scripts/import_parquet.py

# default container port, config in .env
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host ${APP_HOST:-0.0.0.0} --port ${CONTAINER_PORT:-8000}"]
