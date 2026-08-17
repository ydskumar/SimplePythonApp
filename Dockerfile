FROM python:3.13-slim

ARG BUILD_DATE="unknown"
ARG VCS_REF="unknown"
ARG VERSION="unknown"
ARG BUILD_URL="unknown"

LABEL org.opencontainers.image.title="SimplePythonApp" \
      org.opencontainers.image.description="Simple Python Flask application" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.url="${BUILD_URL}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8081

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && adduser --system --group --home /app appuser \
    && chown appuser:appuser /app

COPY --chown=appuser:appuser . .

EXPOSE 8081

USER appuser

CMD [ "python", "run.py" ]