from sentence_transformers import SentenceTransformer
import numpy as np

# Demo texts
texts = [
    'The capital of France is Paris',
    'Paris is known for the Eiffel Tower',
    'The capital of Japan is Tokyo',
    'Tokyo is famous for sushi'
]

# Load model
model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)

# Generate embeddings
embeddings = model.encode(texts)

# Print only the SQL update statements without any other text
for i, (text, embedding) in enumerate(zip(texts, embeddings), 1):
    vector_str = ','.join(map(str, embedding.tolist()))
    print(f"UPDATE documents SET embedding = ARRAY[{vector_str}]::vector WHERE id = {i};")