from sentence_transformers import SentenceTransformer
import psycopg2
import numpy as np

def get_query_embedding(query_text, prefix="search_query: "):
    """Generate embedding for a query with proper prefix."""
    model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
    prefixed_text = f"{prefix}{query_text}"
    embedding = model.encode([prefixed_text])[0]
    # Normalize the vector
    return embedding / np.linalg.norm(embedding)

def search_documents(query, connection_string="dbname=vector_demo user=vector_user password=demo_password"):
    query_embedding = get_query_embedding(query)
    print(f"\nQuery vector norm: {np.linalg.norm(query_embedding):.4f}")
    
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            # Use cosine similarity formula: dot(a,b)/(|a|*|b|)
            cur.execute("""
                SELECT 
                    (embedding <#> %s::vector) / 
                    (sqrt(abs(embedding <#> embedding)) * sqrt(abs(%s::vector <#> %s::vector))) as cosine_sim,
                    content
                FROM documents
                ORDER BY cosine_sim DESC
                LIMIT 4;
            """, (query_embedding.tolist(), query_embedding.tolist(), query_embedding.tolist()))
            
            results = cur.fetchall()
    
    return results

def main():
    query = "Tell me about Paris"
    print("Dense Vector Search")
    print("-------------------")
    print(f"Query: {query}")
    
    results = search_documents(query)
    
    print("\nSearch Results:")
    print("---------------")
    for distance, content in results:
        print(f"Raw Distance/Similarity: {distance:.4f}")
        print(f"Content: {content}\n")

if __name__ == "__main__":
    main() 