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
brew install postgresql@14

# Initialize PostgreSQL data directory (if not already done)
initdb /opt/homebrew/var/postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Add PostgreSQL 14 to your PATH
echo 'export PATH="/opt/homebrew/opt/postgresql@14/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Wait for PostgreSQL to start
sleep 5

# Verify PostgreSQL is running
pg_isready -h localhost

# If pg_isready shows PostgreSQL isn't running, try:
brew services restart postgresql@14
sleep 5
pg_isready -h localhost

# If still having issues, check the logs:
tail -f /opt/homebrew/var/log/postgresql@14.log
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

#### Install pgvecto.rs (for sparse vector indexing)
```bash
cd /tmp
# Remove existing directory if it exists
rm -rf pgvecto.rs
git clone https://github.com/tensorchord/pgvecto.rs.git
cd pgvecto.rs

# Install with your PostgreSQL version (replace XX with your version, e.g. 14)
cargo install --path . --features pg14

# Build and install the extension
cargo pgrx init --pg14=$(which pg_config)
cargo pgrx install --release

# Configure PostgreSQL to preload the extension
psql -c "ALTER SYSTEM SET shared_preload_libraries = 'vectors.so';"

# Restart PostgreSQL to apply the change
# On MacOS:
brew services restart postgresql
# On Linux:
sudo systemctl restart postgresql
```

#### Install pg_bestmatch (for BM25 calculations)
```bash
# Install cargo-pgrx
cargo install cargo-pgrx --version 0.12.0-alpha.1

# Check your PostgreSQL version
psql --version

# Find your pg_config path
which pg_config
# This will output something like /usr/local/bin/pg_config

# Initialize pgrx with your PostgreSQL version
cargo pgrx init --pg14=$(which pg_config)

# Install pg_bestmatch
cd /tmp
# # Remove existing directory if it exists
# rm -rf pg_bestmatch.rs
git clone https://github.com/tensorchord/pg_bestmatch.rs.git
cd pg_bestmatch.rs
cargo pgrx install --release
# Note: You can safely ignore any warnings about "unexpected cfg condition name: pgrx_embed"
```

### Create Database and Enable Extensions

```bash
# Check PostgreSQL is running
pg_isready

# If not running, start PostgreSQL
brew services restart postgresql@14
sleep 5  # Wait for PostgreSQL to start

# Optional: Drop existing database (useful for starting fresh)
dropdb vector_demo || true  # The || true prevents errors if database doesn't exist
dropuser vector_user || true

# Create database and user
createdb vector_demo
createuser -s vector_user
psql -d vector_demo -c "ALTER USER vector_user WITH PASSWORD 'demo_password';"

# Enable extensions (in correct order)
psql -d vector_demo -c "CREATE EXTENSION IF NOT EXISTS vector;"
psql -d vector_demo -c "CREATE EXTENSION IF NOT EXISTS pg_bestmatch;"
psql -d vector_demo -c "CREATE EXTENSION IF NOT EXISTS vectors;"
psql -d vector_demo -c "SET search_path TO public, bm_catalog;"
```

Note: The extensions are enabled in this order:
1. `vector` - from pgvector, for dense vectors
2. `pg_bestmatch` - for BM25 calculations
3. `vectors` - from pgvecto.rs, for sparse vectors

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

First, open the postgres terminal:
```bash
psql -d vector_demo -U vector_user
```

Then set up BM25 statistics and precompute sparse vectors:
```sql
-- Set search path to include bm_catalog
SET search_path TO public, bm_catalog;

-- Create and refresh BM25 statistics
SELECT bm25_create('documents', 'content', 'documents_content_bm25');
SELECT bm25_refresh('documents_content_bm25');

-- Add column for sparse vectors
ALTER TABLE documents ADD COLUMN sparse_vector svector;

-- Precompute sparse vectors for all documents
UPDATE documents 
SET sparse_vector = bm25_document_to_svector('documents_content_bm25', content, 'pgvector')::svector;

-- Create efficient index for sparse vectors using pgvecto.rs
CREATE INDEX ON documents USING vectors (sparse_vector svector_dot_ops);
```

### 3. Create Dense Vector Index
```sql
-- Create HNSW index for dense vectors using pgvector
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
```

### 4. Run Searches

#### Dense Vector Search (using HNSW index)
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
    1 - (d.embedding <#> q.embedding) as similarity  -- <#> operator uses HNSW index
FROM documents d, query q
ORDER BY d.embedding <#> q.embedding  -- ORDER BY with LIMIT leverages index for top-k
LIMIT 4;
```

#### Sparse Vector (BM25) Search (using precomputed vectors)
```sql
-- Convert query to sparse vector and search using index
WITH query_vector AS (
    SELECT bm25_query_to_svector(
        'documents_content_bm25',
        'capital city',
        'pgvector'
    )::svector AS qv  -- svector type for pgvecto.rs
)
SELECT content,
       1 - (sparse_vector <#> (SELECT qv FROM query_vector)) as similarity
FROM documents
ORDER BY sparse_vector <#> (SELECT qv FROM query_vector)
LIMIT 4;  -- Will efficiently find top-4 using the vector index, without calculating all similarities
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
2. The dense vector search uses:
   - HNSW indexing with `vector_cosine_ops` for semantic similarity
   - `<#>` operator uses the cosine distance because of the `vector_cosine_ops` index
   - We convert to similarity with `1 - distance`
3. The sparse vector search uses:
   - Index with `svector_dot_ops` for BM25 sparse vectors
   - Same `<#>` operator but uses dot product because of the `svector_dot_ops` index
   - We convert to similarity with `1 - distance`
4. The `<#>` operator:
   - Behavior determined by the index operator class
   - Returns distance (smaller = more similar)
   - Always needs to be converted to similarity with `1 - distance`

