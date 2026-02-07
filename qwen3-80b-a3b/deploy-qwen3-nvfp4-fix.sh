#!/bin/bash

# Fix FlashInfer Bug - Deploy NVFP4 with Workaround
# Disable flashinfer KV cache planning to avoid the non_blocking=None bug

set -e

echo "🚀 Deploy Qwen3 NVFP4 with FlashInfer Fix"
echo "=========================================="

# 1. Cleanup existing containers
echo "🧹 Cleaning up existing containers..."
docker stop vllm_qwen 2>/dev/null || true
docker rm vllm_qwen 2>/dev/null || true

# 2. Pull the scitrera image but with flashinfer workaround
echo "📦 Pulling DGX Spark vLLM image..."
docker pull scitrera/dgx-spark-vllm:0.13.0-t4

# 3. Deploy with flashinfer workaround
echo "🔥 Deploying with flashinfer KV cache disabled..."
echo "📊 Configuration:"
echo "   - Model: nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4"
echo "   - FlashInfer: Disabled KV cache planning"
echo "   - Attention: Use Torch SDPA fallback"
echo "   - Port: 8356"

docker run -d \
  --name vllm_qwen \
  --gpus '"device=0"' \
  --shm-size=16g \
  -p 8356:8356 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e VLLM_ATTENTION_BACKEND=TORCH_SDPA \
  -e FLASHINFER_DISABLE=1 \
  scitrera/dgx-spark-vllm:0.13.0-t4 \
  vllm serve \
        "nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4" \
        --port 8356 \
        --max-model-len 32768 \
        --gpu-memory-utilization 0.80 \
        --kv-cache-dtype fp8 \
        --trust-remote-code \
        --enforce-eager \
        --disable-frontend-multiprocessing

# 4. Wait for server initialization
echo "⏳ Waiting for vLLM server to initialize..."
sleep 90

# 5. Test the endpoint
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
          {\"role\": \"user\", \"content\": \"Say 'NVFP4 FlashInfer fix successful!'\"
        }],
        \"max_tokens\": 15
      }" | jq -r '.choices[0].message.content')
    
    if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
        echo "✅ Chat completion working: $RESPONSE"
        echo "🎉 NVFP4 model successfully deployed with FlashInfer fix!"
    else
        echo "❌ Chat completion failed"
        docker logs vllm_qwen --tail 20
    fi
    
    echo "🌐 API Endpoint: http://localhost:8356/v1"
    echo "📖 Docs: http://localhost:8356/docs"
else
    echo "❌ Server not ready, checking logs..."
    docker logs vllm_qwen --tail 30
fi

echo "✅ Fix applied: FlashInfer KV cache planning disabled"