# pgvector Similarity Search Demo

A minimal demo to understand different similarity metrics in pgvector.

## Setup

1. Install PostgreSQL and pgvector:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib postgresql-server-dev-all
cd /tmp
git clone --branch v0.8.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

2. Create and configure database:

```bash
# Create database
createdb pgvector_demo
psql pgvector_demo

# In psql:
CREATE EXTENSION vector;
```

3. Create test table with vectors:

```sql
-- Create table with 3D vectors
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name TEXT,
    embedding vector(3)
);

-- Insert some test vectors
INSERT INTO items (name, embedding) VALUES 
    ('point_a', '[1,2,3]'),
    ('point_b', '[4,5,6]'),
    ('point_c', '[1,1,1]'),
    ('point_d', '[2,2,2]'),
    ('point_zero', '[0,0,0]');
```

## Try Different Similarity Metrics

1. Euclidean Distance (`<->`)
```sql
-- Find nearest neighbors using L2 distance
SELECT name, embedding <-> '[2,2,2]' as distance 
FROM items 
ORDER BY distance 
LIMIT 3;
```

2. Cosine Distance (`<=>`)
```sql
-- Find nearest neighbors using cosine distance
SELECT name, embedding <=> '[2,2,2]' as cosine_distance,
       1 - (embedding <=> '[2,2,2]') as cosine_similarity
FROM items 
ORDER BY cosine_distance 
LIMIT 3;
```

3. Inner Product (`<#>`)
```sql
-- Find nearest neighbors using inner product
-- Note: Returns negative inner product, multiply by -1 for actual value
SELECT name, 
       embedding <#> '[2,2,2]' as neg_inner_product,
       (embedding <#> '[2,2,2]') * -1 as inner_product
FROM items 
ORDER BY neg_inner_product 
LIMIT 3;
```

4. Manhattan/L1 Distance (`<+>`)
```sql
-- Find nearest neighbors using L1 distance
SELECT name, embedding <+> '[2,2,2]' as manhattan_distance 
FROM items 
ORDER BY manhattan_distance 
LIMIT 3;
```

## Add Index for Better Performance

```sql
-- Create HNSW index for cosine similarity
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

-- For Euclidean distance use vector_l2_ops instead
-- CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
```

## Understanding the Results

- Euclidean (`<->`) measures straight-line distance between points
- Cosine (`<=>`) measures angle between vectors (normalized by length)
- Inner Product (`<#>`) measures directional similarity
- Manhattan (`<+>`) measures distance along axes

Try changing the query vector `[2,2,2]` to different values to see how each metric behaves differently!