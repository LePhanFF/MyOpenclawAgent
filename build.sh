# Build once
docker build -t openclaw-agent:latest .

# Run (most common pattern)
docker run --rm -it \
  --name openclaw \
  -v "$(pwd)/data:/data" \
  -v "$(pwd)/logs:/logs" \
  -e OPENAI_BASE_URL=http://host.docker.internal:8001/v1 \
  -e OPENAI_API_KEY=sk-dummy \
  openclaw-agent:latest
