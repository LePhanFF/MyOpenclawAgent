# syntax=docker/dockerfile:1.4

FROM python:3.12-slim as base

# Install system dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
# Docker and DinD
    docker.io \
    docker-cli \
    ca-certificates \
    # Development tools
    git \
    curl \
    wget \
    # Discord dependencies
    libopus0 \
    libffi-dev \
    libssl-dev \
    # Audio dependencies for Discord voice (optional)
    libsodium-dev \
    libopus-dev \
    # Build dependencies
    build-essential \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Modify existing docker group to match host GID (988) and create non-root user
RUN groupmod -g 988 docker && \
    useradd -m -u 1000 -s /bin/bash openclaw && \
    usermod -aG docker openclaw

WORKDIR /app

# Install Python dependencies
COPY requirements.txt* ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=openclaw:openclaw src/ ./src/
COPY --chown=openclaw:openclaw scripts/ ./scripts/
COPY --chown=openclaw:openclaw config/ ./config/
COPY --chown=openclaw:openclaw entrypoint.sh ./
COPY --chown=openclaw:openclaw requirements.txt ./

# Set proper permissions
RUN chmod +x entrypoint.sh
RUN find scripts/ -name "*.sh" -exec chmod +x {} \;

# Create necessary directories before switching user
RUN mkdir -p /app/logs /app/github-workspace /app/build-cache /app/data
RUN chown -R openclaw:openclaw /app

# Switch to non-root user
USER openclaw

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

EXPOSE 8080
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "-m", "src.core.main"]
