import json
import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Cargar variables del archivo .env
load_dotenv()

# 📌 Obtener variables de entorno
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("INDEX_NAME")

# 📂 Ruta del archivo con embeddings
EMBEDDINGS_FILE = "data/embeddings.jsonl"
BATCH_SIZE = 100  # Tamaño del batch para carga optimizada

def load_embeddings(path):
    """Carga los embeddings desde un archivo JSONL"""
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def upsert_in_batches(index, data, batch_size):
    """Sube embeddings a Pinecone en lotes"""
    vectors = [
        (str(i), item["embedding"], {"title": item["title"], "text": item["text"]})
        for i, item in enumerate(data)
    ]

    total_vectors = len(vectors)
    for i in range(0, total_vectors, batch_size):
        batch = vectors[i:i+batch_size]
        index.upsert(vectors=batch)
        print(f"🔄 Batch subido: {i} a {min(i + batch_size, total_vectors)} de {total_vectors}")

def main():
    print("🔌 Conectando a Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Validar si el índice existe
    existing_indexes = pc.list_indexes().names()
    if INDEX_NAME not in existing_indexes:
        print(f"❌ Índice '{INDEX_NAME}' no encontrado. Crea el índice antes de subir embeddings.")
        return

    index = pc.Index(INDEX_NAME)

    print("📚 Cargando embeddings...")
    data = load_embeddings(EMBEDDINGS_FILE)

    print(f"⬆️ Subiendo embeddings en lotes de {BATCH_SIZE}...")
    upsert_in_batches(index, data, BATCH_SIZE)

    print("✅ ¡Embeddings subidos correctamente a Pinecone!")

if __name__ == "__main__":
    main()
