# Touch Rugby Chat Bot

A command line chat bot that answers questions about touch rugby using OpenAI's GPT-4o-mini model, with Braintrust logging.

## Objectives

### Generic
1. Instrument the generation pipeline to log traces to the evals software.
2. Generate a dataset of questions and answers (or, questions and criteria for correct answers).
3. Set up a scorer that evaluates answers based on the criteria.
4. Run an evaluation of the chatbot on the dataset (either on the UI or from command line).

### Braintrust
- [x] Create a simple chatbot command line interface (to which I could add retrieval or other techniques).
- [x] Log traces to Braintrust.
- [x] Define an evaluation dataset consisting of questions and answers. Done in Braintrust.
    - [x] Explore different evaluation types, e.g. criterion based versus factuality based. Works fine, although datasets seem to always require `input` and `expected` values, rather than `criteria`. This seems to be because I changed the expectations for the ClosedQA scorer and that stuck.
    - [ ] Allow the evaluation dataset to be expanded/augmented with production data. Key issue is formatting the data appropriately.
- [x] Evaluate the chatbot on the dataset.
    - [x] Abstract the pipeline such that it may be used in the command line interface OR for evaluations. This is critical to allow evals to easily be run on a production pipeline.
    - [ ] I can't run an evaluation with my customer scorer from the UI...

Feedback for Braintrust:
1. Users are able to overwrite the behaviour of default Scorers. This poses an issue because errors the user makes propagate when deriving new scorers from the default. Suggest keeping the default scorer values as defaults.
2. When running evals, it's not obvious how the project is being set and how the eval name is set. The Eval class expects a name, and that seems to be the project name.
3. I want to copy production logs into a dataset. Right now, that seems to copy across data in llm format. How do I format that properly - use the API?
4. I can't delete scorers on the UI.
5. There is no way to add a custom-named row to a dataset in the UI.

## Project Structure

- `pipeline.py` - Core chat completion logic and Braintrust integration
- `touch_rugby_bot.py` - Command line interface
- `config.py` - Configuration settings for model and evaluations
- `run_evals.py` - Evaluation script using Braintrust datasets and scorers

## Features

- Interactive command line interface
- Specialized knowledge about touch rugby rules, techniques, and strategies
- Powered by OpenAI's GPT-4o-mini model
- Logging and monitoring via Braintrust
- Automated evaluations using Braintrust datasets and scorers
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

## Usage

### Chat Interface

Run the chat bot from the command line:
```bash
uv run touch_rugby_bot.py
```

### Running Evaluations

Run the evaluations using:
```bash
uv run eval_touch_rugby.py
```

The evaluation uses:
- Dataset: "touch-rugby-evals" (configured in Braintrust)
- Scorer: "touch-criteria" (configured in Braintrust)
- Project: "touch-rugby-bot"

These settings can be modified in `config.py`.

## Configuration

The project uses two main configuration objects in `config.py`:

```python
EVAL_CONFIG = {
    "dataset": "touch-rugby-evals",
    "scorer": "touch-criteria",
    "project": "touch-rugby-bot"
}

MODEL_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7
}
```

## Development

The project is structured to separate concerns:
- Core chat completion logic is in `pipeline.py`
- Command line interface is in `touch_rugby_bot.py`
- Evaluation logic is in `run_evals.py`
- Configuration is in `config.py`

This makes it easy to:
- Add new features to the pipeline
- Create new interfaces
- Run evaluations with different datasets/scorers
- Modify model parameters
