#!/bin/bash

# Monitor vLLM deployment status
echo "🔍 vLLM Deployment Monitor"
echo "========================"

echo "📊 Container Status:"
docker ps | grep vllm_qwen

echo -e "\n💾 Resource Usage:"
docker stats vllm_qwen --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.GPUMemUsage}}"

echo -e "\n📋 Recent Logs (last 5 lines):"
docker logs vllm_qwen --tail 5 | grep -v "Initializing a V1 LLM engine"

echo -e "\n🌐 API Test:"
if curl -s --max-time 5 http://localhost:8356/health > /dev/null 2>&1; then
    echo "✅ Server is responding"
else
    echo "❌ Server not ready yet"
fi

echo -e "\n📅 Elapsed Time:"
docker ps --format "{{.Names}}: {{.Status}}" | grep vllm_qwen