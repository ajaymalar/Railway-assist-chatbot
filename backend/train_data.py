import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
import os

# Configuration
DATA_PATH = r"S:\CIP\Railway_data.csv"  # Update this to your correct CSV file path
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "railway_faq"

# Check if the dataset exists
if not os.path.exists(DATA_PATH):
    print(f"Data file not found: {DATA_PATH}")
    exit()

# Load railway schemes dataset
df = pd.read_csv(DATA_PATH).dropna()
print(f"Loaded {len(df)} rows from CSV.")

# Initialize SentenceTransformer model
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("SentenceTransformer model loaded successfully.")
except Exception as e:
    print(f"Error loading embedding model: {e}")
    exit()

# Setup ChromaDB client
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    print(f"Connected to ChromaDB: {COLLECTION_NAME}")
except Exception as e:
    print(f"Error initializing ChromaDB: {e}")
    exit()

# Clear existing records safely
try:
    collection.delete(where={"text": {"$ne": ""}})  # Deletes all records
    print("Cleared old embeddings from ChromaDB.")
except Exception as e:
    print(f"Error deleting existing records: {e}")

# Prepare text entries for embedding
def format_entry(row):
    return (
            f"Scheme: {row['scheme_name']}\n"
            f"Discount: {row['discount_(%)']}%\n"
            f"Eligibility: {row['eligibility_criteria']}\n"
            f"Application Mode: {row['application_mode']}\n"
            f"Validity: {row['validity_period']}\n"
            f"Authority: {row['implementing_authority']}\n"
            f"Notes: {row['additional_notes']}\n"
            f"Category: {row['scheme_category']}\n"
            f"Funding Source: {row['funding_source']}\n"
            f"Application Complexity: {row['application_complexity']}\n"
            f"Discount Category: {row['discount_category']}\n"
            f"Application Mode Type: {row['application_mode_type']}\n"
            f"Validity Type: {row['validity_type']}\n"
            f"Implementing Authority Type: {row['implementing_authority_type']}\n"
            )

texts = df.apply(format_entry, axis=1).tolist()
print(f"🔹 Prepared {len(texts)} unique entries for embedding.")

# Encode embeddings in batches
try:
    embeddings = model.encode(texts, batch_size=16, show_progress_bar=True).tolist()
    print("Embeddings generated successfully.")
except Exception as e:
    print(f"Error generating embeddings: {e}")
    exit()

# Store in ChromaDB
try:
    ids = [str(i) for i in range(len(texts))]
    metadatas = [{"text": text} for text in texts]
    collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas)
    print("Railway schemes stored successfully in ChromaDB!")
except Exception as e:
    print(f"Error storing data in ChromaDB: {e}")
