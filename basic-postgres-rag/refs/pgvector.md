Title: GitHub - pgvector/pgvector: Open-source vector similarity search for Postgres

URL Source: http://github.com/pgvector/pgvector

Markdown Content:
pgvector
--------

[](http://github.com/pgvector/pgvector#pgvector)

Open-source vector similarity search for Postgres

Store your vectors with the rest of your data. Supports:

*   exact and approximate nearest neighbor search
*   single-precision, half-precision, binary, and sparse vectors
*   L2 distance, inner product, cosine distance, L1 distance, Hamming distance, and Jaccard distance
*   any [language](http://github.com/pgvector/pgvector#languages) with a Postgres client

Plus [ACID](https://en.wikipedia.org/wiki/ACID) compliance, point-in-time recovery, JOINs, and all of the other [great features](https://www.postgresql.org/about/) of Postgres

[![Image 17: Build Status](https://github.com/pgvector/pgvector/actions/workflows/build.yml/badge.svg)](https://github.com/pgvector/pgvector/actions)

Installation
------------

[](http://github.com/pgvector/pgvector#installation)

### Linux and Mac

[](http://github.com/pgvector/pgvector#linux-and-mac)

Compile and install the extension (supports Postgres 13+)

cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install # may need sudo

See the [installation notes](http://github.com/pgvector/pgvector#installation-notes---linux-and-mac) if you run into issues

You can also install it with [Docker](http://github.com/pgvector/pgvector#docker), [Homebrew](http://github.com/pgvector/pgvector#homebrew), [PGXN](http://github.com/pgvector/pgvector#pgxn), [APT](http://github.com/pgvector/pgvector#apt), [Yum](http://github.com/pgvector/pgvector#yum), [pkg](http://github.com/pgvector/pgvector#pkg), or [conda-forge](http://github.com/pgvector/pgvector#conda-forge), and it comes preinstalled with [Postgres.app](http://github.com/pgvector/pgvector#postgresapp) and many [hosted providers](http://github.com/pgvector/pgvector#hosted-postgres). There are also instructions for [GitHub Actions](https://github.com/pgvector/setup-pgvector).

### Windows

[](http://github.com/pgvector/pgvector#windows)

Ensure [C++ support in Visual Studio](https://learn.microsoft.com/en-us/cpp/build/building-on-the-command-line?view=msvc-170#download-and-install-the-tools) is installed, and run:

call "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Auxiliary\\Build\\vcvars64.bat"

Note: The exact path will vary depending on your Visual Studio version and edition

Then use `nmake` to build:

set "PGROOT\=C:\\Program Files\\PostgreSQL\\16"
cd %TEMP%
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
nmake /F Makefile.win
nmake /F Makefile.win install

Note: Postgres 17 is not supported with MSVC yet due to an [upstream issue](https://www.postgresql.org/message-id/flat/CAOdR5yF0krWrxycA04rgUKCgKugRvGWzzGLAhDZ9bzNv8g0Lag%40mail.gmail.com)

See the [installation notes](http://github.com/pgvector/pgvector#installation-notes---windows) if you run into issues

You can also install it with [Docker](http://github.com/pgvector/pgvector#docker) or [conda-forge](http://github.com/pgvector/pgvector#conda-forge).

Getting Started
---------------

[](http://github.com/pgvector/pgvector#getting-started)

Enable the extension (do this once in each database where you want to use it)

Create a vector column with 3 dimensions

CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));

Insert vectors

INSERT INTO items (embedding) VALUES ('\[1,2,3\]'), ('\[4,5,6\]');

Get the nearest neighbors by L2 distance

SELECT \* FROM items ORDER BY embedding <\-\> '\[3,1,2\]' LIMIT 5;

Also supports inner product (`<#>`), cosine distance (`<=>`), and L1 distance (`<+>`, added in 0.7.0)

Note: `<#>` returns the negative inner product since Postgres only supports `ASC` order index scans on operators

Storing
-------

[](http://github.com/pgvector/pgvector#storing)

Create a new table with a vector column

CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));

Or add a vector column to an existing table

ALTER TABLE items ADD COLUMN embedding vector(3);

Also supports [half-precision](http://github.com/pgvector/pgvector#half-precision-vectors), [binary](http://github.com/pgvector/pgvector#binary-vectors), and [sparse](http://github.com/pgvector/pgvector#sparse-vectors) vectors

Insert vectors

INSERT INTO items (embedding) VALUES ('\[1,2,3\]'), ('\[4,5,6\]');

Or load vectors in bulk using `COPY` ([example](https://github.com/pgvector/pgvector-python/blob/master/examples/loading/example.py))

COPY items (embedding) FROM STDIN WITH (FORMAT BINARY);

Upsert vectors

INSERT INTO items (id, embedding) VALUES (1, '\[1,2,3\]'), (2, '\[4,5,6\]')
    ON CONFLICT (id) DO UPDATE SET embedding \= EXCLUDED.embedding;

Update vectors

UPDATE items SET embedding \= '\[1,2,3\]' WHERE id \= 1;

Delete vectors

DELETE FROM items WHERE id \= 1;

Querying
--------

[](http://github.com/pgvector/pgvector#querying)

Get the nearest neighbors to a vector

SELECT \* FROM items ORDER BY embedding <\-\> '\[3,1,2\]' LIMIT 5;

Supported distance functions are:

*   `<->` - L2 distance
*   `<#>` - (negative) inner product
*   `<=>` - cosine distance
*   `<+>` - L1 distance (added in 0.7.0)
*   `<~>` - Hamming distance (binary vectors, added in 0.7.0)
*   `<%>` - Jaccard distance (binary vectors, added in 0.7.0)

Get the nearest neighbors to a row

SELECT \* FROM items WHERE id != 1 ORDER BY embedding <\-\> (SELECT embedding FROM items WHERE id \= 1) LIMIT 5;

Get rows within a certain distance

SELECT \* FROM items WHERE embedding <\-\> '\[3,1,2\]' < 5;

Note: Combine with `ORDER BY` and `LIMIT` to use an index

#### Distances

[](http://github.com/pgvector/pgvector#distances)

Get the distance

SELECT embedding <\-\> '\[3,1,2\]' AS distance FROM items;

For inner product, multiply by -1 (since `<#>` returns the negative inner product)

SELECT (embedding <#\> '\[3,1,2\]') \* \-1 AS inner\_product FROM items;

For cosine similarity, use 1 - cosine distance

SELECT 1 \- (embedding <\=\> '\[3,1,2\]') AS cosine\_similarity FROM items;

#### Aggregates

[](http://github.com/pgvector/pgvector#aggregates)

Average vectors

SELECT AVG(embedding) FROM items;

Average groups of vectors

SELECT category\_id, AVG(embedding) FROM items GROUP BY category\_id;

Indexing
--------

[](http://github.com/pgvector/pgvector#indexing)

By default, pgvector performs exact nearest neighbor search, which provides perfect recall.

You can add an index to use approximate nearest neighbor search, which trades some recall for speed. Unlike typical indexes, you will see different results for queries after adding an approximate index.

Supported index types are:

*   [HNSW](http://github.com/pgvector/pgvector#hnsw)
*   [IVFFlat](http://github.com/pgvector/pgvector#ivfflat)

HNSW
----

[](http://github.com/pgvector/pgvector#hnsw)

An HNSW index creates a multilayer graph. It has better query performance than IVFFlat (in terms of speed-recall tradeoff), but has slower build times and uses more memory. Also, an index can be created without any data in the table since there isn’t a training step like IVFFlat.

Add an index for each distance function you want to use.

L2 distance

CREATE INDEX ON items USING hnsw (embedding vector\_l2\_ops);

Note: Use `halfvec_l2_ops` for `halfvec` and `sparsevec_l2_ops` for `sparsevec` (and similar with the other distance functions)

Inner product

CREATE INDEX ON items USING hnsw (embedding vector\_ip\_ops);

Cosine distance

CREATE INDEX ON items USING hnsw (embedding vector\_cosine\_ops);

L1 distance - added in 0.7.0

CREATE INDEX ON items USING hnsw (embedding vector\_l1\_ops);

Hamming distance - added in 0.7.0

CREATE INDEX ON items USING hnsw (embedding bit\_hamming\_ops);

Jaccard distance - added in 0.7.0

CREATE INDEX ON items USING hnsw (embedding bit\_jaccard\_ops);

Supported types are:

*   `vector` - up to 2,000 dimensions
*   `halfvec` - up to 4,000 dimensions (added in 0.7.0)
*   `bit` - up to 64,000 dimensions (added in 0.7.0)
*   `sparsevec` - up to 1,000 non-zero elements (added in 0.7.0)

### Index Options

[](http://github.com/pgvector/pgvector#index-options)

Specify HNSW parameters

*   `m` - the max number of connections per layer (16 by default)
*   `ef_construction` - the size of the dynamic candidate list for constructing the graph (64 by default)

CREATE INDEX ON items USING hnsw (embedding vector\_l2\_ops) WITH (m \= 16, ef\_construction \= 64);

A higher value of `ef_construction` provides better recall at the cost of index build time / insert speed.

### Query Options

[](http://github.com/pgvector/pgvector#query-options)

Specify the size of the dynamic candidate list for search (40 by default)

SET hnsw.ef\_search \= 100;

A higher value provides better recall at the cost of speed.

Use `SET LOCAL` inside a transaction to set it for a single query

BEGIN;
SET LOCAL hnsw.ef\_search \= 100;
SELECT ...
COMMIT;

### Index Build Time

[](http://github.com/pgvector/pgvector#index-build-time)

Indexes build significantly faster when the graph fits into `maintenance_work_mem`

SET maintenance\_work\_mem \= '8GB';

A notice is shown when the graph no longer fits

```
NOTICE:  hnsw graph no longer fits into maintenance_work_mem after 100000 tuples
DETAIL:  Building will take significantly more time.
HINT:  Increase maintenance_work_mem to speed up builds.
```

Note: Do not set `maintenance_work_mem` so high that it exhausts the memory on the server

Like other index types, it’s faster to create an index after loading your initial data

Starting with 0.6.0, you can also speed up index creation by increasing the number of parallel workers (2 by default)

SET max\_parallel\_maintenance\_workers \= 7; \-- plus leader

For a large number of workers, you may also need to increase `max_parallel_workers` (8 by default)

### Indexing Progress

[](http://github.com/pgvector/pgvector#indexing-progress)

Check [indexing progress](https://www.postgresql.org/docs/current/progress-reporting.html#CREATE-INDEX-PROGRESS-REPORTING)

SELECT phase, round(100.0 \* blocks\_done / nullif(blocks\_total, 0), 1) AS "%" FROM pg\_stat\_progress\_create\_index;

The phases for HNSW are:

1.  `initializing`
2.  `loading tuples`

IVFFlat
-------

[](http://github.com/pgvector/pgvector#ivfflat)

An IVFFlat index divides vectors into lists, and then searches a subset of those lists that are closest to the query vector. It has faster build times and uses less memory than HNSW, but has lower query performance (in terms of speed-recall tradeoff).

Three keys to achieving good recall are:

1.  Create the index _after_ the table has some data
2.  Choose an appropriate number of lists - a good place to start is `rows / 1000` for up to 1M rows and `sqrt(rows)` for over 1M rows
3.  When querying, specify an appropriate number of [probes](http://github.com/pgvector/pgvector#query-options) (higher is better for recall, lower is better for speed) - a good place to start is `sqrt(lists)`

Add an index for each distance function you want to use.

L2 distance

CREATE INDEX ON items USING ivfflat (embedding vector\_l2\_ops) WITH (lists \= 100);

Note: Use `halfvec_l2_ops` for `halfvec` (and similar with the other distance functions)

Inner product

CREATE INDEX ON items USING ivfflat (embedding vector\_ip\_ops) WITH (lists \= 100);

Cosine distance

CREATE INDEX ON items USING ivfflat (embedding vector\_cosine\_ops) WITH (lists \= 100);

Hamming distance - added in 0.7.0

CREATE INDEX ON items USING ivfflat (embedding bit\_hamming\_ops) WITH (lists \= 100);

Supported types are:

*   `vector` - up to 2,000 dimensions
*   `halfvec` - up to 4,000 dimensions (added in 0.7.0)
*   `bit` - up to 64,000 dimensions (added in 0.7.0)

### Query Options

[](http://github.com/pgvector/pgvector#query-options-1)

Specify the number of probes (1 by default)

A higher value provides better recall at the cost of speed, and it can be set to the number of lists for exact nearest neighbor search (at which point the planner won’t use the index)

Use `SET LOCAL` inside a transaction to set it for a single query

BEGIN;
SET LOCAL ivfflat.probes \= 10;
SELECT ...
COMMIT;

### Index Build Time

[](http://github.com/pgvector/pgvector#index-build-time-1)

Speed up index creation on large tables by increasing the number of parallel workers (2 by default)

SET max\_parallel\_maintenance\_workers \= 7; \-- plus leader

For a large number of workers, you may also need to increase `max_parallel_workers` (8 by default)

### Indexing Progress

[](http://github.com/pgvector/pgvector#indexing-progress-1)

Check [indexing progress](https://www.postgresql.org/docs/current/progress-reporting.html#CREATE-INDEX-PROGRESS-REPORTING)

SELECT phase, round(100.0 \* tuples\_done / nullif(tuples\_total, 0), 1) AS "%" FROM pg\_stat\_progress\_create\_index;

The phases for IVFFlat are:

1.  `initializing`
2.  `performing k-means`
3.  `assigning tuples`
4.  `loading tuples`

Note: `%` is only populated during the `loading tuples` phase

Filtering
---------

[](http://github.com/pgvector/pgvector#filtering)

There are a few ways to index nearest neighbor queries with a `WHERE` clause.

SELECT \* FROM items WHERE category\_id \= 123 ORDER BY embedding <\-\> '\[3,1,2\]' LIMIT 5;

A good place to start is creating an index on the filter column. This can provide fast, exact nearest neighbor search in many cases. Postgres has a number of [index types](https://www.postgresql.org/docs/current/indexes-types.html) for this: B-tree (default), hash, GiST, SP-GiST, GIN, and BRIN.

CREATE INDEX ON items (category\_id);

For multiple columns, consider a [multicolumn index](https://www.postgresql.org/docs/current/indexes-multicolumn.html).

CREATE INDEX ON items (location\_id, category\_id);

Exact indexes work well for conditions that match a low percentage of rows. Otherwise, [approximate indexes](http://github.com/pgvector/pgvector#indexing) can work better.

CREATE INDEX ON items USING hnsw (embedding vector\_l2\_ops);

With approximate indexes, filtering is applied _after_ the index is scanned. If a condition matches 10% of rows, with HNSW and the default `hnsw.ef_search` of 40, only 4 rows will match on average. For more rows, increase `hnsw.ef_search`.

SET hnsw.ef\_search \= 200;

Starting with 0.8.0, you can enable [iterative index scans](http://github.com/pgvector/pgvector#iterative-index-scans), which will automatically scan more of the index when needed.

SET hnsw.iterative\_scan \= strict\_order;

If filtering by only a few distinct values, consider [partial indexing](https://www.postgresql.org/docs/current/indexes-partial.html).

CREATE INDEX ON items USING hnsw (embedding vector\_l2\_ops) WHERE (category\_id \= 123);

If filtering by many different values, consider [partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html).

CREATE TABLE items (embedding vector(3), category\_id int) PARTITION BY LIST(category\_id);

Iterative Index Scans
---------------------

[](http://github.com/pgvector/pgvector#iterative-index-scans)

_Added in 0.8.0_

With approximate indexes, queries with filtering can return less results since filtering is applied _after_ the index is scanned. Starting with 0.8.0, you can enable iterative index scans, which will automatically scan more of the index until enough results are found (or it reaches `hnsw.max_scan_tuples` or `ivfflat.max_probes`).

Iterative scans can use strict or relaxed ordering.

Strict ensures results are in the exact order by distance

SET hnsw.iterative\_scan \= strict\_order;

Relaxed allows results to be slightly out of order by distance, but provides better recall

SET hnsw.iterative\_scan \= relaxed\_order;
# or
SET ivfflat.iterative\_scan \= relaxed\_order;

With relaxed ordering, you can use a [materialized CTE](https://www.postgresql.org/docs/current/queries-with.html#QUERIES-WITH-CTE-MATERIALIZATION) to get strict ordering

WITH relaxed\_results AS MATERIALIZED (
    SELECT id, embedding <\-\> '\[1,2,3\]' AS distance FROM items WHERE category\_id \= 123 ORDER BY distance LIMIT 5
) SELECT \* FROM relaxed\_results ORDER BY distance;

For queries that filter by distance, use a materialized CTE and place the distance filter outside of it for best performance (due to the [current behavior](https://www.postgresql.org/message-id/flat/CAOdR5yGUoMQ6j7M5hNUXrySzaqZVGf_Ne%2B8fwZMRKTFxU1nbJg%40mail.gmail.com) of the Postgres executor)

WITH nearest\_results AS MATERIALIZED (
    SELECT id, embedding <\-\> '\[1,2,3\]' AS distance FROM items ORDER BY distance LIMIT 5
) SELECT \* FROM nearest\_results WHERE distance < 5 ORDER BY distance;

Note: Place any other filters inside the CTE

### Iterative Scan Options

[](http://github.com/pgvector/pgvector#iterative-scan-options)

Since scanning a large portion of an approximate index is expensive, there are options to control when a scan ends.

#### HNSW

[](http://github.com/pgvector/pgvector#hnsw-1)

Specify the max number of tuples to visit (20,000 by default)

SET hnsw.max\_scan\_tuples \= 20000;

Note: This is approximate and does not affect the initial scan

Specify the max amount of memory to use, as a multiple of `work_mem` (1 by default)

SET hnsw.scan\_mem\_multiplier \= 2;

Note: Try increasing this if increasing `hnsw.max_scan_tuples` does not improve recall

#### IVFFlat

[](http://github.com/pgvector/pgvector#ivfflat-1)

Specify the max number of probes

SET ivfflat.max\_probes \= 100;

Note: If this is lower than `ivfflat.probes`, `ivfflat.probes` will be used

Half-Precision Vectors
----------------------

[](http://github.com/pgvector/pgvector#half-precision-vectors)

_Added in 0.7.0_

Use the `halfvec` type to store half-precision vectors

CREATE TABLE items (id bigserial PRIMARY KEY, embedding halfvec(3));

Half-Precision Indexing
-----------------------

[](http://github.com/pgvector/pgvector#half-precision-indexing)

_Added in 0.7.0_

Index vectors at half precision for smaller indexes

CREATE INDEX ON items USING hnsw ((embedding::halfvec(3)) halfvec\_l2\_ops);

Get the nearest neighbors

SELECT \* FROM items ORDER BY embedding::halfvec(3) <\-\> '\[1,2,3\]' LIMIT 5;

Binary Vectors
--------------

[](http://github.com/pgvector/pgvector#binary-vectors)

Use the `bit` type to store binary vectors ([example](https://github.com/pgvector/pgvector-python/blob/master/examples/imagehash/example.py))

CREATE TABLE items (id bigserial PRIMARY KEY, embedding bit(3));
INSERT INTO items (embedding) VALUES ('000'), ('111');

Get the nearest neighbors by Hamming distance (added in 0.7.0)

SELECT \* FROM items ORDER BY embedding <~\> '101' LIMIT 5;

Or (before 0.7.0)

SELECT \* FROM items ORDER BY bit\_count(embedding # '101') LIMIT 5;

Also supports Jaccard distance (`<%>`)

Binary Quantization
-------------------

[](http://github.com/pgvector/pgvector#binary-quantization)

_Added in 0.7.0_

Use expression indexing for binary quantization

CREATE INDEX ON items USING hnsw ((binary\_quantize(embedding)::bit(3)) bit\_hamming\_ops);

Get the nearest neighbors by Hamming distance

SELECT \* FROM items ORDER BY binary\_quantize(embedding)::bit(3) <~\> binary\_quantize('\[1,-2,3\]') LIMIT 5;

Re-rank by the original vectors for better recall

SELECT \* FROM (
    SELECT \* FROM items ORDER BY binary\_quantize(embedding)::bit(3) <~\> binary\_quantize('\[1,-2,3\]') LIMIT 20
) ORDER BY embedding <\=\> '\[1,-2,3\]' LIMIT 5;

Sparse Vectors
--------------

[](http://github.com/pgvector/pgvector#sparse-vectors)

_Added in 0.7.0_

Use the `sparsevec` type to store sparse vectors

CREATE TABLE items (id bigserial PRIMARY KEY, embedding sparsevec(5));

Insert vectors

INSERT INTO items (embedding) VALUES ('{1:1,3:2,5:3}/5'), ('{1:4,3:5,5:6}/5');

The format is `{index1:value1,index2:value2}/dimensions` and indices start at 1 like SQL arrays

Get the nearest neighbors by L2 distance

SELECT \* FROM items ORDER BY embedding <\-\> '{1:3,3:1,5:2}/5' LIMIT 5;

Hybrid Search
-------------

[](http://github.com/pgvector/pgvector#hybrid-search)

Use together with Postgres [full-text search](https://www.postgresql.org/docs/current/textsearch-intro.html) for hybrid search.

SELECT id, content FROM items, plainto\_tsquery('hello search') query
    WHERE textsearch @@ query ORDER BY ts\_rank\_cd(textsearch, query) DESC LIMIT 5;

You can use [Reciprocal Rank Fusion](https://github.com/pgvector/pgvector-python/blob/master/examples/hybrid_search/rrf.py) or a [cross-encoder](https://github.com/pgvector/pgvector-python/blob/master/examples/hybrid_search/cross_encoder.py) to combine results.

Indexing Subvectors
-------------------

[](http://github.com/pgvector/pgvector#indexing-subvectors)

_Added in 0.7.0_

Use expression indexing to index subvectors

CREATE INDEX ON items USING hnsw ((subvector(embedding, 1, 3)::vector(3)) vector\_cosine\_ops);

Get the nearest neighbors by cosine distance

SELECT \* FROM items ORDER BY subvector(embedding, 1, 3)::vector(3) <\=\> subvector('\[1,2,3,4,5\]'::vector, 1, 3) LIMIT 5;

Re-rank by the full vectors for better recall

SELECT \* FROM (
    SELECT \* FROM items ORDER BY subvector(embedding, 1, 3)::vector(3) <\=\> subvector('\[1,2,3,4,5\]'::vector, 1, 3) LIMIT 20
) ORDER BY embedding <\=\> '\[1,2,3,4,5\]' LIMIT 5;

Performance
-----------

[](http://github.com/pgvector/pgvector#performance)

### Tuning

[](http://github.com/pgvector/pgvector#tuning)

Use a tool like [PgTune](https://pgtune.leopard.in.ua/) to set initial values for Postgres server parameters. For instance, `shared_buffers` should typically be 25% of the server’s memory. You can find the config file with:

And check individual settings with:

Be sure to restart Postgres for changes to take effect.

### Loading

[](http://github.com/pgvector/pgvector#loading)

Use `COPY` for bulk loading data ([example](https://github.com/pgvector/pgvector-python/blob/master/examples/loading/example.py)).

COPY items (embedding) FROM STDIN WITH (FORMAT BINARY);

Add any indexes _after_ loading the initial data for best performance.

### Indexing

[](http://github.com/pgvector/pgvector#indexing-1)

See index build time for [HNSW](http://github.com/pgvector/pgvector#index-build-time) and [IVFFlat](http://github.com/pgvector/pgvector#index-build-time-1).

In production environments, create indexes concurrently to avoid blocking writes.

CREATE INDEX CONCURRENTLY ...

### Querying

[](http://github.com/pgvector/pgvector#querying-1)

Use `EXPLAIN ANALYZE` to debug performance.

EXPLAIN ANALYZE SELECT \* FROM items ORDER BY embedding <\-\> '\[3,1,2\]' LIMIT 5;

#### Exact Search

[](http://github.com/pgvector/pgvector#exact-search)

To speed up queries without an index, increase `max_parallel_workers_per_gather`.

SET max\_parallel\_workers\_per\_gather \= 4;

If vectors are normalized to length 1 (like [OpenAI embeddings](https://platform.openai.com/docs/guides/embeddings/which-distance-function-should-i-use)), use inner product for best performance.

SELECT \* FROM items ORDER BY embedding <#\> '\[3,1,2\]' LIMIT 5;

#### Approximate Search

[](http://github.com/pgvector/pgvector#approximate-search)

To speed up queries with an IVFFlat index, increase the number of inverted lists (at the expense of recall).

CREATE INDEX ON items USING ivfflat (embedding vector\_l2\_ops) WITH (lists \= 1000);

### Vacuuming

[](http://github.com/pgvector/pgvector#vacuuming)

Vacuuming can take a while for HNSW indexes. Speed it up by reindexing first.

REINDEX INDEX CONCURRENTLY index\_name;
VACUUM table\_name;

Monitoring
----------

[](http://github.com/pgvector/pgvector#monitoring)

Monitor performance with [pg\_stat\_statements](https://www.postgresql.org/docs/current/pgstatstatements.html) (be sure to add it to `shared_preload_libraries`).

CREATE EXTENSION pg\_stat\_statements;

Get the most time-consuming queries with:

SELECT query, calls, ROUND((total\_plan\_time + total\_exec\_time) / calls) AS avg\_time\_ms,
    ROUND((total\_plan\_time + total\_exec\_time) / 60000) AS total\_time\_min
    FROM pg\_stat\_statements ORDER BY total\_plan\_time + total\_exec\_time DESC LIMIT 20;

Note: Replace `total_plan_time + total_exec_time` with `total_time` for Postgres < 13

Monitor recall by comparing results from approximate search with exact search.

BEGIN;
SET LOCAL enable\_indexscan \= off; \-- use exact search
SELECT ...
COMMIT;

Scaling
-------

[](http://github.com/pgvector/pgvector#scaling)

Scale pgvector the same way you scale Postgres.

Scale vertically by increasing memory, CPU, and storage on a single instance. Use existing tools to [tune parameters](http://github.com/pgvector/pgvector#tuning) and [monitor performance](http://github.com/pgvector/pgvector#monitoring).

Scale horizontally with [replicas](https://www.postgresql.org/docs/current/hot-standby.html), or use [Citus](https://github.com/citusdata/citus) or another approach for sharding ([example](https://github.com/pgvector/pgvector-python/blob/master/examples/citus/example.py)).

Languages
---------

[](http://github.com/pgvector/pgvector#languages)

Use pgvector from any language with a Postgres client. You can even generate and store vectors in one language and query them in another.

| Language | Libraries / Examples |
| --- | --- |
| C | [pgvector-c](https://github.com/pgvector/pgvector-c) |
| C++ | [pgvector-cpp](https://github.com/pgvector/pgvector-cpp) |
| C#, F#, Visual Basic | [pgvector-dotnet](https://github.com/pgvector/pgvector-dotnet) |
| Crystal | [pgvector-crystal](https://github.com/pgvector/pgvector-crystal) |
| D | [pgvector-d](https://github.com/pgvector/pgvector-d) |
| Dart | [pgvector-dart](https://github.com/pgvector/pgvector-dart) |
| Elixir | [pgvector-elixir](https://github.com/pgvector/pgvector-elixir) |
| Erlang | [pgvector-erlang](https://github.com/pgvector/pgvector-erlang) |
| Fortran | [pgvector-fortran](https://github.com/pgvector/pgvector-fortran) |
| Gleam | [pgvector-gleam](https://github.com/pgvector/pgvector-gleam) |
| Go | [pgvector-go](https://github.com/pgvector/pgvector-go) |
| Haskell | [pgvector-haskell](https://github.com/pgvector/pgvector-haskell) |
| Java, Kotlin, Groovy, Scala | [pgvector-java](https://github.com/pgvector/pgvector-java) |
| JavaScript, TypeScript | [pgvector-node](https://github.com/pgvector/pgvector-node) |
| Julia | [pgvector-julia](https://github.com/pgvector/pgvector-julia) |
| Lisp | [pgvector-lisp](https://github.com/pgvector/pgvector-lisp) |
| Lua | [pgvector-lua](https://github.com/pgvector/pgvector-lua) |
| Nim | [pgvector-nim](https://github.com/pgvector/pgvector-nim) |
| OCaml | [pgvector-ocaml](https://github.com/pgvector/pgvector-ocaml) |
| Perl | [pgvector-perl](https://github.com/pgvector/pgvector-perl) |
| PHP | [pgvector-php](https://github.com/pgvector/pgvector-php) |
| Python | [pgvector-python](https://github.com/pgvector/pgvector-python) |
| R | [pgvector-r](https://github.com/pgvector/pgvector-r) |
| Raku | [pgvector-raku](https://github.com/pgvector/pgvector-raku) |
| Ruby | [pgvector-ruby](https://github.com/pgvector/pgvector-ruby), [Neighbor](https://github.com/ankane/neighbor) |
| Rust | [pgvector-rust](https://github.com/pgvector/pgvector-rust) |
| Swift | [pgvector-swift](https://github.com/pgvector/pgvector-swift) |
| Zig | [pgvector-zig](https://github.com/pgvector/pgvector-zig) |

Frequently Asked Questions
--------------------------

[](http://github.com/pgvector/pgvector#frequently-asked-questions)

#### How many vectors can be stored in a single table?

[](http://github.com/pgvector/pgvector#how-many-vectors-can-be-stored-in-a-single-table)

A non-partitioned table has a limit of 32 TB by default in Postgres. A partitioned table can have thousands of partitions of that size.

#### Is replication supported?

[](http://github.com/pgvector/pgvector#is-replication-supported)

Yes, pgvector uses the write-ahead log (WAL), which allows for replication and point-in-time recovery.

#### What if I want to index vectors with more than 2,000 dimensions?

[](http://github.com/pgvector/pgvector#what-if-i-want-to-index-vectors-with-more-than-2000-dimensions)

You can use [half-precision indexing](http://github.com/pgvector/pgvector#half-precision-indexing) to index up to 4,000 dimensions or [binary quantization](http://github.com/pgvector/pgvector#binary-quantization) to index up to 64,000 dimensions. Another option is [dimensionality reduction](https://en.wikipedia.org/wiki/Dimensionality_reduction).

#### Can I store vectors with different dimensions in the same column?

[](http://github.com/pgvector/pgvector#can-i-store-vectors-with-different-dimensions-in-the-same-column)

You can use `vector` as the type (instead of `vector(3)`).

CREATE TABLE embeddings (model\_id bigint, item\_id bigint, embedding vector, PRIMARY KEY (model\_id, item\_id));

However, you can only create indexes on rows with the same number of dimensions (using [expression](https://www.postgresql.org/docs/current/indexes-expressional.html) and [partial](https://www.postgresql.org/docs/current/indexes-partial.html) indexing):

CREATE INDEX ON embeddings USING hnsw ((embedding::vector(3)) vector\_l2\_ops) WHERE (model\_id \= 123);

and query with:

SELECT \* FROM embeddings WHERE model\_id \= 123 ORDER BY embedding::vector(3) <\-\> '\[3,1,2\]' LIMIT 5;

#### Can I store vectors with more precision?

[](http://github.com/pgvector/pgvector#can-i-store-vectors-with-more-precision)

You can use the `double precision[]` or `numeric[]` type to store vectors with more precision.

CREATE TABLE items (id bigserial PRIMARY KEY, embedding double precision\[\]);

\-- use {} instead of \[\] for Postgres arrays
INSERT INTO items (embedding) VALUES ('{1,2,3}'), ('{4,5,6}');

Optionally, add a [check constraint](https://www.postgresql.org/docs/current/ddl-constraints.html) to ensure data can be converted to the `vector` type and has the expected dimensions.

ALTER TABLE items ADD CHECK (vector\_dims(embedding::vector) \= 3);

Use [expression indexing](https://www.postgresql.org/docs/current/indexes-expressional.html) to index (at a lower precision):

CREATE INDEX ON items USING hnsw ((embedding::vector(3)) vector\_l2\_ops);

and query with:

SELECT \* FROM items ORDER BY embedding::vector(3) <\-\> '\[3,1,2\]' LIMIT 5;

#### Do indexes need to fit into memory?

[](http://github.com/pgvector/pgvector#do-indexes-need-to-fit-into-memory)

No, but like other index types, you’ll likely see better performance if they do. You can get the size of an index with:

SELECT pg\_size\_pretty(pg\_relation\_size('index\_name'));

Troubleshooting
---------------

[](http://github.com/pgvector/pgvector#troubleshooting)

#### Why isn’t a query using an index?

[](http://github.com/pgvector/pgvector#why-isnt-a-query-using-an-index)

The query needs to have an `ORDER BY` and `LIMIT`, and the `ORDER BY` must be the result of a distance operator (not an expression) in ascending order.

\-- index
ORDER BY embedding <\=\> '\[3,1,2\]' LIMIT 5;

\-- no index
ORDER BY 1 \- (embedding <\=\> '\[3,1,2\]') DESC LIMIT 5;

You can encourage the planner to use an index for a query with:

BEGIN;
SET LOCAL enable\_seqscan \= off;
SELECT ...
COMMIT;

Also, if the table is small, a table scan may be faster.

#### Why isn’t a query using a parallel table scan?

[](http://github.com/pgvector/pgvector#why-isnt-a-query-using-a-parallel-table-scan)

The planner doesn’t consider [out-of-line storage](https://www.postgresql.org/docs/current/storage-toast.html) in cost estimates, which can make a serial scan look cheaper. You can reduce the cost of a parallel scan for a query with:

BEGIN;
SET LOCAL min\_parallel\_table\_scan\_size \= 1;
SET LOCAL parallel\_setup\_cost \= 1;
SELECT ...
COMMIT;

or choose to store vectors inline:

ALTER TABLE items ALTER COLUMN embedding SET STORAGE PLAIN;

#### Why are there less results for a query after adding an HNSW index?

[](http://github.com/pgvector/pgvector#why-are-there-less-results-for-a-query-after-adding-an-hnsw-index)

Results are limited by the size of the dynamic candidate list (`hnsw.ef_search`), which is 40 by default. There may be even less results due to dead tuples or filtering conditions in the query. Enabling [iterative index scans](http://github.com/pgvector/pgvector#iterative-index-scans) can help address this.

Also, note that `NULL` vectors are not indexed (as well as zero vectors for cosine distance).

#### Why are there less results for a query after adding an IVFFlat index?

[](http://github.com/pgvector/pgvector#why-are-there-less-results-for-a-query-after-adding-an-ivfflat-index)

The index was likely created with too little data for the number of lists. Drop the index until the table has more data.

Results can also be limited by the number of probes (`ivfflat.probes`). Enabling [iterative index scans](http://github.com/pgvector/pgvector#iterative-index-scans) can address this.

Also, note that `NULL` vectors are not indexed (as well as zero vectors for cosine distance).

Reference
---------

[](http://github.com/pgvector/pgvector#reference)

*   [Vector](http://github.com/pgvector/pgvector#vector-type)
*   [Halfvec](http://github.com/pgvector/pgvector#halfvec-type)
*   [Bit](http://github.com/pgvector/pgvector#bit-type)
*   [Sparsevec](http://github.com/pgvector/pgvector#sparsevec-type)

### Vector Type

[](http://github.com/pgvector/pgvector#vector-type)

Each vector takes `4 * dimensions + 8` bytes of storage. Each element is a single-precision floating-point number (like the `real` type in Postgres), and all elements must be finite (no `NaN`, `Infinity` or `-Infinity`). Vectors can have up to 16,000 dimensions.

### Vector Operators

[](http://github.com/pgvector/pgvector#vector-operators)

| Operator | Description | Added |
| --- | --- | --- |
| + | element-wise addition |  |
| \- | element-wise subtraction |  |
| \* | element-wise multiplication | 0.5.0 |
| || | concatenate | 0.7.0 |
| <\-\> | Euclidean distance |  |
| <#\> | negative inner product |  |
| <\=\> | cosine distance |  |
| <+\> | taxicab distance | 0.7.0 |

### Vector Functions

[](http://github.com/pgvector/pgvector#vector-functions)

| Function | Description | Added |
| --- | --- | --- |
| binary\_quantize(vector) → bit | binary quantize | 0.7.0 |
| cosine\_distance(vector, vector) → double precision | cosine distance |  |
| inner\_product(vector, vector) → double precision | inner product |  |
| l1\_distance(vector, vector) → double precision | taxicab distance | 0.5.0 |
| l2\_distance(vector, vector) → double precision | Euclidean distance |  |
| l2\_normalize(vector) → vector | Normalize with Euclidean norm | 0.7.0 |
| subvector(vector, integer, integer) → vector | subvector | 0.7.0 |
| vector\_dims(vector) → integer | number of dimensions |  |
| vector\_norm(vector) → double precision | Euclidean norm |  |

### Vector Aggregate Functions

[](http://github.com/pgvector/pgvector#vector-aggregate-functions)

| Function | Description | Added |
| --- | --- | --- |
| avg(vector) → vector | average |  |
| sum(vector) → vector | sum | 0.5.0 |

### Halfvec Type

[](http://github.com/pgvector/pgvector#halfvec-type)

Each half vector takes `2 * dimensions + 8` bytes of storage. Each element is a half-precision floating-point number, and all elements must be finite (no `NaN`, `Infinity` or `-Infinity`). Half vectors can have up to 16,000 dimensions.

### Halfvec Operators

[](http://github.com/pgvector/pgvector#halfvec-operators)

| Operator | Description | Added |
| --- | --- | --- |
| + | element-wise addition | 0.7.0 |
| \- | element-wise subtraction | 0.7.0 |
| \* | element-wise multiplication | 0.7.0 |
| || | concatenate | 0.7.0 |
| <\-\> | Euclidean distance | 0.7.0 |
| <#\> | negative inner product | 0.7.0 |
| <\=\> | cosine distance | 0.7.0 |
| <+\> | taxicab distance | 0.7.0 |

### Halfvec Functions

[](http://github.com/pgvector/pgvector#halfvec-functions)

| Function | Description | Added |
| --- | --- | --- |
| binary\_quantize(halfvec) → bit | binary quantize | 0.7.0 |
| cosine\_distance(halfvec, halfvec) → double precision | cosine distance | 0.7.0 |
| inner\_product(halfvec, halfvec) → double precision | inner product | 0.7.0 |
| l1\_distance(halfvec, halfvec) → double precision | taxicab distance | 0.7.0 |
| l2\_distance(halfvec, halfvec) → double precision | Euclidean distance | 0.7.0 |
| l2\_norm(halfvec) → double precision | Euclidean norm | 0.7.0 |
| l2\_normalize(halfvec) → halfvec | Normalize with Euclidean norm | 0.7.0 |
| subvector(halfvec, integer, integer) → halfvec | subvector | 0.7.0 |
| vector\_dims(halfvec) → integer | number of dimensions | 0.7.0 |

### Halfvec Aggregate Functions

[](http://github.com/pgvector/pgvector#halfvec-aggregate-functions)

| Function | Description | Added |
| --- | --- | --- |
| avg(halfvec) → halfvec | average | 0.7.0 |
| sum(halfvec) → halfvec | sum | 0.7.0 |

### Bit Type

[](http://github.com/pgvector/pgvector#bit-type)

Each bit vector takes `dimensions / 8 + 8` bytes of storage. See the [Postgres docs](https://www.postgresql.org/docs/current/datatype-bit.html) for more info.

### Bit Operators

[](http://github.com/pgvector/pgvector#bit-operators)

| Operator | Description | Added |
| --- | --- | --- |
| <~\> | Hamming distance | 0.7.0 |
| <%\> | Jaccard distance | 0.7.0 |

### Bit Functions

[](http://github.com/pgvector/pgvector#bit-functions)

| Function | Description | Added |
| --- | --- | --- |
| hamming\_distance(bit, bit) → double precision | Hamming distance | 0.7.0 |
| jaccard\_distance(bit, bit) → double precision | Jaccard distance | 0.7.0 |

### Sparsevec Type

[](http://github.com/pgvector/pgvector#sparsevec-type)

Each sparse vector takes `8 * non-zero elements + 16` bytes of storage. Each element is a single-precision floating-point number, and all elements must be finite (no `NaN`, `Infinity` or `-Infinity`). Sparse vectors can have up to 16,000 non-zero elements.

### Sparsevec Operators

[](http://github.com/pgvector/pgvector#sparsevec-operators)

| Operator | Description | Added |
| --- | --- | --- |
| <\-\> | Euclidean distance | 0.7.0 |
| <#\> | negative inner product | 0.7.0 |
| <\=\> | cosine distance | 0.7.0 |
| <+\> | taxicab distance | 0.7.0 |

### Sparsevec Functions

[](http://github.com/pgvector/pgvector#sparsevec-functions)

| Function | Description | Added |
| --- | --- | --- |
| cosine\_distance(sparsevec, sparsevec) → double precision | cosine distance | 0.7.0 |
| inner\_product(sparsevec, sparsevec) → double precision | inner product | 0.7.0 |
| l1\_distance(sparsevec, sparsevec) → double precision | taxicab distance | 0.7.0 |
| l2\_distance(sparsevec, sparsevec) → double precision | Euclidean distance | 0.7.0 |
| l2\_norm(sparsevec) → double precision | Euclidean norm | 0.7.0 |
| l2\_normalize(sparsevec) → sparsevec | Normalize with Euclidean norm | 0.7.0 |

Installation Notes - Linux and Mac
----------------------------------

[](http://github.com/pgvector/pgvector#installation-notes---linux-and-mac)

### Postgres Location

[](http://github.com/pgvector/pgvector#postgres-location)

If your machine has multiple Postgres installations, specify the path to [pg\_config](https://www.postgresql.org/docs/current/app-pgconfig.html) with:

export PG\_CONFIG=/Library/PostgreSQL/17/bin/pg\_config

Then re-run the installation instructions (run `make clean` before `make` if needed). If `sudo` is needed for `make install`, use:

sudo --preserve-env=PG\_CONFIG make install

A few common paths on Mac are:

*   EDB installer - `/Library/PostgreSQL/17/bin/pg_config`
*   Homebrew (arm64) - `/opt/homebrew/opt/postgresql@17/bin/pg_config`
*   Homebrew (x86-64) - `/usr/local/opt/postgresql@17/bin/pg_config`

Note: Replace `17` with your Postgres server version

### Missing Header

[](http://github.com/pgvector/pgvector#missing-header)

If compilation fails with `fatal error: postgres.h: No such file or directory`, make sure Postgres development files are installed on the server.

For Ubuntu and Debian, use:

sudo apt install postgresql-server-dev-17

Note: Replace `17` with your Postgres server version

### Missing SDK

[](http://github.com/pgvector/pgvector#missing-sdk)

If compilation fails and the output includes `warning: no such sysroot directory` on Mac, reinstall Xcode Command Line Tools.

### Portability

[](http://github.com/pgvector/pgvector#portability)

By default, pgvector compiles with `-march=native` on some platforms for best performance. However, this can lead to `Illegal instruction` errors if trying to run the compiled extension on a different machine.

To compile for portability, use:

Installation Notes - Windows
----------------------------

[](http://github.com/pgvector/pgvector#installation-notes---windows)

### Missing Header

[](http://github.com/pgvector/pgvector#missing-header-1)

If compilation fails with `Cannot open include file: 'postgres.h': No such file or directory`, make sure `PGROOT` is correct.

### Permissions

[](http://github.com/pgvector/pgvector#permissions)

If installation fails with `Access is denied`, re-run the installation instructions as an administrator.

Additional Installation Methods
-------------------------------

[](http://github.com/pgvector/pgvector#additional-installation-methods)

### Docker

[](http://github.com/pgvector/pgvector#docker)

Get the [Docker image](https://hub.docker.com/r/pgvector/pgvector) with:

docker pull pgvector/pgvector:pg17

This adds pgvector to the [Postgres image](https://hub.docker.com/_/postgres) (replace `17` with your Postgres server version, and run it the same way).

You can also build the image manually:

git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
docker build --pull --build-arg PG\_MAJOR=17 -t myuser/pgvector .

### Homebrew

[](http://github.com/pgvector/pgvector#homebrew)

With Homebrew Postgres, you can use:

Note: This only adds it to the `postgresql@17` and `postgresql@14` formulas

### PGXN

[](http://github.com/pgvector/pgvector#pgxn)

Install from the [PostgreSQL Extension Network](https://pgxn.org/dist/vector) with:

### APT

[](http://github.com/pgvector/pgvector#apt)

Debian and Ubuntu packages are available from the [PostgreSQL APT Repository](https://wiki.postgresql.org/wiki/Apt). Follow the [setup instructions](https://wiki.postgresql.org/wiki/Apt#Quickstart) and run:

sudo apt install postgresql-17-pgvector

Note: Replace `17` with your Postgres server version

### Yum

[](http://github.com/pgvector/pgvector#yum)

RPM packages are available from the [PostgreSQL Yum Repository](https://yum.postgresql.org/). Follow the [setup instructions](https://www.postgresql.org/download/linux/redhat/) for your distribution and run:

sudo yum install pgvector\_17
# or
sudo dnf install pgvector\_17

Note: Replace `17` with your Postgres server version

### pkg

[](http://github.com/pgvector/pgvector#pkg)

Install the FreeBSD package with:

pkg install postgresql16-pgvector

or the port with:

cd /usr/ports/databases/pgvector
make install

### conda-forge

[](http://github.com/pgvector/pgvector#conda-forge)

With Conda Postgres, install from [conda-forge](https://anaconda.org/conda-forge/pgvector) with:

conda install -c conda-forge pgvector

This method is [community-maintained](https://github.com/conda-forge/pgvector-feedstock) by [@mmcauliffe](https://github.com/mmcauliffe)

### Postgres.app

[](http://github.com/pgvector/pgvector#postgresapp)

Download the [latest release](https://postgresapp.com/downloads.html) with Postgres 15+.

Hosted Postgres
---------------

[](http://github.com/pgvector/pgvector#hosted-postgres)

pgvector is available on [these providers](https://github.com/pgvector/pgvector/issues/54).

Upgrading
---------

[](http://github.com/pgvector/pgvector#upgrading)

[Install](http://github.com/pgvector/pgvector#installation) the latest version (use the same method as the original installation). Then in each database you want to upgrade, run:

ALTER EXTENSION vector UPDATE;

You can check the version in the current database with:

SELECT extversion FROM pg\_extension WHERE extname \= 'vector';

Upgrade Notes
-------------

[](http://github.com/pgvector/pgvector#upgrade-notes)

### 0.6.0

[](http://github.com/pgvector/pgvector#060)

#### Postgres 12

[](http://github.com/pgvector/pgvector#postgres-12)

If upgrading with Postgres 12, remove this line from `sql/vector--0.5.1--0.6.0.sql`:

ALTER TYPE vector SET (STORAGE \= external);

Then run `make install` and `ALTER EXTENSION vector UPDATE;`.

#### Docker

[](http://github.com/pgvector/pgvector#docker-1)

The Docker image is now published in the `pgvector` org, and there are tags for each supported version of Postgres (rather than a `latest` tag).

docker pull pgvector/pgvector:pg16
# or
docker pull pgvector/pgvector:0.6.0-pg16

Also, if you’ve increased `maintenance_work_mem`, make sure `--shm-size` is at least that size to avoid an error with parallel HNSW index builds.

docker run --shm-size=1g ...

Thanks
------

[](http://github.com/pgvector/pgvector#thanks)

Thanks to:

*   [PASE: PostgreSQL Ultra-High-Dimensional Approximate Nearest Neighbor Search Extension](https://dl.acm.org/doi/pdf/10.1145/3318464.3386131)
*   [Faiss: A Library for Efficient Similarity Search and Clustering of Dense Vectors](https://github.com/facebookresearch/faiss)
*   [Using the Triangle Inequality to Accelerate k-means](https://cdn.aaai.org/ICML/2003/ICML03-022.pdf)
*   [k-means++: The Advantage of Careful Seeding](https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf)
*   [Concept Decompositions for Large Sparse Text Data using Clustering](https://www.cs.utexas.edu/users/inderjit/public_papers/concept_mlj.pdf)
*   [Efficient and Robust Approximate Nearest Neighbor Search using Hierarchical Navigable Small World Graphs](https://arxiv.org/ftp/arxiv/papers/1603/1603.09320.pdf)

History
-------

[](http://github.com/pgvector/pgvector#history)

View the [changelog](https://github.com/pgvector/pgvector/blob/master/CHANGELOG.md)

Contributing
------------

[](http://github.com/pgvector/pgvector#contributing)

Everyone is encouraged to help improve this project. Here are a few ways you can help:

*   [Report bugs](https://github.com/pgvector/pgvector/issues)
*   Fix bugs and [submit pull requests](https://github.com/pgvector/pgvector/pulls)
*   Write, clarify, or fix documentation
*   Suggest or add new features

To get started with development:

git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

To run all tests:

make installcheck        # regression tests
make prove\_installcheck  # TAP tests

To run single tests:

make installcheck REGRESS=functions                            # regression test
make prove\_installcheck PROVE\_TESTS=test/t/001\_ivfflat\_wal.pl  # TAP test

To enable assertions:

make clean && PG\_CFLAGS="\-DUSE\_ASSERT\_CHECKING" make && make install

To enable benchmarking:

make clean && PG\_CFLAGS="\-DIVFFLAT\_BENCH" make && make install

To show memory usage:

make clean && PG\_CFLAGS="\-DHNSW\_MEMORY -DIVFFLAT\_MEMORY" make && make install

To get k-means metrics:

make clean && PG\_CFLAGS="\-DIVFFLAT\_KMEANS\_DEBUG" make && make install

Resources for contributors

*   [Extension Building Infrastructure](https://www.postgresql.org/docs/current/extend-pgxs.html)
*   [Index Access Method Interface Definition](https://www.postgresql.org/docs/current/indexam.html)
*   [Generic WAL Records](https://www.postgresql.org/docs/current/generic-wal.html)