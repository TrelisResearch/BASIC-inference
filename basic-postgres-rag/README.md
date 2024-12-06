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

First, let's generate our embeddings:

```bash
# Install requirements
uv pip install -r requirements.txt

# Generate embeddings
uv run python generate_demo_embeddings.py > embeddings.sql
```

Now connect to the database:
```bash
psql vector_demo
```

### 1. Create Tables

```sql
-- Set search path to include bm_catalog
SET search_path TO public, bm_catalog;

-- Drop BM25 statistics if they exist
SELECT bm25_drop('documents_content_bm25');

-- Drop existing table if it exists
DROP TABLE IF EXISTS documents;

-- Create table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768)  -- Dense vector for similarity search
);

-- Insert sample texts first
INSERT INTO documents (content) VALUES 
    ('The capital of France is Paris'),
    ('Paris is known for the Eiffel Tower'),
    ('The capital of Japan is Tokyo'),
    ('Tokyo is famous for sushi');

-- Create BM25 statistics (must be done after data is inserted)
SELECT bm25_create('documents', 'content', 'documents_content_bm25');

-- Add dense vectors
\i embeddings.sql

-- Now refresh BM25 statistics
SELECT bm25_refresh('documents_content_bm25');
```

### 2. Run Searches

#### Dense Vector Search
```sql
-- Search for content about Paris
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
LIMIT 3;
```

Example output:
```
               content               |     similarity     
-------------------------------------+--------------------
 The capital of France is Paris      |                  1
 Paris is known for the Eiffel Tower | 0.7303327241274449
 The capital of Japan is Tokyo       | 0.7289948838545682
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
       bm25_document_to_svector('documents_content_bm25', content, 'pgvector')::sparsevec <=> 
           (SELECT qv FROM query_vector) as score
FROM documents
ORDER BY score ASC  -- Lower score means more similar
LIMIT 3;
```

Example output:
```
               content               |       score       
-------------------------------------+-------------------
 The capital of France is Paris      | 0.591751698707732
 The capital of Japan is Tokyo       | 0.591751698707732
 Paris is known for the Eiffel Tower |                 1
```

## Notes

1. The embeddings are generated using the nomic-embed-text-v1.5 model (768 dimensions)
2. The dense vector search uses cosine similarity (1 - distance)
3. The sparse vector search uses BM25 scoring

