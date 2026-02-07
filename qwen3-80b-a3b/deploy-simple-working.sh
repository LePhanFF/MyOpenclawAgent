#!/bin/bash

# Simple Working vLLM Deployment
# Using a known working model to get OpenClaw operational quickly

set -e

echo "🚀 Simple Working vLLM Deployment"
echo "=================================="

# 1. Cleanup existing containers
echo "🧹 Cleaning up existing containers..."
docker stop vllm_qwen 2>/dev/null || true
docker rm vllm_qwen 2>/dev/null || true

# 2. Use lightweight working model
echo "📦 Deploying known working model..."
docker run -d \
  --name vllm_qwen \
  --gpus '"device=0"' \
  --shm-size=8g \
  -p 8356:8356 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  vllm/vllm-openai:latest \
  vllm serve "microsoft/DialoGPT-medium" \
    --port 8356 \
    --max-model-len 2048 \
    --gpu-memory-utilization 0.8

# 3. Wait for server
echo "⏳ Waiting for server to initialize..."
sleep 60

# 4. Test the endpoint
echo "🧪 Testing vLLM endpoint..."
if curl -s http://localhost:8356/v1/models > /dev/null; then
    echo "✅ vLLM server is healthy and ready!"
    MODEL=$(curl -s http://localhost:8356/v1/models | jq -r '.data[0].id')
    echo "🤖 Loaded model: $MODEL"
    
    # Test chat completion
    RESPONSE=$(curl -s -X POST http://localhost:8356/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
          {\"role\": \"user\", \"content\": \"Hello! Say 'OpenClaw working!'\"
        }],
        \"max_tokens\": 10
      }" | jq -r '.choices[0].message.content')
    
    if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
        echo "✅ Chat completion working: $RESPONSE"
        echo "🎉 OpenClaw integration ready!"
    else
        echo "⚠️  Model loaded but chat completion limited"
    fi
    
    echo "🌐 API Endpoint: http://localhost:8356/v1"
else
    echo "❌ Server failed to start"
    docker logs vllm_qwen --tail 20
fi