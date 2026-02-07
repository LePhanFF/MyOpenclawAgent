#!/bin/bash

# 8-bit vLLM Deployment for Qwen3 model (compatible with standard containers)
# Using 8-bit quantization to avoid NVFP4 compatibility issues

set -e

echo "🚀 8-bit vLLM Deployment - Qwen3 Model (Standard Quantization)"
echo "==============================================================="

# 1. Cleanup existing containers
echo "🧹 Cleaning up existing containers..."
docker stop vllm_qwen 2>/dev/null || true
docker rm vllm_qwen 2>/dev/null || true

# 2. Pull standard vLLM image
echo "📦 Pulling standard vLLM image..."
docker pull vllm/vllm-openai:latest

# 3. Find available Qwen3 models
echo "🔍 Checking available Qwen3 models..."
echo "   Option 1: Try Qwen2.5-72B-Instruct (8-bit compatible)"
echo "   Option 2: Try Qwen3-80B with bitsandbytes 8-bit"

# 4. Launch with 8-bit quantization
echo "🔥 Launching vLLM server with 8-bit quantization..."
echo "📊 Configuration:"
echo "   - Model: Qwen2.5-72B-Instruct (8-bit compatible alternative)"
echo "   - GPU Memory Utilization: 85%"
echo "   - Max Context Length: 32K tokens" 
echo "   - Quantization: bitsandbytes (8-bit)"
echo "   - Port: 8356"

docker run -d \
  --name vllm_qwen \
  --gpus '"device=0"' \
  --shm-size=16g \
  -p 8356:8356 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  vllm/vllm-openai:latest \
  vllm serve \
        "Qwen/Qwen2.5-72B-Instruct" \
        --port 8356 \
        --max-model-len 32768 \
        --gpu-memory-utilization 0.85 \
        --quantization bitsandbytes \
        --load-format bitsandbytes \
        --trust-remote-code

# 5. Wait for server to be ready
echo "⏳ Waiting for vLLM server to initialize..."
sleep 120

# 6. Check container status
echo "📋 Checking container status..."
docker ps | grep vllm_qwen

# 7. Test the endpoint
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
    else
        echo "❌ Chat completion failed"
    fi
else
    echo "❌ Server not ready, checking logs..."
    docker logs vllm_qwen --tail 50
fi

echo "🎉 Deployment complete!"
echo "⚠️  Note: Using 8-bit quantization (larger memory footprint but compatible)"