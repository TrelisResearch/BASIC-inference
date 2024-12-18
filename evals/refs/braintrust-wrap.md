Title: Write logs - Docs - Braintrust

URL Source: http://www.braintrust.dev/docs/guides/logs/write

Markdown Content:
Logs are more than a debugging tool— they are a key part of the feedback loop that drives continuous improvement in your AI application. There are several ways to log things in Braintrust, ranging from higher level for simple use cases, to more complex and customized [spans](https://www.braintrust.dev/docs/guides/traces/customize) for more control.

The simplest way to log to Braintrust is to wrap the code you wish to log with `wrapTraced`for TypeScript, or `@traced` for Python. This works for any function input and output provided. To learn more about tracing, check out the [tracing guide](https://www.braintrust.dev/docs/guides/traces).

Most commonly, logs are used for LLM calls. Braintrust includes a wrapper for the OpenAI API that automatically logs your requests. To use it, call `wrapOpenAI` for TypeScript, or `wrap_openai` for Python on your OpenAI instance. We intentionally _do not_ [monkey patch](https://en.wikipedia.org/wiki/Monkey_patch) the libraries directly, so that you can use the wrapper in a granular way.

Braintrust will automatically capture and log information behind the scenes:

![Image 3: Log code output](https://www.braintrust.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fsimple-log.682c5f15.png&w=3840&q=75)

You can use other AI model providers with the OpenAI client through the [AI proxy](https://www.braintrust.dev/docs/guides/proxy). You can also pick from a number of [integrations](https://www.braintrust.dev/docs/guides/traces/integrations) (OpenTelemetry, Vercel AI SDK, and others) or create a [custom LLM client wrapper](https://www.braintrust.dev/docs/guides/traces/customize#wrapping-a-custom-llm-client) in less than 10 lines of code.

### [Logging with `invoke`](http://www.braintrust.dev/docs/guides/logs/write#logging-with-invoke)

For more information about logging when using `invoke` to execute a prompt directly, check out the [prompt guide](https://www.braintrust.dev/docs/guides/functions/prompts#logging).

Braintrust supports logging user feedback, which can take multiple forms:

*   A **score** for a specific span, e.g. the output of a request could be 👍 (corresponding to 1) or 👎 (corresponding to 0), or a document retrieved in a vector search might be marked as relevant or irrelevant on a scale of 0-\>1.
*   An **expected** value, which gets saved in the `expected` field of a span, alongside `input` and `output`. This is a great place to store corrections.
*   A **comment**, which is a free-form text field that can be used to provide additional context.
*   Additional **metadata** fields, which allow you to track information about the feedback, like the `user_id` or `session_id`.

Each time you submit feedback, you can specify one or more of these fields using the `logFeedback()` / `log_feedback()` method, which simply needs you to specify the `span_id` corresponding to the span you want to log feedback for, and the feedback fields you want to update.

The following example shows how to log feedback within a simple API endpoint.

### [Collecting multiple scores](http://www.braintrust.dev/docs/guides/logs/write#collecting-multiple-scores)

Often, you want to collect multiple scores for a single span. For example, multiple users might provide independent feedback on a single document. Although each score and expected value is logged separately, each update overwrites the previous value. Instead, to capture multiple scores, you should create a new span for each submission, and log the score in the `scores` field. When you view and use the trace, Braintrust will automatically average the scores for you in the parent span(s).

### [Data model](http://www.braintrust.dev/docs/guides/logs/write#data-model)

*   Each log entry is associated with an organization and a project. If you do not specify a project name or id in `initLogger()`/`init_logger()`, the SDK will create and use a project named "Global".
*   Although logs are associated with a single project, you can still use them in evaluations or datasets that belong to any project.
*   Like evaluation experiments, log entries contain optional `input`, `output`, `expected`, `scores`, `metadata`, and `metrics` fields. These fields are optional, but we encourage you to use them to provide context to your logs.
*   Logs are indexed automatically to enable efficient search. When you load logs, Braintrust automatically returns the most recently updated log entries first. You can also search by arbitrary subfields, e.g. `metadata.user_id = '1234'`. Currently, inequality filters, e.g. `scores.accuracy > 0.5` do not use an index.

### [Production vs. staging](http://www.braintrust.dev/docs/guides/logs/write#production-vs-staging)

There are a few ways to handle production vs. staging data. The most common pattern we see is to split them into different projects, so that they are separated and code changes to staging cannot affect production. Separating projects also allows you to enforce [access controls](https://www.braintrust.dev/docs/guides/access-control) at the project level.

Alternatively, if it's easier to keep things in one project (e.g. to have a single spot to triage them), you can use tags to separate them. If you need to physically isolate production and staging, you can create separate organizations, each mapping to a different deployment.

Experiments, prompts, and playgrounds can all use data across projects. For example, if you want to reference a prompt from your production project in your staging logs, or evaluate using a dataset from staging in a different project, you can do so.

### [Initializing](http://www.braintrust.dev/docs/guides/logs/write#initializing)

The `initLogger()`/`init_logger()` method initializes the logger. Unlike the experiment `init()` method, the logger lazily initializes itself, so that you can call `initLogger()`/`init_logger()` at the top of your file (in module scope). The first time you `log()` or start a span, the logger will log into Braintrust and retrieve/initialize project details.

### [Flushing](http://www.braintrust.dev/docs/guides/logs/write#flushing)

The SDK can operate in two modes: either it sends log statements to the server after each request, or it buffers them in memory and sends them over in batches. Batching reduces the number of network requests and makes the `log()` command as fast as possible. Each SDK flushes logs to the server as fast as possible, and attempts to flush any outstanding logs when the program terminates.

You can enable background batching by setting the `asyncFlush` / `async_flush` flag to `true` in `initLogger()`/`init_logger()`. When async flush mode is on, you can use the `.flush()` method to manually flush any outstanding logs to the server.

### [Serverless environments](http://www.braintrust.dev/docs/guides/logs/write#serverless-environments)

The `asyncFlush` / `async_flush` flag controls whether or not logs are flushed when a trace completes. This flag should be set to `false` in serverless environments (**other than Vercel**) where the process may halt as soon as the request completes. By default, `asyncFlush` is set to `false` in the TypeScript SDK, since most TypeScript applications are serverless, and `True` in Python.

#### [Vercel](http://www.braintrust.dev/docs/guides/logs/write#vercel)

Braintrust automatically utilizes Vercel's `waitUntil` functionality if it's available, so you can set `asyncFlush: true` in Vercel and your requests will _not_ need to block on logging.

For more advanced logging topics, see the [advanced logging guide](https://www.braintrust.dev/docs/guides/logs/advanced).