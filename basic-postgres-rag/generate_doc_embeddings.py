### A script to generate embeddings for a set of documents and store them in a database

from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_values
import os
import numpy as np

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

def get_embeddings(texts, prefix="search_document: "): # if the query type is not specified, the prefex used is that for documents
    """Generate embeddings for given texts using the correct prefix."""
    model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
    # Add prefix to each text
    prefixed_texts = [f"{prefix}{text}" for text in texts]
    embeddings = model.encode(prefixed_texts)
    # Normalize the vectors
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized = embeddings / norms
    
    # Debug info
    print("\nEmbedding stats before storage:")
    for text, emb in zip(texts, normalized):
        print(f"{text[:20]}...: norm={np.linalg.norm(emb):.4f}, mean={np.mean(emb):.4f}")
    
    return normalized

def setup_demo_data(connection_string="dbname=vector_demo user=vector_user password=demo_password"):
    """Create table, insert texts, calculate embeddings, and add their embeddings."""
    print("Starting demo data setup...")
    
    # Demo texts
    texts = [
        'The capital of France is Paris',
        'Paris is known for the Eiffel Tower',
        'The capital of Japan is Tokyo',
        'Tokyo is famous for sushi'
    ]
    print(f"Preparing to process {len(texts)} demo texts...")
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = get_embeddings(texts)
    print(f"Generated embeddings with shape: {embeddings.shape}")
    
    # Connect to database and update
    print("Connecting to database...")
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            # Create table - modified to use CASCADE
            print("Creating documents table...")
            cur.execute("""
                DROP TABLE IF EXISTS documents CASCADE;
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(768)
                );
            """)
            
            # Insert texts and embeddings in one go
            print("Inserting texts and embeddings into database...")
            data = [(text, embedding.tolist()) for text, embedding in zip(texts, embeddings)]
            execute_values(
                cur,
                "INSERT INTO documents (content, embedding) VALUES %s",
                data,
                template="(%s, %s::vector)"
            )
        conn.commit()
    print("Setup completed successfully!")

if __name__ == "__main__":
    setup_demo_data()