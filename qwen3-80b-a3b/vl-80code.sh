## abadon, sucks compared to glm

# 1. Cleanup
docker stop vllm_qwen && docker rm vllm_qwen

docker pull  scitrera/dgx-spark-vllm:0.13.0-t4:latest

# 2. Launch with the Blackwell Environment Shims
#
docker run -d \
  --gpus '"device=0"' \
  --shm-size=16g \
  -p 8356:8356 \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  scitrera/dgx-spark-vllm:0.13.0-t4 \
  vllm serve \
        "RESMP-DEV/Qwen3-Next-80B-A3B-Instruct-NVFP4" \
        --port 8356 \
        --max-model-len 32768 \
	--kv-cache-dtype fp8 \
        --gpu-memory-utilization 0.90 \
        --trust-remote-code \
        --enable-auto-tool-choice \
        --tool-call-parser hermes
