FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-libmysqlclient-dev pkg-config gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]