#!/bin/bash
set -e

echo "🐳 Initializing OpenClaw with DinD support..."

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    echo "⏳ Waiting for ${service_name}..."
    
    timeout 60 bash -c "until curl -f http://${host}:${port}/health > /dev/null 2>&1; do sleep 2; done" || {
        echo "❌ ${service_name} not accessible within timeout"
        return 1
    }
    echo "✅ ${service_name} is ready"
}

# Wait for Docker daemon if DinD is configured
if [ -n "$DOCKER_HOST" ]; then
    echo "⏳ Waiting for Docker daemon..."
    timeout 60 bash -c 'until docker info; do sleep 2; done' || {
        echo "❌ Docker daemon not ready within timeout"
        exit 1
    }
    echo "✅ Docker daemon is ready"
fi

# Wait for vLLM if configured
if [ -n "$OPENAI_BASE_URL" ] && [[ "$OPENAI_BASE_URL" == *"host.docker.internal"* ]]; then
    # Extract host and port from OPENAI_BASE_URL
    VLLM_HOST="host.docker.internal"
    VLLM_PORT="8001"
    
    # Test vLLM connectivity
    echo "⏳ Testing vLLM connectivity..."
    if timeout 30 curl -f -s "${OPENAI_BASE_URL}/models" > /dev/null; then
        echo "✅ vLLM is accessible"
    else
        echo "⚠️ vLLM not immediately accessible, continuing anyway..."
    fi
fi

# Create necessary directories
mkdir -p /app/logs /app/github-workspace /app/build-cache /app/data

# Set proper permissions
chmod 755 /app/logs /app/github-workspace /app/build-cache /app/data

# Validate configuration
if [ ! -f "/app/config/config.yaml" ]; then
    echo "❌ Configuration file not found at /app/config/config.yaml"
    exit 1
fi

echo "✅ Configuration file found"

# Start health check server in background
echo "🚀 Starting health check server..."
python -c "
import uvicorn
import sys
import os
sys.path.append('/app')
os.environ['PYTHONPATH'] = '/app'

from src.core.health import create_app
app = create_app()
uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info')
" &

HEALTH_PID=$!

# Give health server time to start
sleep 3

# Verify health server is running
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Health check server started (PID: $HEALTH_PID)"
else
    echo "❌ Health check server failed to start"
    exit 1
fi

echo "🚀 Starting OpenClaw application..."

# Start the main application
exec "$@"