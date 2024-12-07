# Minimal Vector Search Demo with Postgres

A minimal demo showing how to use Postgres for vector search using pgvector (dense) and pg_bestmatch (sparse/BM25).

## ADVANCED Version Features

> [!TIP]
> Purchase life-time access to the advanced version at: https://trelis.com/ADVANCED-inference

<details>

- **Document Processing**
  - Handles PDF, DOCX, TXT, and MD files automatically
  - Preserves metadata (page numbers, line numbers, sections)
  - Smart text chunking by page, paragraphs, lines and/or characters
  - Two-stage text normalization (cleaning + lemmatization)

- **Vector Search Capabilities**
  - Dense vector search using HNSW indexing for semantic similarity
  - Sparse vector search using BM25 for keyword matching
  - Configurable top-k retrieval

- **Database Optimizations**
  - Asynchronous database operations with connection pooling
  - Efficient vector indexing using pgvector
  - BM25 statistics tracking for improved text search
  - Batch processing support for document uploads

- **Development Features**
  - Complete test suite for embeddings, chunking, and search
  - Database migration management with Alembic
  - Verification scripts for setup and configuration
  - Command-line tools for testing and maintenance

- **Performance Features**
  - Pre-initialized NLTK models to reduce latency
  - Optimized chunk size for LLM context windows
  - Direct SQL queries for vector operations

- **Command Line Search Interface**
  - Conduct dense or sparse searches from the command line
</details>

## Basic Scripts (FREE)

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

### Install Extensions

#### Install pgvector (for dense search)
```bash
cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

#### Install pg_bestmatch (for sparse/BM25 search)
```bash
# Install cargo-pgrx
cargo install cargo-pgrx --version 0.12.0-alpha.1

# Initialize pgrx
cargo pgrx init

# Install pg_bestmatch
cd /tmp
git clone https://github.com/tensorchord/pg_bestmatch.rs.git
cd pg_bestmatch.rs
cargo pgrx install --release
```

### Create Database and Enable Extensions

```bash
# Optional: Drop existing database (useful for starting fresh)
dropdb vector_demo
dropuser vector_user

# Create database and user
createdb vector_demo
createuser -s vector_user
psql -d vector_demo -c "ALTER USER vector_user WITH PASSWORD 'demo_password';"

# Enable extensions
psql -d vector_demo -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d vector_demo -c "CREATE EXTENSION IF NOT EXISTS pg_bestmatch;"
psql -d vector_demo -c "SET search_path TO public, bm_catalog;"
```

## Demo

### 1. Set Up Database and Add Data

```bash
# Make sure your virtual environment is activated
cd basic-postgres-rag
uv venv
uv pip install -r requirements.txt

# Run the script to create table and add data with embeddings
uv run python generate_demo_embeddings.py
```

### 2. Set Up BM25 Search

Open the postgres terminal:
bash
psql -d vector_demo -U vector_user
```

Then run:
```sql
-- Set search path to include bm_catalog
SET search_path TO public, bm_catalog;

-- Create and refresh BM25 statistics
SELECT bm25_create('documents', 'content', 'documents_content_bm25');
SELECT bm25_refresh('documents_content_bm25');
```

### 3. Run Searches
```
#### Dense Vector Search
```sql
-- Grab one row of data to search against
WITH query AS (
    SELECT embedding 
    FROM documents 
    WHERE content LIKE '%Paris%' 
    LIMIT 1
)
SELECT 
    d.content,
    1 - (d.embedding <=> q.embedding) as similarity
FROM documents d, query q
ORDER BY d.embedding <=> q.embedding
LIMIT 4;
```

Example output:
```
               content               |     similarity     
-------------------------------------+--------------------
 The capital of France is Paris      |                  1
 The capital of Japan is Tokyo       | 0.8014076652679855
 Paris is known for the Eiffel Tower | 0.7418301003706876
 Tokyo is famous for sushi           |  0.577042391843145
```

#### Sparse Vector (BM25) Search
```sql
-- Convert query to sparse vector and search
WITH query_vector AS (
    SELECT bm25_query_to_svector(
        'documents_content_bm25',
        'capital city',
        'pgvector'
    )::sparsevec AS qv
)
SELECT content,
       1 - (bm25_document_to_svector('documents_content_bm25', content, 'pgvector')::sparsevec <=> 
           (SELECT qv FROM query_vector)) as similarity
FROM documents
ORDER BY similarity DESC  -- Higher score means more similar
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

## Notes

1. The embeddings are generated using the nomic-embed-text-v1.5 model (768 dimensions)
2. The dense vector search uses cosine similarity (1 - distance)
3. The sparse vector search uses BM25 scoring along with cosine similarity

