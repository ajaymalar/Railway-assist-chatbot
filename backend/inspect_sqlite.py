import sqlite3

# Path to the ChromaDB SQLite database
db_path = "chroma_db/chroma.sqlite3"

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("🔹 Tables in ChromaDB:")
for table in tables:
    print(f" - {table[0]}")

# Fetch some data from the 'collections' table
cursor.execute("SELECT * FROM collections;")
collections = cursor.fetchall()
print("\n🔹 Collections Data:")
for row in collections:
    print(row)

# Fetch some data from the 'embeddings' table (if it exists)
cursor.execute("SELECT * FROM embeddings LIMIT 5;")
embeddings = cursor.fetchall()
print("\n🔹 Sample Embeddings Data:")
for row in embeddings:
    print(row)

# Close connection
conn.close()
