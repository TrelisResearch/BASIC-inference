# uv venv
# uv pip install 'smolagents[litellm]' transformers
# uv run test-agent.py

from smolagents import CodeAgent

# Use a model provider
# Run: export ANTHROPIC_API_KEY=your-api-key
from smolagents import LiteLLMModel
model = LiteLLMModel("anthropic/claude-3-5-sonnet-latest")

# Use the huggingface api, for free (rated limited)
# from smolagents import HfApiModel
# model = HfApiModel()

# It's safest to modify the system prompt than to replace it, especially since it includes imports.
from smolagents.prompts import CODE_SYSTEM_PROMPT
modified_system_prompt = CODE_SYSTEM_PROMPT + "\\nBe funny." 

agent = CodeAgent(
    tools=[],
    model=model,
    add_base_tools=True, # set to true to include duckduckgo search
    verbosity_level=2,
    system_prompt=modified_system_prompt
)
agent.run("What is the result of 2 power 3.7384?")
# agent.run("What is the difference in attention mechanism in Llama 1 and Llama 2?")