from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import execute_values

def get_embeddings(texts, prefix="search_document: "):
    """Generate embeddings for given texts using the correct prefix."""
    model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
    # Add prefix to each text
    prefixed_texts = [f"{prefix}{text}" for text in texts]
    return model.encode(prefixed_texts)

def setup_demo_data(connection_string="dbname=vector_demo user=vector_user password=demo_password"):
    """Create table, insert texts, and add their embeddings."""
    # Demo texts
    texts = [
        'The capital of France is Paris',
        'Paris is known for the Eiffel Tower',
        'The capital of Japan is Tokyo',
        'Tokyo is famous for sushi'
    ]
    
    # Generate embeddings
    embeddings = get_embeddings(texts)
    
    # Connect to database and update
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            # Create table
            cur.execute("""
                DROP TABLE IF EXISTS documents;
                CREATE TABLE documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding vector(768)
                );
            """)
            
            # Insert texts and embeddings in one go
            data = [(text, embedding.tolist()) for text, embedding in zip(texts, embeddings)]
            execute_values(
                cur,
                "INSERT INTO documents (content, embedding) VALUES %s",
                data,
                template="(%s, %s::vector)",
                page_size=100
            )
        conn.commit()

if __name__ == "__main__":
    setup_demo_data()