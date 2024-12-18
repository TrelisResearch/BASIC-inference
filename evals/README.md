# Touch Rugby Chat Bot

A command line chat bot that answers questions about touch rugby using OpenAI's GPT-4o-mini model, with Braintrust logging.

## Objectives

- [x] Create a simple chatbot command line interface (to which I could add retrieval or other techniques).
- [x] Log traces to Braintrust.
- [x] Define an evaluation dataset consisting of questions and answers. Done in Braintrust.
    - [ ] Explore different evaluation types, e.g. criterion based versus factuality based.
    - [ ] Allow the evaluation dataset to be expanded/augmented with production data.
- [ ] Evaluate the chatbot on the dataset.
    - [ ] This requires abstracting the pipeline such that it may be used in the command line interface OR for evaluations.

## Features

- Interactive command line interface
- Specialized knowledge about touch rugby rules, techniques, and strategies
- Powered by OpenAI's GPT-4o-mini model
- Logging and monitoring via Braintrust
- Simple, easy-to-use interface

## Installation

1. Clone this repository
2. Install dependencies:
```bash
uv venv
uv pip install openai python-dotenv braintrust autoevals
```

3. Set up your API keys:
```bash
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "BRAINTRUST_API_KEY=your_braintrust_key_here" >> .env
```

4. Run the bot:
```bash
uv run touch_rugby_bot.py
```
