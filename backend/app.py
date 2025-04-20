from flask import Flask, request, jsonify, g
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
import chromadb
import subprocess
import logging
import os
import time
import jwt
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from auth import auth_bp, db  # User model and login/signup

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# Config
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB + Blueprint
db.init_app(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load ChromaDB and SentenceTransformer
try:
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection(name="railway_faq")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logging.info("ChromaDB & embedding model loaded.")
except Exception as e:
    logging.error(f"Failed to load ChromaDB or model: {e}")
    exit(1)

# In-memory context per user
user_context = {}

# JWT auth decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"error": "Token is missing!"}), 403
        try:
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            g.current_user_id = decoded.get("user_id")
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token!"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "🚀 Chatbot API is running!"})

# ✅ Chat route with context memory
@app.route("/chat", methods=["POST"])
@token_required
def chat():
    try:
        user_input = request.json.get("message", "").strip()
        if not user_input:
            return jsonify({"error": "Empty message received"}), 400

        user_id = g.current_user_id
        logging.info(f"[{user_id}] User Input: {user_input}")

        previous_context = user_context.get(user_id, "")
        full_prompt = f"{previous_context}\nFollow-up: {user_input}" if previous_context else user_input

        user_embedding = model.encode(full_prompt).tolist()
        results = collection.query(query_embeddings=[user_embedding], n_results=3)
        retrieved_texts = list(set(
            metadata.get("text", "") for metadata in results.get("metadatas", [[]])[0] if metadata
        ))
        context = "\n".join(retrieved_texts[:3]) if retrieved_texts else "No relevant data found."

        final_prompt = f"Use the following context to answer the query:\n\n{context}\n\nUser Query: {user_input}"
        logging.info(f"[Prompt] {final_prompt[:300].replace(chr(10), ' ')}")

        max_retries = 2
        for attempt in range(max_retries):
            try:
                result = subprocess.run(
                    ["ollama", "run", "phi"],
                    input=final_prompt,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    timeout=60
                )
                if result.returncode == 0:
                    break
                logging.warning(f"Ollama failed (Attempt {attempt+1}): {result.stderr}")
                time.sleep(2)
            except subprocess.TimeoutExpired:
                return jsonify({"error": "Ollama timed out"}), 500
            except Exception as e:
                return jsonify({"error": f"Ollama error: {e}"}), 500

        response = result.stdout.strip() or "Sorry, couldn't find an answer."
        user_context[user_id] = f"{full_prompt}\nBot: {response}"

        return jsonify({"response": response})

    except Exception as e:
        logging.error(f"Chat Exception: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# ✅ Voice transcription route
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No audio file received"}), 400

    audio_path = "temp_audio.webm"
    file.save(audio_path)

    try:
        # Convert to wav (requires ffmpeg installed)
        wav_path = "temp_audio.wav"
        subprocess.run(["ffmpeg", "-y", "-i", audio_path, wav_path], check=True)

        # Transcribe with whisper (requires whisper installed)
        result = subprocess.run(
            ["whisper", wav_path, "--language", "en", "--model", "base", "--output_format", "txt"],
            capture_output=True,
            text=True,
            timeout=60
        )

        transcript_file = "temp_audio.txt"
        if os.path.exists(transcript_file):
            with open(transcript_file, "r") as f:
                transcript = f.read().strip()
        else:
            transcript = "Transcription failed."

        return jsonify({"text": transcript})

    except Exception as e:
        logging.error(f"Transcription error: {e}")
        return jsonify({"error": f"Transcription failed: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
