import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB client and model
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="railway_faq")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample user query
query = "What schemes are available for senior citizens?"

# Encode query to match stored embeddings
query_embedding = model.encode(query).tolist()

# Retrieve relevant schemes
results = collection.query(query_embeddings=[query_embedding], n_results=3)

# Print results
for metadata in results["metadatas"][0]:
    print("Retrieved Scheme:\n", metadata["text"])
