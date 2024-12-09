# Minimal Vector Search Demo with Postgres

A minimal demo showing how to use Postgres for vector search using pgvector (dense) and pg_bestmatch (sparse/BM25).

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

1. Create HNSW index for efficient similarity search:
```bash
psql -d vector_demo -c CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
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
-- First set the search path to include bm_catalog
SET search_path TO public, bm_catalog;

-- Create and refresh BM25 statistics
SELECT bm25_create('documents', 'content', 'documents_content_bm25');
SELECT bm25_refresh('documents_content_bm25');

-- Add sparse vector column and precompute vectors
ALTER TABLE documents ADD COLUMN sparse_vector sparsevec;
UPDATE documents 
SET sparse_vector = bm25_document_to_svector('documents_content_bm25', content, 'pgvector')::sparsevec;

-- Note: We don't create an index for sparse vectors
-- HNSW and IVFFlat don't work well with highly sparse BM25 vectors
```

2. Run a BM25 search query:
```sql
WITH query_vector AS (
    SELECT bm25_query_to_svector(
        'documents_content_bm25',
        'capital city',
        'pgvector'
    )::sparsevec AS qv
)
SELECT content,
       sparse_vector <#> (SELECT qv FROM query_vector) as distance
FROM documents
ORDER BY sparse_vector <#> (SELECT qv FROM query_vector)
LIMIT 4;
```

Example output:
```
               content               |     similarity      
-------------------------------------+---------------------
 The capital of France is Paris      | 0.40824830129226797
 The capital of Japan is Tokyo       | 0.40824830129226797
 Paris is known for the Eiffel Tower |                   0
 Tokyo is famous for sushi           |                   0
```

## Technical Notes

- **Embeddings**: Using nomic-embed-text-v1.5 model (768 dimensions)
  - Documents use "search_document: " prefix
  - Queries use "search_query: " prefix

- **Dense Search**:
  - HNSW index with `vector_cosine_ops`
  - `<#>` operator returns cosine distance
  - Similarity = 1 - distance

- **Sparse Search**:
  - No index used (highly sparse vectors)
  - `<#>` operator returns inner product distance
  - Lower distance indicates higher BM25 relevance
  - Negative distances are normal (higher magnitude means better match)

## Advanced Version

For additional features including PDF processing, optimizations, and development tools, see our [Advanced Version](https://trelis.com/ADVANCED-inference).

<details>
<summary>Advanced Features Overview</summary>

- Document Processing (PDF, DOCX, TXT, MD)
- Enhanced Vector Search Capabilities
- Database Optimizations
- Development Tools
- Performance Features
- Command Line Interface
</details>

