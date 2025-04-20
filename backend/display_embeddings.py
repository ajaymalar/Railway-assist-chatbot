import chromadb
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sentence_transformers import SentenceTransformer  # Use proper embeddings

# ✅ Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# ✅ Get available collections
collections = chroma_client.list_collections()
if not collections:
    print("⚠️ No collections found in ChromaDB. Please ensure data is added first.")
    exit()

# ✅ Fix for Chroma v0.6.0+ (Use only the collection name string)
collection_name = collections[0]
print(f"🔹 Using collection: {collection_name}")

# ✅ Load the collection
collection = chroma_client.get_collection(collection_name)

# ✅ Fetch all stored embeddings
results = collection.get(include=["embeddings", "metadatas"])

# ✅ Fix: Properly check if embeddings exist
if results["embeddings"] is None or len(results["embeddings"]) == 0:
    print("⚠️ No embeddings found in the collection.")
    exit()

embeddings = np.array(results["embeddings"])
metadata = results["metadatas"]

# ✅ Fix: Normalize stored embeddings
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# ✅ Use a proper embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Load a model

# ✅ Display embeddings while typing a query
while True:
    query = input("🔍 Enter your query (or type 'exit' to quit): ")
    if query.lower() == "exit":
        break

    # ✅ Encode query properly
    query_embedding = model.encode(query, normalize_embeddings=True)

    # ✅ Compute similarity (cosine similarity)
    similarities = np.dot(embeddings, query_embedding)

    # ✅ Get top result
    top_index = np.argmax(similarities)
    print(f"🔹 Closest match: {metadata[top_index]} (Similarity: {similarities[top_index]:.2f})")

# ✅ Model Evaluation Metrics

# 🎯 Dummy ground truth labels and predictions (Replace with actual labels)
y_true = np.random.randint(0, 2, len(embeddings))  # Actual labels (0 or 1)
y_pred = np.random.randint(0, 2, len(embeddings))  # Predicted labels

# 📊 Accuracy Score
accuracy = accuracy_score(y_true, y_pred)
print(f"\n✅ Model Accuracy: {accuracy:.2f}")

# 📊 Confusion Matrix
cm = confusion_matrix(y_true, y_pred)
print("\nConfusion Matrix:\n", cm)

# 📊 Classification Report
print("\nClassification Report:\n", classification_report(y_true, y_pred))

# 📊 Plot Confusion Matrix
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Class 0", "Class 1"], yticklabels=["Class 0", "Class 1"])
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()
