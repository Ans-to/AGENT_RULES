FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/models/huggingface

RUN set -eux; \
    for attempt in 1 2 3; do \
      apt-get update -o Acquire::Retries=5 \
      && apt-get install -y --no-install-recommends -o Acquire::Retries=5 \
        ffmpeg \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-chi-sim \
        ca-certificates \
      && break; \
      if [ "$attempt" = "3" ]; then exit 1; fi; \
      rm -rf /var/lib/apt/lists/*; \
      sleep 5; \
    done; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "scripts/video_analysis.py"]

FROM base AS asr
COPY requirements-asr.txt ./
RUN pip install --no-cache-dir -r requirements-asr.txt \
    && mkdir -p /models/huggingface
ARG PRELOAD_ASR_MODEL=none
RUN if [ "$PRELOAD_ASR_MODEL" != "none" ]; then \
      python scripts/doctor.py --profile asr --download-asr-model "$PRELOAD_ASR_MODEL" --asr-model "$PRELOAD_ASR_MODEL"; \
    fi

FROM base AS final
