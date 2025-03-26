from sentence_transformers import SentenceTransformer
import torch

torch.hub.set_dir("./cache")  # Forzar almacenamiento en caché local

print("🔄 Descargando modelo, espera un momento...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder="./cache")
print("✅ Modelo descargado correctamente")
