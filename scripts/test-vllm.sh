#!/bin/bash
# Test script for OpenClaw vLLM integration

echo "🧪 Testing vLLM integration..."

# Test basic vLLM connectivity
echo "1. Testing vLLM models endpoint..."
if curl -s http://localhost:8001/v1/models | jq -e '.data[0].id' > /dev/null 2>&1; then
    echo "✅ vLLM models endpoint accessible"
    MODEL=$(curl -s http://localhost:8001/v1/models | jq -r '.data[0].id')
    echo "📊 Available model: $MODEL"
else
    echo "❌ vLLM models endpoint not accessible"
    exit 1
fi

# Test chat completion
echo "2. Testing vLLM chat completion..."
RESPONSE=$(curl -s -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"You are a helpful assistant. Respond briefly.\"},
      {\"role\": \"user\", \"content\": \"Say 'Hello OpenClaw!'\"}
    ],
    \"max_tokens\": 20
  }" | jq -r '.choices[0].message.content')

if [ -n "$RESPONSE" ] && [ "$RESPONSE" != "null" ]; then
    echo "✅ vLLM chat completion working"
    echo "🤖 Response: $RESPONSE"
else
    echo "❌ vLLM chat completion failed"
    exit 1
fi

# Test health check
echo "3. Testing health check endpoint..."
if curl -s http://localhost:8080/health | jq -e '.status' > /dev/null 2>&1; then
    echo "✅ Health check endpoint working"
    STATUS=$(curl -s http://localhost:8080/health | jq -r '.status')
    echo "🏥 Health status: $STATUS"
else
    echo "❌ Health check endpoint not accessible"
    exit 1
fi

echo "🎉 All vLLM integration tests passed!"