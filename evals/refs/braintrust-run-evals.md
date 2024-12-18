Title: Run evaluations - Docs - Braintrust

URL Source: http://www.braintrust.dev/docs/guides/evals/run

Markdown Content:
Braintrust allows you to create evaluations directly in your code, and run them in your development workflow or CI/CD pipeline. Once you have defined one or more evaluations, you can run them using the `braintrust eval` command. This command will run all evaluations in the specified files and directories. As they run, they will automatically log results to Braintrust and display a summary in your terminal.

You can run evaluations in watch-mode by passing the `--watch` flag. This will re-run evaluations whenever any of the files they depend on change.

Once you get the hang of running evaluations, you can integrate them into your CI/CD pipeline to automatically run them on every pull request or commit. This workflow allows you to catch eval regressions early and often.

The [`braintrustdata/eval-action`](https://github.com/braintrustdata/eval-action) action allows you to run evaluations directly in your Github workflow. Each time you run an evaluation, the action automatically posts a comment:

![Image 3: action comment](https://www.braintrust.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fgithub-actions-comment.f49b3e26.png&w=3840&q=75)

To use the action, simply include it in a workflow yaml file (`.github/workflows`):

You must specify `permissions` for the action to leave comments on your PR. Without these permissions, you'll see Github API errors.

For more information, see the [`braintrustdata/eval-action` README](https://github.com/braintrustdata/eval-action), or check out full workflow files in the [examples](https://github.com/braintrustdata/eval-action/tree/main/examples) directory.

The `braintrustdata/eval-action` GitHub action does not currently support custom reporters. If you use custom reporters, you'll need to run the `braintrust eval` command directly in your CI/CD pipeline.

Although you can invoke `Eval()` functions via the `braintrust eval` command, you can also call them directly in your code.

Sometimes, due to rate limits or other constraints, you may want to limit the number of concurrent evaluations in an `Eval()` call. Each `Eval()` lets you define `maxConcurrency`/`max_concurrency` to limit the number of concurrent test cases that run.

### [Stack traces](http://www.braintrust.dev/docs/guides/evals/run#stack-traces)

By default, the evaluation framework swallows errors in individual tasks, reports them to Braintrust, and prints a single line per error to the console. If you want to see the full stack trace for each error, you can pass the `--verbose` flag.

### [Why are my scores getting averaged?](http://www.braintrust.dev/docs/guides/evals/run#why-are-my-scores-getting-averaged)

Braintrust organizes your data into traces, each of which is a row in the experiments table. Within a trace, if you log the same score multiple times, it will be averaged in the table. This is a useful way to collect an overall measurement, e.g. if you compute the relevance of each retrieved document in a RAG use case, and want to see the overall relevance. However, if you want to see each score individually, you have a few options:

*   Split the input into multiple independent traces, and log each score in a separate trace. The [trials](http://www.braintrust.dev/docs/guides/evals/run#trials) feature will naturally average the results at the top-level, but allow you to view each individual output as a separate test case.
*   Compute a separate score for each instance. For example, if you have exactly 3 documents you retrieve every time, you may want to compute a separate score for the 1st, 2nd, and 3rd position.
*   Create separate experiments for each thing you're trying to score. For example, you may want to try out two different models and compute a score for each. In this case, if you split into separate experiments, you'll be able to diff across experiments and compare outputs side-by-side.

### [Node bundling errors (e.g. "cannot be marked as external")](http://www.braintrust.dev/docs/guides/evals/run#node-bundling-errors-eg-cannot-be-marked-as-external)

The `.eval.ts` files are bundled in a somewhat limiting way, via `esbuild` and a special set of build options that work in most cases, but not all. For example, if you have any `export` statements in them, you may see errors like "cannot be marked as external".

You can usually fix this specific error by removing `export` statements. However, if that does not work, or you want more control over how the files are bundled, you can also just run the files directly. `Eval` is an async function, so you can just call it directly in a script: