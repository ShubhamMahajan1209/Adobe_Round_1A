# ───────────────── Round‑1A container ─────────────────
# * Platform‑locked to linux/amd64
# * Tiny image: python:3.11‑slim + PyMuPDF
# * Works 100 % offline (no network calls after build)
# ------------------------------------------------------
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app/extractor.py app/run.sh /app/
RUN chmod +x run.sh

ENTRYPOINT ["./run.sh"]
