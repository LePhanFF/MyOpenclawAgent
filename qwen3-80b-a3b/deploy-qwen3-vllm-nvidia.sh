#!/bin/bash

# NVIDIA Official vLLM Deployment for Qwen3-Next-80B-A3B-Instruct-NVFP4
# Using official NVIDIA container to avoid flashinfer issues

set -e

echo "🚀 NVIDIA Official vLLM Deployment - Qwen3-Next-80B-A3B-Instruct-NVFP4"
echo "====================================================================="

# 1. Cleanup existing containers
echo "🧹 Cleaning up existing containers..."
docker stop vllm_qwen 2>/dev/null || true
docker rm vllm_qwen 2>/dev/null || true

# 2. Pull official NVIDIA vLLM image
echo "📦 Pulling official NVIDIA vLLM image..."
docker pull nvcr.io/nvidia/vllm:25.11-py3

# 3. Launch with optimized settings
echo "🔥 Launching vLLM server with official NVIDIA container..."
echo "📊 Configuration:"
echo "   - Model: nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4"
echo "   - GPU Memory Utilization: 80%"
echo "   - Max Context Length: 64K tokens"
echo "   - Port: 8356"

docker run -d \
  --name vllm_qwen \
  --gpus '"device=0"' \
  --shm-size=16g \
  -p 8356:8356 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  nvcr.io/nvidia/vllm:25.11-py3 \
  vllm serve \
        "nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4" \
        --port 8356 \
        --max-model-len 65536 \
        --gpu-memory-utilization 0.80 \
        --kv-cache-dtype fp8 \
        --trust-remote-code \
        --disable-tokenization-parallelism

# 4. Wait for server to be ready
echo "⏳ Waiting for vLLM server to initialize..."
sleep 60

# 5. Check container status
echo "📋 Checking container status..."
docker ps | grep vllm_qwen

# 6. Show logs and health check
echo "🏥 Checking server health..."
sleep 10
if curl -f http://localhost:8356/health 2>/dev/null; then
    echo "✅ vLLM server is healthy and ready!"
    echo "🌐 API Endpoint: http://localhost:8356/v1"
    echo "📖 OpenAI-compatible API documentation: http://localhost:8356/docs"
else
    echo "❌ Server not ready yet, checking logs..."
    docker logs vllm_qwen --tail 50
fi

echo "🎉 Deployment complete! You can now use the model via the OpenAI-compatible API."
echo "💡 Example usage:"
echo "   curl http://localhost:8356/v1/chat/completions -H 'Content-Type: application/json' -d '{\"model\":\"nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}],\"max_tokens\":100}'"