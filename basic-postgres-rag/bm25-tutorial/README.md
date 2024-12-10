# BM25 Tutorial in Postgres

This tutorial shows two approaches to implementing BM25 (Best Match 25) ranking in Postgres:

1. Pure Postgres Implementation
2. Sparse Vector Implementation using pgvector (this is not currently supported, and would require pgvecto.rs - rust based - to work)

## Understanding BM25

The BM25 formula is:

```
score(D,Q) = ∑ IDF(qi) * (f(qi,D) * (k1 + 1)) / (f(qi,D) + k1 * (1 - b + b * |D|/avgdl))
```

Where:
- D is the document
- Q is the query
- f(qi,D) is term frequency of term qi in document D
- |D| is document length
- avgdl is average document length
- k1 and b are free parameters (typically k1=1.2, b=0.75)
- IDF(qi) = log((N - n(qi) + 0.5)/(n(qi) + 0.5))
  - N is total number of documents
  - n(qi) is number of documents containing term qi

## Part 1: Pure Postgres Implementation

Setup a database and connect to it:

```bash
createdb bm25_demo
psql -d bm25_demo;
```

First, let's create our tables and functions:

```sql
-- Create documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL
);

-- Create terms table to store term statistics
CREATE TABLE term_stats (
    term TEXT PRIMARY KEY,
    doc_count INTEGER NOT NULL, -- n(qi)
    total_count INTEGER NOT NULL -- total occurrences
);

-- Create document statistics
CREATE TABLE doc_stats (
    doc_id INTEGER PRIMARY KEY REFERENCES documents(id),
    length INTEGER NOT NULL,
    terms JSONB NOT NULL -- stores term frequencies
);

-- Create materialized view for global statistics
CREATE MATERIALIZED VIEW global_stats AS
SELECT 
    COUNT(*) as total_docs,
    AVG(length) as avg_length
FROM doc_stats;

-- Function to tokenize and count terms
CREATE OR REPLACE FUNCTION tokenize_and_count(content TEXT)
RETURNS TABLE (term TEXT, count INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT word, COUNT(*)::INTEGER
    FROM regexp_split_to_table(
        lower(regexp_replace(content, '[^\w\s]', ' ', 'g')), 
        '\s+'
    ) word
    WHERE length(word) > 0
    GROUP BY word;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate IDF with debugging
CREATE OR REPLACE FUNCTION calculate_idf(term_doc_count INTEGER, total_docs INTEGER)
RETURNS FLOAT AS $$
DECLARE
    numerator FLOAT;
    denominator FLOAT;
BEGIN
    numerator := total_docs + 1 - term_doc_count + 0.5;
    denominator := term_doc_count + 0.5;
    
    RAISE NOTICE 'total_docs: %, term_doc_count: %, numerator: %, denominator: %', 
                  total_docs, term_doc_count, numerator, denominator;
    
    IF numerator <= 0 THEN
        -- If numerator would be negative, return a small positive value
        RETURN 0.0;
    END IF;
    
    RETURN ln(numerator/denominator);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate BM25 score for a single term
CREATE OR REPLACE FUNCTION bm25_term_score(
    tf INTEGER,
    doc_length INTEGER,
    idf FLOAT,
    avg_length FLOAT,
    k1 FLOAT DEFAULT 1.2,
    b FLOAT DEFAULT 0.75
) RETURNS FLOAT AS $$
BEGIN
    RETURN idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * doc_length/avg_length));
END;
$$ LANGUAGE plpgsql;

-- Function to index a document
CREATE OR REPLACE FUNCTION index_document(doc_content TEXT) 
RETURNS INTEGER AS $$
DECLARE
    doc_id INTEGER;
    doc_length INTEGER;
    term_counts JSONB;
BEGIN
    -- Insert document
    INSERT INTO documents (content) VALUES (doc_content) 
    RETURNING id INTO doc_id;
    
    -- Calculate term frequencies
    WITH term_counts_cte AS (
        SELECT * FROM tokenize_and_count(doc_content)
    )
    SELECT 
        json_object_agg(term, count)::jsonb,
        sum(count)
    INTO term_counts, doc_length
    FROM term_counts_cte;
    
    -- Update document stats
    INSERT INTO doc_stats (doc_id, length, terms)
    VALUES (doc_id, doc_length, term_counts);
    
    -- Update term stats
    INSERT INTO term_stats (term, doc_count, total_count)
    SELECT 
        term,
        1,
        (term_counts->term)::integer
    FROM jsonb_object_keys(term_counts) term
    ON CONFLICT (term) DO UPDATE SET
        doc_count = term_stats.doc_count + 1,
        total_count = term_stats.total_count + (EXCLUDED.total_count);
    
    RETURN doc_id;
END;
$$ LANGUAGE plpgsql;

-- Function to search documents using BM25
CREATE OR REPLACE FUNCTION search_documents(
    query_text TEXT,
    k1 FLOAT DEFAULT 1.2,
    b FLOAT DEFAULT 0.75,
    limit_val INTEGER DEFAULT 10
) RETURNS TABLE (
    doc_id INTEGER,
    score FLOAT,
    content TEXT
) AS $$
DECLARE
    v_total_docs INTEGER;
    v_avg_length FLOAT;
BEGIN
    -- Get global stats
    SELECT gs.total_docs, gs.avg_length 
    INTO v_total_docs, v_avg_length
    FROM global_stats gs;
    
    RETURN QUERY
    WITH query_terms AS (
        SELECT term FROM tokenize_and_count(query_text)
    ),
    scores AS (
        SELECT 
            d.doc_id,
            SUM(
                bm25_term_score(
                    (d.terms->>t.term)::INTEGER,
                    d.length,
                    calculate_idf(ts.doc_count, v_total_docs),
                    v_avg_length,
                    k1,
                    b
                )
            ) as score
        FROM doc_stats d
        CROSS JOIN query_terms t
        JOIN term_stats ts ON ts.term = t.term
        WHERE d.terms ? t.term
        GROUP BY d.doc_id
    )
    SELECT 
        s.doc_id,
        s.score,
        doc.content
    FROM scores s
    JOIN documents doc ON doc.id = s.doc_id
    ORDER BY score DESC
    LIMIT limit_val;
END;
$$ LANGUAGE plpgsql;
```

### Usage Example

```sql
-- Index some documents
SELECT index_document('The quick brown fox jumps over the lazy dog');
SELECT index_document('A quick brown cat sleeps by the window');
SELECT index_document('The lazy dog sleeps all day long');

-- Refresh materialized view
REFRESH MATERIALIZED VIEW global_stats;

-- Search documents
SELECT * FROM search_documents('quick brown');
```

### Indexing Considerations

For the pure Postgres implementation, we should consider:

1. B-tree index on term_stats(term)
```sql
CREATE INDEX idx_term_stats_term ON term_stats(term);
```

2. GIN index on doc_stats(terms)
```sql
CREATE INDEX idx_doc_stats_terms ON doc_stats USING gin(terms);
```

## Part 2: Sparse Vector Implementation

This approach uses pgvector's sparse vector support to implement BM25. First, enable pgvector:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables for vector approach
CREATE TABLE vector_documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    sparse_embedding sparsevec -- for sparse BM25 vectors
);

-- Create vocabulary table for mapping terms to indices
CREATE TABLE vocabulary (
    term TEXT PRIMARY KEY,
    idx INTEGER NOT NULL UNIQUE,
    doc_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0
);

-- Create materialized view for vector document statistics
CREATE MATERIALIZED VIEW vector_doc_stats AS
SELECT 
    COUNT(*) as total_docs,
    AVG(array_length(regexp_split_to_array(content, '\s+'), 1)) as avg_length
FROM vector_documents;

-- Function to get or create term index
CREATE OR REPLACE FUNCTION get_or_create_term_idx(p_term TEXT) 
RETURNS INTEGER AS $$
DECLARE
    v_idx INTEGER;
BEGIN
    INSERT INTO vocabulary (term, idx)
    VALUES (p_term, COALESCE((SELECT MAX(idx) + 1 FROM vocabulary), 0))
    ON CONFLICT (term) DO UPDATE SET term = EXCLUDED.term
    RETURNING idx INTO v_idx;
    
    RETURN v_idx;
END;
$$ LANGUAGE plpgsql;

-- Function to create sparse BM25 vector
CREATE OR REPLACE FUNCTION create_bm25_sparse_vector(
    doc_content TEXT,
    k1 FLOAT DEFAULT 1.2,
    b FLOAT DEFAULT 0.75
) RETURNS sparsevec AS $$
DECLARE
    doc_terms JSONB;
    doc_length INTEGER;
    v_total_docs INTEGER;
    v_avg_length FLOAT;
    result_vector TEXT := '{';
    term_record RECORD;
BEGIN
    -- Get document statistics
    WITH term_counts AS (
        SELECT * FROM tokenize_and_count(doc_content)
    )
    SELECT json_object_agg(term, count), COUNT(*)
    INTO doc_terms, doc_length
    FROM term_counts;
    
    -- Get global statistics - use count from vector_documents instead of materialized view
    SELECT COALESCE(COUNT(*), 0), COALESCE(AVG(array_length(regexp_split_to_array(content, '\s+'), 1)), 1)
    INTO v_total_docs, v_avg_length
    FROM vector_documents;
    
    -- Add 1 to total_docs to account for current document
    v_total_docs := v_total_docs + 1;
    
    -- Build sparse vector
    FOR term_record IN 
        SELECT 
            get_or_create_term_idx(t.term_key) as idx,
            (doc_terms->>t.term_key)::INTEGER as tf,
            COALESCE(v.doc_count, 0) as doc_count
        FROM (
            SELECT key as term_key 
            FROM jsonb_object_keys(doc_terms) AS key
        ) t
        LEFT JOIN vocabulary v ON v.term = t.term_key
    LOOP
        -- Calculate BM25 weight for term
        result_vector := result_vector || 
            term_record.idx::TEXT || ':' ||
            bm25_term_score(
                term_record.tf,
                doc_length,
                calculate_idf(term_record.doc_count, v_total_docs),
                v_avg_length,
                k1,
                b
            )::TEXT || ',';
    END LOOP;
    
    -- Remove trailing comma and add closing brace
    IF result_vector = '{' THEN
        result_vector := '{1:0}';  -- Default empty vector
    ELSE
        result_vector := rtrim(result_vector, ',') || '}';
    END IF;
    
    -- Add dimensions
    result_vector := result_vector || '/10000';
    
    RETURN result_vector::sparsevec;
END;
$$ LANGUAGE plpgsql;

-- Function to index document with sparse vector
CREATE OR REPLACE FUNCTION index_vector_document(
    doc_content TEXT,
    k1 FLOAT DEFAULT 1.2,
    b FLOAT DEFAULT 0.75
) RETURNS INTEGER AS $$
DECLARE
    doc_id INTEGER;
BEGIN
    INSERT INTO vector_documents (content, sparse_embedding)
    VALUES (
        doc_content,
        create_bm25_sparse_vector(doc_content, k1, b)
    )
    RETURNING id INTO doc_id;
    
    -- Update vocabulary statistics
    WITH term_counts AS (
        SELECT * FROM tokenize_and_count(doc_content)
    )
    UPDATE vocabulary v
    SET 
        doc_count = COALESCE(doc_count, 0) + 1,
        total_count = COALESCE(total_count, 0) + tc.count
    FROM term_counts tc
    WHERE v.term = tc.term;
    
    RETURN doc_id;
END;
$$ LANGUAGE plpgsql;

-- Function to search using sparse vectors
CREATE OR REPLACE FUNCTION search_sparse_vectors(
    query_text TEXT,
    limit_val INTEGER DEFAULT 10
) RETURNS TABLE (
    id INTEGER,
    content TEXT,
    similarity FLOAT
) AS $$
DECLARE
    query_vector sparsevec;
BEGIN
    query_vector := create_bm25_sparse_vector(query_text);
    
    RETURN QUERY
    SELECT 
        d.id,
        d.content,
        1 - (d.sparse_embedding <=> query_vector) as similarity
    FROM vector_documents d
    WHERE d.sparse_embedding IS NOT NULL
    ORDER BY d.sparse_embedding <=> query_vector
    LIMIT limit_val;
END;
$$ LANGUAGE plpgsql;
```

### Usage Example

```sql
-- Index documents
SELECT index_vector_document('The quick brown fox jumps over the lazy dog');
SELECT index_vector_document('A quick brown cat sleeps by the window');
SELECT index_vector_document('The lazy dog sleeps all day long');

-- Refresh statistics
REFRESH MATERIALIZED VIEW vector_doc_stats;

-- Create IVFFlat index for better performance
CREATE INDEX ON vector_documents 
USING ivfflat (sparse_embedding sparsevec_cosine_ops)
WITH (lists = 100);

>[!WARNING]
>The `ivfflat` index is not supported for sparse vectors at present.

-- Search using sparse vectors
SELECT * FROM search_sparse_vectors('quick brown');
```

## Performance Comparison

The two approaches have different trade-offs:

1. Pure Postgres BM25:
   - Pros: Exact BM25 scoring, easy to understand and modify
   - Cons: Can be slower for large collections, requires more storage

2. Sparse Vectors:
   - Pros: Maintains term importance, efficient storage for sparse data
   - Cons: Limited by vocabulary size, requires careful index tuning

For optimal performance, consider:
- Using partitioning for large collections
- Regular updates to materialized views
- Monitoring and adjusting index parameters