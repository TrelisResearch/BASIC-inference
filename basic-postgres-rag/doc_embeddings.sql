-- Get document embeddings with proper prefix
WITH query AS (
    SELECT embedding 
    FROM documents 
    WHERE content LIKE '%Paris%' 
    LIMIT 1
)
SELECT 
    d.content,
    1 - (d.embedding <#> q.embedding) as similarity
FROM documents d, query q
ORDER BY d.embedding <#> q.embedding
LIMIT 4; 