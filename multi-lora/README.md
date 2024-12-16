# Multi-LoRA inference with LoRAX

This directory contains scripts for making inference calls to a LoRAX server running on RunPod.

## ADVANCED / Custom Multi-LoRA vLLM Server

You can purchase lifetime access to the ADVANCED version of this repo at: https://trelis.com/ADVANCED-inference

<details>
<summary>Advanced Features Overview</summary>

- vLLM based server (faster than LoRAX, which is TGI-based).
- Automated LoRA loading/unloading from VRAM as well as downloading/removing from disk.
- Ability to set up external API endpoint.
- Customizable proxy server wrapping vLLM, allowing hyper parameters to be varied.

</details>

## Setup

Start up a vLLM server using vllm docs or a [one-click Runpod server](https://runpod.io/console/deploy?template=p4l5qvim7s&ref=jmfkcdio).

1. Create a virtual environment and install dependencies:
```
cd multi-lora
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

2. Export the required environment variables:
```
export RUNPOD_ENDPOINT="https://<YOUR-POD-ID>-8000.proxy.runpod.net"
export BASE_MODEL="unsloth/Meta-Llama-3.1-8B-Instruct"
```

## Usage

The script supports several modes:

1. Base model inference:
```
uv run lorax.py
```

2. LoRA adapter inference (specify HuggingFace adapter slug):
```
uv run lorax.py --adapter Trelis/Meta-Llama-3.1-8B-Instruct-touch-rugby-2-adapters
```

3. Long prompt testing:
```
uv run lorax.py --long-prompt
```
This mode uses a longer prompt ("Write me a long essay on the topic of spring") with a 500 token limit to better measure performance metrics.

The script outputs:
- Response content
- Time to first token
- Total response time per token

These metrics are particularly useful when using `--long-prompt` to evaluate model performance with longer generations.

## Environment

The script is configured to use:
- API Endpoint: https://<YOUR-POD-ID>-8000.proxy.runpod.net
- Default Base Model: unsloth/Meta-Llama-3.1-8B-Instruct

## Replication Testing

The `lorax-replication.py` script is provided to help debug and validate LoRAX server responses against local PEFT inference.

### Usage

Run the replication script similarly to the main script:

```
# Base model only
uv run lorax-replication.py

# With adapter
uv run lorax-replication.py --adapter Trelis/Meta-Llama-3.1-8B-Instruct-touch-rugby-3-adapters
```

### Purpose

This script helps identify discrepancies between:
1. LoRAX server inference
2. Local PEFT model inference

### Known Issues

Current testing reveals several concerns:

1. **Adapter Loading**: The LoRAX server may not be correctly loading adapters, producing responses that don't reflect the adapter's training. For example:
   - Server responses discuss Australian rules football when queried about touch rugby
   - Local PEFT inference correctly identifies touch rugby concepts

2. **Response Length**: Responses may be truncated due to token limits. Consider adjusting `max_tokens` if complete responses are needed.