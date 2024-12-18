Title: Write evaluations - Docs - Braintrust

URL Source: http://www.braintrust.dev/docs/guides/evals/write

Markdown Content:
An `Eval()` statement logs results to a Braintrust project. (Note: you can have multiple eval statements for one project and/or multiple eval statements in one file.)

An evaluation dataset is a list of test cases. Each has an input and optional expected output, metadata, and tags. The key fields in a data record are:

*   **Input**: The arguments that uniquely define a test case (an arbitrary, JSON serializable object). Braintrust uses the `input` to know whether two test cases are the same between evaluation runs, so the cases should not contain run-specific state. A simple rule of thumb is that if you run the same eval twice, the `input` should be identical.
*   **Expected**. (Optional) the ground truth value (an arbitrary, JSON serializable object) that you'd compare to `output` to determine if your `output` value is correct or not. Braintrust currently does not compare `output` to `expected` for you, since there are many different ways to do that correctly. For example, you may use a subfield in `expected` to compare to a subfield in `output` for a certain scoring function. Instead, these values are just used to help you navigate your evals while debugging and comparing results.
*   **Metadata**. (Optional) a dictionary with additional data about the test example, model outputs, or just about anything else that's relevant, that you can use to help find and analyze examples later. For example, you could log the `prompt`, example's `id`, model parameters, or anything else that would be useful to slice/dice later.
*   **Tags**. (Optional) a list of strings that you can use to filter and group records later.

### [Getting started](http://www.braintrust.dev/docs/guides/evals/write#getting-started)

To get started with evals, you need some test data. A fine starting point is to write 5-10 examples that you believe are representative. The data must have an input field (which could be complex JSON, or just a string) and should ideally have an expected output field, (although this is not required).

Once you have an evaluation set up end-to-end, you can always add more test cases. You'll know you need more data if your eval scores and outputs seem fine, but your production app doesn't look right. And once you have Braintrust's [Logging](https://www.braintrust.dev/docs/guides/logging) set up, your real application data will provide a rich source of examples to use as test cases.

As you scale, Braintrust's [Datasets](https://www.braintrust.dev/docs/guides/datasets) are a great tool for managing your test cases.

It's a common misconception that you need a large volume of perfectly labeled evaluation data, but that's not the case. In practice, it's better to assume your data is noisy, your AI model is imperfect, and your scoring methods are a little bit wrong. The goal of evaluation is to assess each of these components and improve them over time.

### [Specifying an existing dataset in evals](http://www.braintrust.dev/docs/guides/evals/write#specifying-an-existing-dataset-in-evals)

In addition to providing inline data examples when you call the `Eval()` function, you can also [pass an existing or newly initialized dataset](https://www.braintrust.dev/docs/guides/datasets#using-a-dataset-in-an-evaluation).

A scoring function allows you to compare the expected output of a task to the actual output and produce a score between 0 and 1. You use a scoring function by referencing it in the `scores` array in your eval.

We recommend starting with the scorers provided by Braintrust's [autoevals library](https://www.braintrust.dev/docs/autoevals). They work out of the box and will get you up and running quickly. Just like with test cases, once you begin running evaluations, you will find areas that need improvement. This will lead you create your own scorers, customized to your usecases, to get a well rounded view of your application's performance.

### [Define your own scorers](http://www.braintrust.dev/docs/guides/evals/write#define-your-own-scorers)

You can define your own score, e.g.

### [Score using AI](http://www.braintrust.dev/docs/guides/evals/write#score-using-ai)

You can also define your own prompt-based scoring functions. For example,

### [Conditional scoring](http://www.braintrust.dev/docs/guides/evals/write#conditional-scoring)

Sometimes, the scoring function(s) you want to use depend on the input data. For example, if you're evaluating a chatbot, you might want to use a scoring function that measures whether calculator-style inputs are correctly answered.

#### [Skip scorers](http://www.braintrust.dev/docs/guides/evals/write#skip-scorers)

Return `null`/`None` to skip a scorer for a particular test case.

Scores with `null`/`None` values will be ignored when computing the overall score, improvements/regressions, and summary metrics like standard deviation.

#### [List of scorers](http://www.braintrust.dev/docs/guides/evals/write#list-of-scorers)

You can also return a list of scorers from a scorer function. This allows you to dynamically generate scores based on the input data, or even combine scores together into a single score. When you return a list of scores, you must return a `Score` object, which has a `name` and a `score` field.

### [Scorers with additional fields](http://www.braintrust.dev/docs/guides/evals/write#scorers-with-additional-fields)

Certain scorers, like [ClosedQA](https://github.com/braintrustdata/autoevals/blob/main/templates/closed_q_a.yaml), allow additional fields to be passed in. You can pass them in by initializing them with `.partial(...)`.

This approach works well if the criteria is static, but if the criteria is dynamic, you can pass them in via a wrapper function, e.g.

### [Composing scorers](http://www.braintrust.dev/docs/guides/evals/write#composing-scorers)

Sometimes, it's useful to build scorers that call other scorers. For example, if you're building a translation app, you could reverse translate the output, and use `EmbeddingSimilarity` to compare it to the original input.

To compose scorers, simply call one scorer from another.

### [While executing the `task`](http://www.braintrust.dev/docs/guides/evals/write#while-executing-the-task)

Although you can provide `metadata` about each test case in the `data` function, it can be helpful to add additional metadata while your `task` is executing. The second argument to `task` is a `hooks` object, which allows you to read and update metadata on the test case.

### [Experiment-level metadata](http://www.braintrust.dev/docs/guides/evals/write#experiment-level-metadata)

It can be useful to add custom metadata to your experiments, e.g. to store information about the model or other parameters that you use. To set custom metadata, pass a `metadata` field to your `Eval` block:

Once you set metadata, you can view and filter by it on the Experiments page:

You can also construct complex analyses across experiments. See [Analyze across experiments](https://www.braintrust.dev/docs/guides/evals/interpret#analyze-across-experiments) for more details.

It is often useful to run each input in an evaluation multiple times, to get a sense of the variance in responses and get a more robust overall score. Braintrust supports _trials_ as a first-class concept, allowing you to run each input multiple times. Behind the scenes, Braintrust will intelligently aggregate the results by bucketing test cases with the same `input` value and computing summary statistics for each bucket.

To enable trials, add a `trialCount`/`trial_count` property to your evaluation:

Sometimes you do not have expected outputs, and instead want to use a previous experiment as a baseline. Hill climbing is inspired by, but not exactly the same as, the term used in [numerical optimization](https://en.wikipedia.org/wiki/Hill_climbing). In the context of Braintrust, hill climbing is a way to iteratively improve a model's performance by comparing new experiments to previous ones. This is especially useful when you don't have a pre-existing benchmark to evaluate against.

Braintrust supports hill climbing as a first-class concept, allowing you to use a previous experiment's `output` field as the `expected` field for the current experiment. Autoevals also includes a number of scoreres, like `Summary` and `Battle`, that are designed to work well with hill climbing.

To enable hill climbing, use `BaseExperiment()` in the `data` field of an eval:

That's it! Braintrust will automatically pick the best base experiment, either using git metadata if available or timestamps otherwise, and then populate the `expected` field by merging the `expected` and `output` field of the base experiment. This means that if you set `expected`, e.g. through the UI while reviewing results, it will be used as the `expected` field for the next experiment.

**Using a specific experiment**

If you want to use a specific experiment as the base experiment, you can pass the `name` field to `BaseExperiment()`:

**Scoring considerations**

Often while hill climbing, you want to use two different types of scoring functions:

*   Methods that do not require an expected output, e.g. `ClosedQA`, so that you can judge the quality of the output purely based on the input and output. This measure is useful to track across experiments, and it can be used to compare any two experiments, even if they are not sequentially related.
*   Comparative methods, e.g. `Battle` or `Summary`, that accept an `expected` output but do not treat it as a ground truth. Generally speaking, if you score \> 50% on a comparative method, it means you're doing better than the base on average. To learn more about how `Battle` and `Summary` work, check out [their prompts](https://github.com/braintrustdata/autoevals/tree/main/templates).

When you run an experiment, Braintrust logs the results to your terminal, and `braintrust eval` returns a non-zero exit code if any eval throws an exception. However, it's often useful to customize this behavior, e.g. in your CI/CD pipeline to precisely define what constitutes a failure, or to report results to a different system.

Braintrust allows you to define custom reporters that can be used to process and log results anywhere you'd like. You can define a reporter by adding a `Reporter(...)` block. A Reporter has two functions:

Any `Reporter` included among your evaluated files will be automatically picked up by the `braintrust eval` command.

*   If no reporters are defined, the default reporter will be used which logs the results to the console.
*   If you define one reporter, it'll be used for all `Eval` blocks.
*   If you define multiple `Reporter`s, you have to specify the reporter name as an optional 3rd argument to `Eval()`.

**Example: the default reporter**

As an example, here's the default reporter that Braintrust uses:

Braintrust allows you to log arbitrary binary data, like images, audio, and PDFs, as [attachments](https://www.braintrust.dev/docs/guides/traces/customize#uploading-attachments). The easiest way to use attachments in your evals is to initialize an `Attachment` object in your data.

You can also store attachments in a dataset for reuse across multiple experiments.

Braintrust allows you to trace detailed debug information and metrics about your application that you can use to measure performance and debug issues. The trace is a tree of spans, where each span represents an expensive task, e.g. an LLM call, vector database lookup, or API request.

If you are using the OpenAI API, Braintrust includes a wrapper function that automatically logs your requests. To use it, simply call `wrapOpenAI/wrap_openai` on your OpenAI instance. See [Wrapping OpenAI](https://www.braintrustdata.com/docs/guides/tracing#wrapping-openai) for more info.

Each call to `experiment.log()` creates its own trace, starting at the time of the previous log statement and ending at the completion of the current. Do not mix `experiment.log()` with tracing. It will result in extra traces that are not correctly parented.

For more detailed tracing, you can wrap existing code with the `braintrust.traced` function. Inside the wrapped function, you can log incrementally to `braintrust.currentSpan()`. For example, you can progressively log the input, output, and expected output of a task, and then log a score at the end:

This results in a span tree you can visualize in the UI by clicking on each test case in the experiment:

![Image 5: Root Span](https://www.braintrust.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Froot_span_trace.7f73783e.png&w=3840&q=75) ![Image 6: Subspan](https://www.braintrust.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fsubspan_trace.82278197.png&w=3840&q=75)

The SDK allows you to report evaluation results directly from your code, without using the `Eval()` or `.traced()` functions. This is useful if you want to structure your own complex evaluation logic, or integrate Braintrust with an existing testing or evaluation framework.

Refer to the [tracing](https://www.braintrust.dev/docs/guides/tracing) guide for examples of how to trace evaluations using the low-level SDK. For more details on how to use the low level SDK, see the [Python](https://www.braintrust.dev/docs/libs/python) or [Node.js](https://www.braintrust.dev/docs/libs/nodejs) documentation.

### [Exception when mixing `log` with `traced`](http://www.braintrust.dev/docs/guides/evals/write#exception-when-mixing-log-with-traced)

There are two ways to log to Braintrust: `Experiment.log` and `Experiment.traced`. `Experiment.log` is for non-traced logging, while `Experiment.traced` is for tracing. This exception is thrown when you mix both methods on the same object, for instance:

Most of the time, you should use either `Experiment.log` or `Experiment.traced`, but not both, so the SDK throws an error to prevent accidentally mixing them together. For the above example, you most likely want to write:

In rare cases, if you are certain you want to mix traced and non-traced logging on the same object, you may pass the argument `allowConcurrentWithSpans: true`/`allow_concurrent_with_spans=True` to `Experiment.log`.

Although you can log scores from your application, it can be awkward and computationally intensive to run evals code in your production environment. To solve this, Braintrust supports server-side online evaluations that are automatically run asynchronously as you upload logs. You can pick from the pre-built [autoevals](https://www.braintrust.dev/docs/reference/autoevals) functions or your custom scorers, and define a sampling rate along with more granular filters to control which logs get evaluated.

### [Configuring online evaluation](http://www.braintrust.dev/docs/guides/evals/write#configuring-online-evaluation)

To create an online evaluation, navigate to the **Configuration** tab in a project and create an online scoring rule.

The score will now automatically run at the specified sampling rate for all logs in the project.

### [Defining custom scoring logic](http://www.braintrust.dev/docs/guides/evals/write#defining-custom-scoring-logic)

In addition to the pre-built autoevals, you can define your own custom scoring logic by creating custom scorers. Currently, you can do that by visiting the [Playground](https://www.braintrust.dev/docs/guides/playground) and creating custom scorers.