from sentence_transformers import SentenceTransformer
import json
import os
import time

# Parámetros
CHUNKS_FILE = "data/chunks.jsonl"
EMBEDDINGS_FILE = "data/embeddings.jsonl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32  # configurable según memoria/hardware disponible

def load_chunks(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Archivo no encontrado: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def save_embeddings(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write("\n")

def generate_embeddings(model, texts, batch_size):
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True)
    return embeddings

def main():
    start_time = time.time()

    print("📚 Cargando chunks...")
    chunks = load_chunks(CHUNKS_FILE)
    texts = [chunk["text"] for chunk in chunks]

    print(f"🔍 Cargando modelo de embeddings: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print("🧮 Generando embeddings...")
    embeddings = generate_embeddings(model, texts, BATCH_SIZE)

    print("💾 Guardando embeddings en archivo...")
    data_with_embeddings = [
        {
            "title": chunk["title"],
            "text": chunk["text"],
            "embedding": vector.tolist()
        }
        for chunk, vector in zip(chunks, embeddings)
    ]

    save_embeddings(data_with_embeddings, EMBEDDINGS_FILE)
    elapsed_time = time.time() - start_time
    print(f"✅ Embeddings guardados exitosamente en: {EMBEDDINGS_FILE}")
    print(f"⏱️ Tiempo total del proceso: {elapsed_time:.2f} segundos")

if __name__ == "__main__":
    main()
