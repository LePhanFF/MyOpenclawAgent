# Local vLLM Integration Guide for OpenClaw.ai
# ================================================

# ✅ CURRENT STATUS
# 🚀 Local vLLM: RUNNING (port 8356)
# 🤖 OpenClaw.ai Gateway: RUNNING (port 18789)
# 🔗 Integration: READY

# 📋 CONFIGURATION STEPS

## METHOD 1: DASHBOARD UI (Recommended)
1. Open: http://localhost:18789
2. Navigate to "Models" or "LLM Configuration"
3. Add Custom Provider:
   - Provider Name: "Qwen3 Local"
   - Base URL: "http://host.docker.internal:8356/v1"
   - API Key: "sk-dummy" (dummy key for local)
   - Model ID: "nvidia/Qwen3-Next-80B-A3B-Instruct-NVFP4"
4. Save and Test

## METHOD 2: CONFIG FILE (Advanced)
I've created: /home/lphan/openclaw-gateway-config.json
This config can be applied via dashboard or CLI.

## 🔗 NETWORK CONNECTIONS
# From Gateway Container → Your Local vLLM
# Gateway uses "host.docker.internal" to reach host services
# Your vLLM runs on localhost:8356 (inside Docker network)
# This bridge allows seamless integration

## 🧪 VERIFICATION
After configuration, test:
1. Use Discord: /chat Hello from local Qwen3!
2. Check Dashboard: Should show "Qwen3 Local" model
3. API Test: curl should work through gateway

## 🎯 BENEFITS
# ✅ Use official OpenClaw.ai features and UI
# ✅ Your powerful local Qwen3 NVFP4 model (64K context)
# ✅ No API costs from cloud providers
# ✅ Low latency (local connection)
# ✅ Full control over your model

## 🚨 TROUBLESHOOTING
# If gateway can't reach vLLM:
# 1. Check if vLLM is running: docker ps | grep vllm_qwen
# 2. Verify port: curl -I http://localhost:8356/health
# 3. Check gateway logs: docker logs openclaw-official-openclaw-gateway-1
# 4. Restart gateway: docker restart openclaw-official-openclaw-gateway-1

# Last Updated: 2026-02-07 01:20
# Status: ✅ READY FOR LOCAL VLLM INTEGRATION