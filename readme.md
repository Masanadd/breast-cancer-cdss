# Breast Cancer - Clinical Decision Support System (CDSS)

Este sistema de soporte clínico está diseñado para ayudar a profesionales de la salud a consultar información actualizada sobre el **cáncer de mama**, basándose en las **Guías ESMO 2024**.

La aplicación permite realizar consultas clínicas en lenguaje natural y entrega respuestas clasificadas en:

- 📖 Diagnóstico
- 💊 Opciones de Tratamiento
- ✅ Recomendaciones

---

## Funcionalidades

- Procesamiento de consultas clínicas usando LLM.
- Recuperación semántica con Pinecone.
- Embeddings generados con modelos de Hugging Face.
- Interfaz en Streamlit con diseño personalizado.

---

## 📁 Estructura del proyecto

```
├── app.py                  # Aplicación principal Streamlit
├── data/
│   ├── Breast_cancer_poket_guidelines.pdf
│   ├── chunks.jsonl        # <-- Ignorado en .gitignore
│   └── embeddings.jsonl    # <-- Ignorado en .gitignore
├── static/
│   ├── background.png
│   ├── image.png
│   └── logo.png
├── query_engine_cohere.py  # Búsqueda + generación con Cohere
├── preprocess.py           # División y limpieza del texto guía
├── upload_to_pinecone.py   # Carga de vectores a Pinecone
├── test_hf.py              # Pruebas locales con modelos HF
├── .env.example            # Variables de entorno requeridas
├── requirements.txt        # Dependencias
└── README.md               # Este archivo
```
---

## ⚙️ Requisitos

- Python 3.9 o superior
- Claves API de:
  - [Pinecone](https://www.pinecone.io/)
  - [Hugging Face](https://huggingface.co/)
  - [Cohere](https://cohere.com/) (opcional)

---

## 🛠 Instalación

```bash
git clone https://github.com/tu_usuario/breast-cancer-cdss.git
cd breast-cancer-cdss
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Copia y completa tus claves en .env
```

## ▶️ Ejecutar la aplicación

```
streamlit run app.py
``` 

📝 Licencia

Este proyecto se distribuye bajo la Licencia MIT.

