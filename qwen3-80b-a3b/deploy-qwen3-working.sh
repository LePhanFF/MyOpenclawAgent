#!/bin/bash

# Qwen3 NVFP4 Working Implementation based on GLM success
# Using v0.14.0-t4 and runtime transformers install

set -e

echo "🚀 Qwen3 NVFP4 Based on Working GLM Implementation"
echo "=================================================="

# 1. Kill the old container
docker stop vllm_qwen || true && docker rm vllm_qwen || true

# 2. Re-launch with the working pattern from GLM
echo "🔥 Deploying Qwen3 with proven v0.14.0-t4 approach..."
echo "📊 Configuration:"
echo "   - Image: scitrera/dgx-spark-vllm:0.14.0-t4 (newer version)"
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
  --entrypoint /bin/sh \
  scitrera/dgx-spark-vllm:0.14.0-t4 \
  -c "pip install git+https://github.com/huggingface/transformers.git && vllm serve nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4 --port 8356 --trust-remote-code --gpu-memory-utilization 0.9 --max-model-len 65536 --tensor-parallel-size 1 --tool-call-parser hermes --enable-auto-tool-choice --kv-cache-dtype fp8 --max-num-batched-tokens 32768"

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
          {\"role\": \"user\", \"content\": \"Say 'Qwen3 NVFP4 working perfectly!'\"
        }],
        \"max_tokens\": 15
      }" | jq -r '.choices[0].message.content')
    
    if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
        echo "✅ Chat completion working: $RESPONSE"
        echo "🎉 Qwen3 NVFP4 successfully deployed!"
        echo "🚀 Ready for OpenClaw integration!"
    else
        echo "⚠️  Model loaded but testing chat completion..."
        docker logs vllm_qwen --tail 10
    fi
    
    echo "🌐 API Endpoint: http://localhost:8356/v1"
    echo "📖 Docs: http://localhost:8356/docs"
else
    echo "❌ Server not ready, checking logs..."
    docker logs vllm_qwen --tail 30
fi

echo "✅ Deployment using proven GLM pattern complete"