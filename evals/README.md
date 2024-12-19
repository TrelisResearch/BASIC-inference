# Touch Rugby Chat Bot

A command line chat bot that answers questions about touch rugby using OpenAI's GPT-4o-mini model, with Braintrust logging.

## Objectives

### Generic
1. Instrument the generation pipeline to log traces to the evals software.
2. Generate a dataset of questions and answers (or, questions and criteria for correct answers).
3. Set up a scorer that evaluates answers based on the criteria.
4. Run an evaluation of the chatbot on the dataset (either on the UI or from command line).

### Humanloop
- [] Log traces to Humanloop. Stuck here getting examples to show up on the dashboard using the agent example.
- [] Set up a scorer. I wanted to get an LLM to compare my answer to criteria, but this isn't obvious how to set up an evaluator to do this. I'm not clear on how I set the variables to do the comparison I want.
- [] Generate a dataset. This was fairly easy but I don't know what the fields correspond to.
- [] Run an eval from the UI. I can do this but because my scoring isn't set up properly it's hard to know what it means. Oddly, when I run an evaluation I don't see how to view the results.
- [] Run an evaluation from command line. Probably I would be able to do this, if I could get the above working.
- [] Create a dataset from existing logs. 

Humanloop Feedback:
0. It's cool that the sign-up flow includes a first example. Probably it should further illustrate how to get set up wiht logging. BTW the metrics shown are not useful / illustrative. The data shown is complex when I just want to see a score from 0 to 1.
1. I'm not clear on how to get logs to start showing on the dashboard (incl. after running the agent.py example).
2. The logging is complex to set up. Is it possible to provide an openai and gemini light wrapper that does this?
3. I do like that I can use messages granularly in evaluations. This is useful and a painpoint in Braintrust.
4. I'm expecting there to be some llm as a judge type template available in evaluators.
5. I'm not clear on the variables I have access to for running an eval? I have access to the messages, but how do I reference a dataset?
6. It's not obvious where datasets are on the dashboard, I later realised they are listed under Files on the left.
7. The terminology of "prompts" is confusing to me. I would have expected the term to be "logs" or "traces". What does prompt mean? Does it mean question? Does it mean question plus system message?

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

- `pipelines/` - Pipeline implementations for Braintrust and Humanloop.
- `touch_rugby_bot.py` - Command line interface
- `config.py` - Configuration settings for model and evaluations
- `bt_eval_touch_rugby.py` - Evaluation script using Braintrust datasets and scorers

## Installation

1. Clone this repository
2. Install dependencies:
```bash
uv venv
uv pip install -r requirements.txt
```

3. Set up your API keys:
```bash
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "BRAINTRUST_API_KEY=your_braintrust_key_here" >> .env
echo "HUMANLOOP_API_KEY=your_humanloop_key_here" >> .env
echo "GEMINI_API_KEY=your_gemini_key_here" >> .env
```

## Usage

### Chat Interface

Run the chat bot from the command line:
```bash
uv run touch_rugby_bot.py
```

### Running Evaluations with Braintrust

Run the evaluations using:
```bash
uv run bt_eval_touch_rugby.py
```

The evaluation uses:
- Dataset: "touch-rugby-evals" (configured in Braintrust)
- Scorer: "touch-criteria" (configured in Braintrust)
- Project: "touch-rugby-bot"

These settings can be modified in `config.py`.

## Configuration

The project uses two main configuration objects in `config.py`:

```python
BT_EVAL_CONFIG = {
    "dataset": "touch-rugby-evals",
    "scorer": "touch-criteria",
    "project": "touch-rugby-bot"
}

MODEL_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7
}
```
