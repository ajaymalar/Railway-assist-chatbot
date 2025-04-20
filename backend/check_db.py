import chromadb

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="railway_faq")

# Check number of documents stored
count = collection.count()
print(f"Total documents in ChromaDB: {count}")

# If data exists, fetch a sample entry
if count > 0:
    results = collection.get(ids=["0"])  # Get first entry
    print("Sample data retrieved:", results)
else:
    print("No data found in ChromaDB. Try re-running train_data.py.")
