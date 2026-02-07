# Qwen3-Next-80B-A3B-Instruct-NVFP4 Deployment

This repository contains a deployment script for the RESMP-DEV/Qwen3-Next-80B-A3B-Instruct-NVFP4 model using vLLM for efficient inference on NVIDIA GPUs.

## Model Overview

RESMP-DEV/Qwen3-Next-80B-A3B-Instruct-NVFP4 is a quantized version of Qwen3-Next-80B-A3B-Instruct, optimized for general AI tasks including coding, reasoning, and tool calling.

- **Type**: Causal Language Models
- **Parameters**: 80B total (MoE architecture)
- **Layers**: Variable (MoE)
- **Attention Heads (GQA)**: Optimized for efficiency
- **Experts**: Multiple experts activated per token
- **Context Length**: 131,072 tokens (as configured)
- **Quantization**: NVFP4 (NVIDIA 4-bit floating point)
- **License**: Apache-2.0

This model excels in long-context understanding, reasoning, and tool calling, supporting advanced AI applications.

**Note**: This model is optimized for the Blackwell GB10 architecture with NVFP4 quantization.

For more details, see the [official Qwen3 blog](https://qwenlm.github.io/blog/qwen3/), [GitHub](https://github.com/QwenLM/Qwen3), and [Documentation](https://qwen.readthedocs.io/en/latest/).

## Quickstart

Use the provided Bash script `vl-32code.sh` to deploy the model with vLLM in a Docker container.

### Prerequisites
- Docker
- NVIDIA GPU with CUDA support (Blackwell GB10/SM12.1 recommended for optimal NVFP4 performance)
- Hugging Face token (set in the script)

### Blackwell GB10 Support

This deployment uses the bleeding-edge `avarok/vllm-nvfp4-gb10-sm120:v8` Docker image, specifically optimized for NVFP4 quantization on Blackwell GB10 (DGX Spark) GPUs:
- **Performance**: Optimized for NVFP4 MoE models with fast loading and inference
- **Compatibility**: Addresses CUDA 12.1/SM12.1 issues and provides native FP4 acceleration
- **Features**: Includes fastsafetensors for improved model loading times
- **References**:
  - [Blog: NVFP4 W4A4 MoE Inference on NVIDIA Blackwell GB10](https://blog.avarok.net/nvfp4-w4a4-moe-inference-on-nvidia-blackwell-gb10-1a83e85d0f9e)
  - [Forum: New bleeding-edge vLLM Docker Image](https://forums.developer.nvidia.com/t/new-bleeding-edge-vllm-docker-image-avarok-vllm-nvfp4-gb10-sm120/354231)

### Deployment
Run the script:
```bash
./vl-32code.sh
```

This will:
- Clean up any existing container
- Pull the optimized vLLM Docker image
- Launch the server on port 8000 with optimized settings for NVFP4 inference

### API Usage
The server exposes an OpenAI-compatible API at `http://localhost:8000/v1`.

Example Python code for tool calling:
```python
import openai

client = openai.OpenAI(
    base_url='http://localhost:8000/v1',
    api_key="EMPTY"
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "square_the_number",
            "description": "Output the square of the number.",
            "parameters": {
                "type": "object",
                "required": ["input_num"],
                "properties": {
                    "input_num": {
                        "type": "number",
                        "description": "Input number to be squared"
                    }
                }
            }
        }
    }
]

messages = [{'role': 'user', 'content': 'Square the number 1024'}]

completion = client.chat.completions.create(
    messages=messages,
    model="RESMP-DEV/Qwen3-Next-80B-A3B-Instruct-NVFP4",
    max_tokens=65536,
    tools=tools
)

print(completion.choices[0])
```

## Best Practices

- **Sampling Parameters**: Use `temperature=0.7`, `top_p=0.8`, `top_k=20`, `repetition_penalty=1.05`
- **Output Length**: 65,536 tokens recommended for most queries
- **Context Management**: Reduce context if encountering OOM issues

## Changes Made

This deployment has been updated to use the bleeding-edge vLLM Docker image and a larger NVFP4 quantized MoE model for optimal performance on Blackwell GB10 GPUs:

- **Docker Image**: Switched from `nvcr.io/nvidia/vllm:25.11-py3` to `avarok/vllm-nvfp4-gb10-sm120:v8` for native NVFP4 support
- **Model**: Changed from `GAlex535/Qwen3-Coder-30B-A3B-Instruct-NVFP4` to `RESMP-DEV/Qwen3-Next-80B-A3B-Instruct-NVFP4` for better MoE performance
- **Configuration**:
  - Port changed from 8356 to 8000
  - Max model length set to 131,072 tokens
  - GPU memory utilization increased to 0.90
  - Added shared memory size (--shm-size=16g) for better performance
- **Flags**: Retained tool calling support with `--enable-auto-tool-choice` and `--tool-call-parser qwen3_coder`

These changes leverage the latest optimizations for NVFP4 quantization on Blackwell architecture, providing faster inference and better compatibility.

## Citation

```
@misc{qwen3technicalreport,
      title={Qwen3 Technical Report},
      author={Qwen Team},
      year={2025},
      eprint={2505.09388},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2505.09388},
}
```

Additional references for NVFP4 optimization:
- [NVFP4 W4A4 MoE Inference on NVIDIA Blackwell GB10](https://blog.avarok.net/nvfp4-w4a4-moe-inference-on-nvidia-blackwell-gb10-1a83e85d0f9e)
- [NVIDIA Developer Forum: Bleeding-edge vLLM Docker Image](https://forums.developer.nvidia.com/t/new-bleeding-edge-vllm-docker-image-avarok-vllm-nvfp4-gb10-sm120/354231)