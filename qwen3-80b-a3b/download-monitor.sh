#!/bin/bash

# Monitor model download and initialization progress
echo "⏳ Monitoring Qwen3-Next-80B-A3B-Instruct-NVFP4 Download & Initialization"
echo "=================================================================="

while true; do
    clear
    echo "⏳ vLLM Model Loading Monitor"
    echo "=============================="
    echo "📅 Current Time: $(date)"
    echo ""
    
    echo "📦 Container Status:"
    docker ps | grep vllm_qwen || echo "❌ Container not found"
    
    echo ""
    echo "💾 Resource Usage:"
    docker stats vllm_qwen --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "Container not accessible"
    
    echo ""
    echo "📋 Recent Logs (last 3 lines):"
    docker logs vllm_qwen --tail 3 2>/dev/null | grep -E "(Downloading|Loading|ready|serving|initialized|error|progress|model)" || echo "No recent logs..."
    
    echo ""
    echo "🌐 API Status:"
    if curl -s --max-time 3 http://localhost:8356/health > /dev/null 2>&1; then
        echo "✅ SERVER IS READY! 🎉"
        echo ""
        echo "🚀 You can now use the model:"
        echo "   API Endpoint: http://localhost:8356/v1"
        echo "   Documentation: http://localhost:8356/docs"
        echo ""
        echo "💡 Example curl command:"
        echo "   curl http://localhost:8356/v1/chat/completions \\"
        echo "     -H 'Content-Type: application/json' \\"
        echo "     -d '{\"model\":\"nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}],\"max_tokens\":100}'"
        exit 0
    else
        echo "⏳ Still loading/downloading..."
        echo "   This is normal for 80B parameter models"
        echo "   NVFP4 quantized size: ~20-25GB"
        echo "   Expected time: 10-30 minutes on first download"
    fi
    
    echo ""
    echo "⏰ Elapsed Time: $(docker ps --format "{{.Names}}: {{.Status}}" | grep vllm_qwen | cut -d' ' -f3- || echo "Unknown")"
    echo ""
    echo "Press Ctrl+C to exit monitoring"
    
    sleep 30
done