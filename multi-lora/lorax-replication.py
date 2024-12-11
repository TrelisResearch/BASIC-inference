import time
import argparse
import os
from openai import OpenAI

def generate_response(client, model_id, prompt):
    messages = [{"role": "user", "content": prompt}]
    
    response = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=100,
        temperature=0.01,
        stream=True
    )

    collected_message = []
    for chunk in response:
        if chunk.choices[0].delta.content:
            collected_message.append(chunk.choices[0].delta.content)
    
    return "".join(collected_message)

def main(adapter_id=None):
    RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT")
    BASE_MODEL = os.getenv("BASE_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    
    if not RUNPOD_ENDPOINT:
        raise ValueError("Please set RUNPOD_ENDPOINT environment variable")

    client = OpenAI(
        api_key="EMPTY",
        base_url=RUNPOD_ENDPOINT + "/v1",
    )

    prompt = "How many players are on the field on each team at the start of a drop-off?"

    # Generate with base model
    print("Base Model Response:")
    base_response = generate_response(client, BASE_MODEL, prompt)
    print(base_response)

    # Generate with adapter if specified
    if adapter_id:
        print("\nAdapter Model Response:")
        adapter_response = generate_response(client, adapter_id, prompt)
        print(adapter_response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LoRAX inference")
    parser.add_argument("--adapter", type=str, help="HuggingFace adapter slug")
    args = parser.parse_args()
    main(args.adapter)