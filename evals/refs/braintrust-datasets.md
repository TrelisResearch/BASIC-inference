Title: Datasets - Docs - Braintrust

URL Source: http://www.braintrust.dev/docs/guides/datasets

Markdown Content:
Datasets allow you to collect data from production, staging, evaluations, and even manually, and then use that data to run evaluations and track improvements over time.

For example, you can use Datasets to:

*   Store evaluation test cases for your eval script instead of managing large JSONL or CSV files
*   Log all production generations to assess quality manually or using model graded evals
*   Store user reviewed (, ) generations to find new test cases

In Braintrust, datasets have a few key properties:

*   **Integrated**. Datasets are integrated with the rest of the Braintrust platform, so you can use them in evaluations, explore them in the playground, and log to them from your staging/production environments.
*   **Versioned**. Every insert, update, and delete is versioned, so you can pin evaluations to a specific version of the dataset, rewind to a previous version, and track changes over time.
*   **Scalable**. Datasets are stored in a modern cloud data warehouse, so you can collect as much data as you want without worrying about storage or performance limits.
*   **Secure**. If you run Braintrust [in your cloud environment](https://www.braintrust.dev/docs/guides/self-hosting), datasets are stored in your warehouse and never touch our infrastructure.

Records in a dataset are stored as JSON objects, and each record has three top-level fields:

*   `input` is a set of inputs that you could use to recreate the example in your application. For example, if you're logging examples from a question answering model, the input might be the question.
*   `expected` (optional) is the output of your model. For example, if you're logging examples from a question answering model, this might be the answer. You can access `expected` when running evaluations as the `expected` field; however, `expected` does not need to be the ground truth.
*   `metadata` (optional) is a set of key-value pairs that you can use to filter and group your data. For example, if you're logging examples from a question answering model, the metadata might include the knowledge source that the question came from.

Datasets are created automatically when you initialize them in the SDK.

### [Inserting records](http://www.braintrust.dev/docs/guides/datasets#inserting-records)

You can use the SDK to initialize and insert into a dataset:

### [Updating records](http://www.braintrust.dev/docs/guides/datasets#updating-records)

In the above example, each `insert()` statement returns an `id`. You can use this `id` to update the record using `update()`:

The `update()` method applies a merge strategy: only the fields you provide will be updated, and all other existing fields in the record will remain unchanged.

### [Deleting records](http://www.braintrust.dev/docs/guides/datasets#deleting-records)

You can also delete records by `id`:

### [Flushing](http://www.braintrust.dev/docs/guides/datasets#flushing)

In both TypeScript and Python, the Braintrust SDK flushes records as fast as possible and installs an exit handler that tries to flush records, but these hooks are not always respected (e.g. by certain runtimes, or if you `exit` a process yourself). If you need to ensure that records are flushed, you can call `flush()` on the dataset.

In addition to managing datasets through the API, you can also manage them in the Braintrust UI.

### [Viewing a dataset](http://www.braintrust.dev/docs/guides/datasets#viewing-a-dataset)

You can view a dataset in the Braintrust UI by navigating to the project and then clicking on the dataset.

![Image 9: Dataset Viewer](https://www.braintrust.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fdatasets.68cdc1d2.webp&w=3840&q=75)

From the UI, you can filter records, create new ones, edit values, and delete records. You can also copy records between datasets and from experiments into datasets. This feature is commonly used to collect interesting or anomalous examples into a golden dataset.

#### [Create custom columns](http://www.braintrust.dev/docs/guides/datasets#create-custom-columns)

When viewing a dataset, create [custom columns](https://www.braintrust.dev/docs/guides/evals/interpret#create-custom-columns) to extract specific values from `input`, `expected`, or `metadata` fields.

### [Creating a dataset](http://www.braintrust.dev/docs/guides/datasets#creating-a-dataset-1)

The easiest way to create a dataset is to upload a CSV file.

![Image 10: Upload CSV](https://www.braintrust.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2FCSV-Upload.5ea37a5f.gif&w=3840&q=75)

### [Updating records](http://www.braintrust.dev/docs/guides/datasets#updating-records-1)

Once you've uploaded a dataset, you can update records or add new ones directly in the UI.

![Image 11: Edit record](https://www.braintrust.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2FEdit-record.95f7f315.gif&w=3840&q=75)

### [Labeling records](http://www.braintrust.dev/docs/guides/datasets#labeling-records)

In addition to updating datasets through the API, you can edit and label them in the UI. Like experiments and logs, you can configure [categorical fields](https://www.braintrust.dev/docs/guides/human-review#writing-to-expected-fields) to allow human reviewers to rapidly label records.

![Image 12: Write to expected](https://www.braintrust.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Fwrite-to-expected.f829f4b4.webp&w=3840&q=75)

You can use a dataset in an evaluation by passing it directly to the `Eval()` function.

You can also manually iterate through a dataset's records and run your tasks, then log the results to an experiment. Log the `id`s to link each dataset record to the corresponding result.

You can also use the results of an experiment as baseline data for future experiments by calling the `asDataset()`/`as_dataset()` function, which converts the experiment into dataset format (`input`, `expected`, and `metadata`).

For a more advanced overview of how to use an experiment as a baseline for other experiments, see [hill climbing](https://www.braintrust.dev/docs/guides/evals/write#hill-climbing).

To log to a dataset from your application, you can simply use the SDK and call `insert()`. Braintrust logs are queued and sent asynchronously, so you don't need to worry about critical path performance.

Since the SDK uses API keys, it's recommended that you log from a privileged environment (e.g. backend server), instead of client applications directly.

This example walks through how to track / from feedback:

### [Downloading large datasets](http://www.braintrust.dev/docs/guides/datasets#downloading-large-datasets)

If you are trying to load a very large dataset, you may run into timeout errors while using the SDK. If so, you can [paginate](https://www.braintrust.dev/docs/guides/api#downloading-a-dataset-using-pagination) through the dataset to download it in smaller chunks.