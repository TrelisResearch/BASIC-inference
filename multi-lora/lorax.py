import time
import argparse
import os
from openai import OpenAI
import json

def main(adapter_id=None, long_prompt=False):
    RUNPOD_ENDPOINT = os.getenv("RUNPOD_ENDPOINT")
    BASE_MODEL = os.getenv("BASE_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    
    if not RUNPOD_ENDPOINT:
        raise ValueError("Please set RUNPOD_ENDPOINT environment variable")

    client = OpenAI(
        api_key="EMPTY",
        base_url=RUNPOD_ENDPOINT + "/v1",
    )

    if long_prompt:
        prompt = "Write me a long essay on the topic of spring."
        max_tokens = 500
    else:
        prompt = "How many players are on the field on each team at the start of a drop-off?"
        max_tokens = 100

    model_name = BASE_MODEL if not adapter_id else adapter_id
    print("Requested model:", model_name)
    print(f"Using prompt: {prompt}")
    print(f"Max tokens: {max_tokens}")
    
    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.01,
            stream=False
        )
        print("API response model:", response.model)
    except Exception as e:
        print(f"Error during non-streaming request: {str(e)}")
        return

    try:
        stream_response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.01,
            stream=True
        )

        first_token = True
        first_token_time = None
        collected_message = []
        
        for chunk in stream_response:
            if first_token and chunk.choices[0].delta.content:
                first_token_time = time.time()
                first_token = False
            if chunk.choices[0].delta.content:
                collected_message.append(chunk.choices[0].delta.content)
        
        full_message = "".join(collected_message)
        print("Response:", full_message)
        print("Time to first token:", first_token_time - start_time if first_token_time else "N/A")
        total_time = time.time() - start_time
        tokens = len(full_message.split())
        print("Tokens per second:", tokens / total_time)
    
    except Exception as e:
        print(f"Error during streaming request: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            try:
                error_content = json.loads(e.response.text)
                print(f"Error content: {json.dumps(error_content, indent=2)}")
            except json.JSONDecodeError:
                print(f"Raw error content: {e.response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LoRAX inference")
    parser.add_argument("--adapter", type=str, help="HuggingFace adapter slug")
    parser.add_argument("--long-prompt", action="store_true", help="Use long essay prompt")
    args = parser.parse_args()
    main(args.adapter, args.long_prompt)