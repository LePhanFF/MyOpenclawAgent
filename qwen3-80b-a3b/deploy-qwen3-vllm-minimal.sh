#!/bin/bash

# DGX Spark vLLM Deployment - Minimal FlashInfer Usage
# Attempt to run Qwen3 with minimal flashinfer features

set -e

echo "🚀 DGX Spark vLLM Deployment - Minimal FlashInfer Mode"
echo "========================================================"

# 1. Cleanup existing containers
echo "🧹 Cleaning up existing containers..."
docker stop vllm_qwen 2>/dev/null || true
docker rm vllm_qwen 2>/dev/null || true

# 2. Pull optimized DGX Spark image
echo "📦 Pulling DGX Spark optimized vLLM image..."
docker pull scitrera/dgx-spark-vllm:0.13.0-t4

# 3. Launch with minimal flashinfer usage
echo "🔥 Launching vLLM server with minimal flashinfer..."
echo "📊 Configuration:"
echo "   - Model: nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4"
echo "   - GPU Memory Utilization: 70%"
echo "   - Max Context Length: 32K tokens"
echo "   - KV Cache: auto (avoid FP8)"
echo "   - Port: 8356"
echo "   - Attention Backend: Triton (avoid FlashInfer)"

docker run -d \
  --name vllm_qwen \
  --gpus '"device=0"' \
  --shm-size=16g \
  -p 8356:8356 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  scitrera/dgx-spark-vllm:0.13.0-t4 \
  vllm serve \
        "nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4" \
        --port 8356 \
        --max-model-len 32768 \
        --gpu-memory-utilization 0.70 \
        --attention-backend triton \
        --enforce-eager \
        --disable-frontend-multiprocessing \
        --trust-remote-code

# 4. Wait for server to be ready
echo "⏳ Waiting for vLLM server to initialize..."
sleep 90

# 5. Check container status
echo "📋 Checking container status..."
docker ps | grep vllm_qwen

# 6. Test the endpoint
echo "🧪 Testing vLLM endpoint..."
if curl -s http://localhost:8356/v1/models > /dev/null; then
    echo "✅ vLLM server is healthy and ready!"
    MODEL=$(curl -s http://localhost:8356/v1/models | jq -r '.data[0].id')
    echo "🤖 Loaded model: $MODEL"
    echo "🌐 API Endpoint: http://localhost:8356/v1"
    
    # Test chat completion
    echo "💬 Testing chat completion..."
    RESPONSE=$(curl -s -X POST http://localhost:8356/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
          {\"role\": \"user\", \"content\": \"Say 'OpenClaw integration successful!'\"}
        ],
        \"max_tokens\": 15
      }" | jq -r '.choices[0].message.content')
    
    if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
        echo "✅ Chat completion working: $RESPONSE"
        echo "🎉 NVFP4 model successfully deployed!"
    else
        echo "❌ Chat completion failed"
        docker logs vllm_qwen --tail 20
    fi
else
    echo "❌ Server not ready, checking logs..."
    docker logs vllm_qwen --tail 50
fi

echo "🔗 Integration ready for OpenClaw"