import os
import json
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import cohere



# Cargar variables de entorno
load_dotenv()

# 📌 Variables de entorno
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
INDEX_NAME = os.getenv("INDEX_NAME")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# 🔍 Modelo de embeddings
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Inicializar globalmente para evitar recargas
embedding_model = None
pinecone_index = None
cohere_client = cohere.Client(COHERE_API_KEY)

def load_embedding_model():
    global embedding_model
    if embedding_model is None:
        print(f"🔍 Cargando modelo: {EMBEDDING_MODEL_NAME}")
        embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return embedding_model

def get_pinecone_index():
    global pinecone_index
    if pinecone_index is None:
        print("🔌 Conectando a Pinecone...")
        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_index = pc.Index(INDEX_NAME)
    return pinecone_index

def search_pinecone(query, top_k=5):
    index = get_pinecone_index()
    embedding_model = load_embedding_model()

    print(f"🔎 Buscando en Pinecone: '{query}'")
    query_embedding = embedding_model.encode(query).tolist()

    response = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    return [
        {
            "score": match["score"],
            "title": match["metadata"]["title"],
            "text": match["metadata"]["text"]
        }
        for match in response["matches"]
    ]

def generate_answer(query, retrieved_docs):
    # Combina claramente los textos relevantes para el contexto
    context = "\n\n".join([
        f"Título: {doc['title']}\nContenido: {doc['text']}"
        for doc in retrieved_docs
    ])
    # Clasifica intención de la consulta
    query_lower = query.lower()
    if "tratamiento" in query_lower or "tratar" in query_lower:
        secciones = "- Responde solo con las opciones de tratamiento más relevantes.\n- Proporciona un mínimo de contexto solo si es necesario."
    elif "diagnóstico" in query_lower:
        secciones = "- Limítate a los procedimientos y criterios de diagnóstico según el contexto.\n- No incluyas opciones de tratamiento ni recomendaciones."
    elif "recomendaciones" in query_lower:
        secciones = "- Proporciona únicamente recomendaciones clínicas basadas en guías.\n- No repitas diagnóstico ni tratamientos si no se piden."
    else:
        secciones = "- Organiza la respuesta en: Diagnóstico, Opciones de Tratamiento y Recomendaciones."


    # Prompt claro, sin referencias numéricas
    prompt = f"""
    Eres un oncólogo senior especializado en cáncer de mama.
    Usa únicamente la información proporcionada en el contexto siguiente para responder.

    CONTEXTO DISPONIBLE:
    {context}

    INSTRUCCIONES:
    - Organiza la respuesta en las siguientes secciones:
      1. Diagnóstico
      2. Opciones de Tratamiento
      3. Recomendaciones
    - Proporciona una respuesta clara y precisa, priorizando tratamientos basados en biomarcadores (HER2+, HR+, etc.) y clasificación TNM cuando sea relevante.
    - Si alguna información no está disponible explícitamente en el contexto proporcionado, indica claramente que no dispones de dicha información.
    - No utilices referencias como [1], [2] o similares.

    PREGUNTA:
    {query}

    RESPUESTA:
    """

    response = cohere_client.generate(
        model="command-r-plus",
        prompt=prompt,
        max_tokens=800,
        temperature=0.1,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        truncate="END"
    )

    import re
    raw_text = response.generations[0].text.strip()
    cleaned_answer = re.sub(r'\[\d+\]', '', raw_text)
    return cleaned_answer
 

def main():
    load_embedding_model()
    get_pinecone_index()

    while True:
        query = input("\n📝 Pregunta (o 'exit' para salir): ")
        if query.lower() == "exit":
            print("👋 Saliendo...")
            break
        
        results = search_pinecone(query)

        print("\n📌 **Resultados más relevantes:**")
        for idx, res in enumerate(results, 1):
            print(f"\n🔹 **{res['title']}** (Score: {res['score']:.4f})")
            print(f"{res['text'][:200]}..." if len(res['text']) > 200 else res['text'])

        answer = generate_answer(query, results)

        print("\n🧠 **Respuesta generada:**")
        print(answer)

if __name__ == "__main__":
    main()
