import os
from humanloop import Humanloop
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

humanloop = Humanloop(api_key=os.getenv("HUMANLOOP_API_KEY"))
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define your Prompt in code
model = "gpt-4-turbo-preview"  # Fixed model name
template = [
    {"role": "user", "content": "Extract the first name for '{{full_name}}'."},
    # Uncomment the next line when running the script a second time.
    {"role": "user", "content": "Reply only with the first name"},
]

def call_openai(**inputs) -> str:
    response = openai.chat.completions.create(
        model=model,
        messages=humanloop.prompts.populate_template(template=template, inputs=inputs),
    )
    return response.choices[0].message.content

# Runs the eval and versions the Prompt and Dataset
humanloop.evaluations.run(
    name="Example Evaluation",
    file={
        "path": "First name extraction",
        "callable": call_openai,
        "type": "prompt",
        "version": {"model": model, "template": template},
    },
    dataset={
        "path": "First names",
        "datapoints": [
            {
                "inputs": {"full_name": "Albert Einstein"},
                "target": {"output": "Albert"},
            },
            {
                "inputs": {"full_name": "Albus Wulfric Percival Brian Dumbledore"},
                "target": {"output": "Albus"},
            },
        ],
    },
    evaluators=[
        {"path": "Example Evaluators/Code/Exact match"},
        {"path": "Example Evaluators/Code/Levenshtein distance"},
        {"path": "Example Evaluators/Code/Latency"},
    ],
) 