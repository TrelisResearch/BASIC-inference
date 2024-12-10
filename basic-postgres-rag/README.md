# Minimal Vector Search Demo with Postgres

A minimal demo showing how to use Postgres for vector search using pgvector (dense) and pg_bestmatch (sparse/BM25).

>[!WARNING]
>This isn't very robust because you have to try to sort for the 2,000 most important terms.
>Currently, there's not enough data to set an index using ivfflat.

## Advanced Version

For additional features beneficial for production/enterprise applications, see Trelis' [Advanced Inference Repo](https://trelis.com/ADVANCED-inference).

<details>
<summary>Advanced Features Overview</summary>

- Faster BM25 implementation (custom implementation allowing for indexing).
- Stemming and stop-word handling - for improved search performance.
- Text Extraction and Chunking (PDF, DOCX, TXT, MD), using binary search for efficiency.
- Asynchronous database calls - allowing higher production throughput.
- Speed/Performance Evaluation.
- Command line search interface.
</details>

## Installation

### MacOS
```bash
# Install PostgreSQL and build tools
brew install postgresql
brew services start postgresql

# Install Rust (needed for extensions)
brew install rust
```

### Ubuntu/Debian
```bash
# Install PostgreSQL and build dependencies
sudo apt update
sudo apt install -y postgresql postgresql-contrib postgresql-server-dev-all build-essential

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
```

### Install PostgreSQL Extensions

1. Install pgvector (for dense search)
```bash
cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

2. Install pg_bestmatch (for sparse/BM25 search)
```bash
# Install cargo-pgrx
cargo install cargo-pgrx --version 0.12.0-alpha.1
cargo pgrx init

# Install pg_bestmatch
cd /tmp
git clone https://github.com/tensorchord/pg_bestmatch.rs.git
cd pg_bestmatch.rs
cargo pgrx install --release
```

### Set Up Database

```bash
# Optional: Drop existing database and user if starting fresh
psql postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'vector_demo';"
psql postgres -c "DROP DATABASE IF EXISTS vector_demo;"
psql postgres -c "DROP OWNED BY vector_user;" || true
psql postgres -c "DROP USER IF EXISTS vector_user;"

# Create database and user
createdb vector_demo
createuser -s vector_user
psql -d vector_demo -c "ALTER USER vector_user WITH PASSWORD 'demo_password';"

# Enable extensions
psql -d vector_demo -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d vector_demo -c "CREATE EXTENSION IF NOT EXISTS pg_bestmatch;"
psql -d vector_demo -c "SET search_path TO public, bm_catalog;"
```

## Demo Setup

1. Set up Python environment and install dependencies:
```bash
cd basic-postgres-rag
uv venv
source .venv/bin/activate

uv pip install huggingface-hub numpy pgvector psycopg2-binary sentence-transformers hf_transfer einops
```

2. Generate document embeddings:
```bash
uv run generate_doc_embeddings.py
```

## Dense Vector Search

1. Create HNSW index for efficient cosine similarity search:
```bash
psql -d vector_demo -c "CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);"
```

2. Run a search query:
```bash
uv run query_embeddings.py
```

## Sparse Vector (BM25) Search

1. Set up BM25 in PostgreSQL:

```bash
psql -d vector_demo
```

```sql
-- First ensure BM25 is properly set up
SET search_path TO public, bm_catalog;

-- Create a table to store global term statistics
CREATE TABLE IF NOT EXISTS term_stats (
    term_id INTEGER PRIMARY KEY,
    global_importance FLOAT4,
    rank INTEGER
);

-- Populate global term statistics
INSERT INTO term_stats (term_id, global_importance)
SELECT 
    (v).element as term_id,
    sum(abs((v).value)) as global_importance
FROM documents d,
     unnest(bm25_document_to_svector('documents_content_bm25', content, 'pgvector')) v
GROUP BY (v).element
ON CONFLICT (term_id) DO UPDATE
SET global_importance = EXCLUDED.global_importance;

-- Update term rankings
WITH ranked_terms AS (
    SELECT 
        term_id,
        global_importance,
        row_number() OVER (ORDER BY global_importance DESC) as rank
    FROM term_stats
)
UPDATE term_stats ts
SET rank = rt.rank
FROM ranked_terms rt
WHERE ts.term_id = rt.term_id;

-- Store BM25 vectors using top global terms
ALTER TABLE documents DROP COLUMN IF EXISTS sparse_vector;
ALTER TABLE documents ADD COLUMN sparse_vector vector(2000);

-- Create a function to map sparse vectors to top global terms
CREATE OR REPLACE FUNCTION map_to_top_terms(sparse_vector sparsevec)
RETURNS vector(2000) AS $$
DECLARE
    result float4[];
BEGIN
    result := array_fill(0::float4, ARRAY[2000]);
    
    -- Map values to their global rank positions (only top 2000)
    FOR i IN 1..array_length((sparse_vector).index, 1) LOOP
        SELECT rank INTO i
        FROM term_stats 
        WHERE term_id = (sparse_vector).index[i]
        AND rank <= 2000;
        
        IF FOUND THEN
            result[i] := (sparse_vector).value[i];
        END IF;
    END LOOP;
    
    RETURN result::vector;
END;
$$ LANGUAGE plpgsql;

-- Update document vectors
UPDATE documents 
SET sparse_vector = map_to_top_terms(
    bm25_document_to_svector('documents_content_bm25', content, 'pgvector')
);

-- Create IVFFlat index on sparse vectors
CREATE INDEX ON documents USING ivfflat (sparse_vector vector_l2_ops) WITH (lists = 100);

-- Function to map query vectors
CREATE OR REPLACE FUNCTION map_query_to_top_terms(query_text TEXT)
RETURNS vector AS $$
BEGIN
    RETURN map_to_top_terms(
        bm25_query_to_svector('documents_content_bm25', query_text, 'pgvector')
    );
END;
$$ LANGUAGE plpgsql;

-- Test BM25 search query
SELECT 
    content,
    (sparse_vector <#> map_query_to_top_terms('Paris capital')) * -1 as bm25_score
FROM documents
WHERE sparse_vector IS NOT NULL
ORDER BY sparse_vector <#> map_query_to_top_terms('Paris capital')
LIMIT 4;
```

Example output:
```
               content               |     bm25_score      
-------------------------------------+---------------------
 The capital of France is Paris      |  0.4761905074119568
 The capital of Japan is Tokyo       |  0.2380952537059784
 Paris is known for the Eiffel Tower | 0.20000000298023224
 Tokyo is famous for sushi           |                   0
```

## Technical Notes

- **Embeddings**: Using nomic-embed-text-v1.5 model (768 dimensions)
  - Documents use "search_document: " prefix
  - Queries use "search_query: " prefix

- **Dense Search**:
  - HNSW index with `vector_cosine_ops`
  - `<=>` operator returns the cosine distance
  - Similarity = 1 - distance

- **Sparse Search**:
  - No index used (highly sparse vectors)
  - `<#>` operator returns the inner product, which is the correct way to sum up the bm25 components.
  - Lower distance indicates higher BM25 relevance
  - Negative distances are normal (higher magnitude means better match)

- **Sparse Search**:
  - No index is used because i) indexing with hnsw works poorly for sparse vectors, and ii) ivfflat is not supported.
  - The solutions, in principle are:
    - Use a custom implementation of BM25 that allows for indexing (done in the advanced repo).
    - Use a dense vector model for the embeddings. This will be slower and require more memory to store the embeddings.
    - Use pgvecto.rs, a rust implementation that should support indexing with ivfflat.

- **Notes on the pg_bestmatch extension**:
  - Under the hood, the text is tokenized using bert uncased.
    - Capitalization is not preserved (which is good)
    - There will be some stemming, but it will follow BERT's syntax.
    - There will be no stop-word removal.

- **IVFFlat Index Details**:
  - The `lists` parameter (default 100) determines the number of clusters/partitions
  - Higher values mean:
    - Faster search (searches fewer vectors)
    - Less accurate results
    - Slower index creation
    - More memory usage
  - Rule of thumb: `lists = sqrt(num_rows)` for balanced performance
  - For small datasets (<10k rows), smaller values (50-100) work well
  - For large datasets, consider: `lists = num_rows / 1000`

- **Sparse Search Updates**:
  - Now using pgvector's vector type with 2000 dimensions (pgvector's limit)
  - Maintaining global term statistics across all documents
  - Terms are mapped to fixed positions based on global importance
  - Main tradeoffs:
    1. Memory usage: Each vector stores 16,000 dimensions
    2. Information loss from dropping less globally significant terms
    3. Some precision loss from float32 representation
    4. Needs periodic updates to global term statistics
  - Benefits:
    1. Consistent term-to-dimension mapping across all documents
    2. Global term importance is considered
    3. Can use standard indexing methods
    4. Potentially faster queries with large datasets due to indexing

- **Global Term Statistics**:
  - Terms are ranked by their total importance across all documents
  - Top 2000 most important terms get fixed positions
  - New documents use the same term-to-position mapping
  - Should be periodically updated when corpus changes significantly
