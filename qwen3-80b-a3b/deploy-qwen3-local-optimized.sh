#!/bin/bash

# Qwen3 NVFP4 with Local Optimized Image
# Using pre-built vllm-glm-optimized image with latest transformers

set -e

echo "🚀 Qwen3 NVFP4 with Local Optimized Image"
echo "============================================"

# 1. Cleanup existing containers
docker stop vllm_qwen || true && docker rm vllm_qwen || true

# 2. Use the working local image with latest transformers
echo "🔥 Using pre-built vllm-glm-optimized image..."
echo "📊 Configuration:"
echo "   - Image: vllm-glm-optimized:latest (local, with transformers)"
echo "   - Model: nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4"
echo "   - GPU Memory: 90%"
echo "   - Max Length: 64K"
echo "   - Tool Parser: hermes"

docker run -d \
  --name vllm_qwen \
  --gpus all \
  --ipc=host \
  -p 8356:8356 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -v "$HOME/.cache/vllm:/root/.cache/vllm" \
  vllm-glm-optimized:latest \
  vllm serve nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4 \
    --port 8356 \
    --trust-remote-code \
    --gpu-memory-utilization 0.9 \
    --max-model-len 65536 \
    --tensor-parallel-size 1 \
    --tool-call-parser hermes \
    --enable-auto-tool-choice \
    --kv-cache-dtype fp8 \
    --max-num-batched-tokens 32768

# 3. Wait for server initialization
echo "⏳ Waiting for vLLM server to initialize..."
sleep 120

# 4. Test the endpoint
echo "🧪 Testing vLLM endpoint..."
if curl -s http://localhost:8356/v1/models > /dev/null; then
    echo "✅ vLLM server is healthy and ready!"
    MODEL=$(curl -s http://localhost:8356/v1/models | jq -r '.data[0].id')
    echo "🤖 Loaded model: $MODEL"
    
    # Test chat completion
    echo "💬 Testing chat completion..."
    RESPONSE=$(curl -s -X POST http://localhost:8356/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
          {\"role\": \"user\", \"content\": \"Say 'Qwen3 NVFP4 with optimized image working!'\"
        }],
        \"max_tokens\": 15
      }" | jq -r '.choices[0].message.content')
    
    if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
        echo "✅ Chat completion working: $RESPONSE"
        echo "🎉 Qwen3 NVFP4 successfully deployed with optimized image!"
        echo "🚀 Ready for OpenClaw integration!"
    else
        echo "⚠️  Model loaded but testing chat completion..."
        docker logs vllm_qwen --tail 10
    fi
    
    echo "🌐 API Endpoint: http://localhost:8356/v1"
    echo "📖 Docs: http://localhost:8356/docs"
    
    # Update OpenClaw config with working endpoint
    echo "🔧 Updating OpenClaw navigation file..."
    echo "VLLM_STATUS: WORKING" >> /home/lphan/openclaw/openclaw.navigate.txt
    echo "MODEL_ENDPOINT: http://localhost:8356/v1" >> /home/lphan/openclaw/openclaw.navigate.txt
    echo "LAST_UPDATE: $(date)" >> /home/lphan/openclaw/openclaw.navigate.txt
    
else
    echo "❌ Server not ready, checking logs..."
    docker logs vllm_qwen --tail 30
fi

echo "✅ Deployment with local optimized image complete"