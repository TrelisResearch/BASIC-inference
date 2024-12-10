# Minimal Vector Search Demo with Postgres

A minimal demo showing how to use Postgres for vector search using pgvector (dense) and pg_bestmatch (sparse/BM25).

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
# Optional: Drop existing database if starting fresh
dropdb vector_demo || true
dropuser vector_user || true

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
-- The bm_catalog schema is created automatically when you install the pg_bestmatch extension using CREATE EXTENSION pg_bestmatch.
SET search_path TO public, bm_catalog;

-- Recreate and refresh BM25 statistics
DROP TABLE IF EXISTS documents_content_bm25;
SELECT bm25_create('documents', 'content', 'documents_content_bm25');
SELECT bm25_refresh('documents_content_bm25');

-- Recreate sparse vector column
ALTER TABLE documents DROP COLUMN IF EXISTS sparse_vector;
ALTER TABLE documents ADD COLUMN sparse_vector sparsevec;
UPDATE documents 
SET sparse_vector = bm25_document_to_svector('documents_content_bm25', content, 'pgvector')::sparsevec;

-- Verify sparse vectors were created properly
SELECT content, sparse_vector IS NOT NULL as has_vector 
FROM documents;

-- Test BM25 search query
WITH query_vector AS (
    SELECT bm25_query_to_svector(
        'documents_content_bm25',
        'Paris capital',  -- Using a test query we know should match
        'pgvector'
    )::sparsevec AS qv
)
SELECT 
    content,
    (sparse_vector <#> (SELECT qv FROM query_vector)) * -1 as bm25_score
FROM documents
WHERE sparse_vector IS NOT NULL  -- Ensure we only search valid vectors
ORDER BY sparse_vector <#> (SELECT qv FROM query_vector)
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
