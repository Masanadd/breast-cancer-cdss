import fitz  # PyMuPDF
import os
import re
import json

# Ruta al archivo PDF (ajústala si cambias el nombre o ubicación)
PDF_PATH = os.path.join("data", "Breast_cancer_poket_guidelines.pdf")
OUTPUT_PATH = "data/chunks.jsonl"

# Función para detectar encabezados en mayúsculas
def is_section_heading(text):
    return bool(re.match(r"^[A-Z][A-Z\s\-]{3,}$", text.strip()))

# Palabras clave para filtrar secciones clínicas relevantes
CLINICAL_KEYWORDS = [
    "MANAGEMENT", "TREATMENT", "THERAPY", "DIAGNOSIS", "STAGING",
    "HER2", "TRIPLE-NEGATIVE", "LUMINAL", "METASTATIC BREAST CANCER",
    "EARLY BREAST CANCER", "HEREDITARY", "PERSONALISED MEDICINE", "FOLLOW-UP"
]

def clean_text(text):
    # Limpieza básica del texto
    text = re.sub(r"\n+", "\n", text).strip()
    text = re.sub(r"\s+", " ", text)
    return text

def extract_diagram_as_text(blocks):
    """
    Transforma bloques dispersos (diagramas) en texto estructurado.
    """
    structured_text = ""
    ordered_blocks = sorted(blocks, key=lambda x: (x[1], x[0]))  # orden top-bottom, left-right
    for b in ordered_blocks:
        text = b[4].strip()
        if text:
            structured_text += f"- {text}\n"
    return structured_text

def extract_sections(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    current_section = {"title": None, "text": ""}
    
    for page in doc:
        
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda x: (x[1], x[0]))

        text_content = [b[4].strip() for b in blocks if b[4].strip()]
        
        # Detectar esquemas gráficos por la poca cantidad de texto o texto disperso
        if len(text_content) < 15 and all(len(t.split()) < 30 for t in text_content):
            diagram_text = extract_diagram_as_text(blocks)
            current_section["text"] += f"\n(Diagrama estructurado):\n{diagram_text}\n"
        else:
            for b in blocks:
                text = b[4].strip()
                if not text:
                    continue
                if is_section_heading(text) and len(text.split()) < 10:
                    if current_section["title"] or current_section["text"]:
                        sections.append(current_section)
                    current_section = {"title": text, "text": ""}
                else:
                    current_section["text"] += text + "\n"

    if current_section["title"] or current_section["text"]:
        sections.append(current_section)
    
    return sections


def filter_relevant_sections(sections):
    return [
        sec for sec in sections
        if sec["title"] and any(keyword in sec["title"] for keyword in CLINICAL_KEYWORDS)
    ]

def split_into_chunks(section, max_chunk_length=500):
    # Divide secciones grandes en chunks menores (aproximadamente 500 caracteres)
    text = section["text"]
    chunks = []
    paragraphs = text.split('. ')
    
    current_chunk = ""
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) < max_chunk_length:
            current_chunk += paragraph + ". "
        else:
            chunks.append({"title": section["title"], "text": current_chunk.strip()})
            current_chunk = paragraph + ". "
    
    if current_chunk:
        chunks.append({"title": section["title"], "text": current_chunk.strip()})

    return chunks

def save_to_jsonl(sections, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for sec in sections:
            json.dump(sec, f, ensure_ascii=False)
            f.write("\n")

def main():
    if not os.path.exists(PDF_PATH):
        print(f"❌ El archivo no fue encontrado en: {PDF_PATH}")
        return

    print("📘 Extrayendo secciones del PDF...")
    sections = extract_sections(PDF_PATH)
    print(f"🔎 Secciones totales encontradas: {len(sections)}")

    relevant_sections = filter_relevant_sections(sections)
    print(f"✅ Secciones clínicas relevantes: {len(relevant_sections)}")

    # Dividir secciones en chunks más pequeños
    all_chunks = []
    for sec in relevant_sections:
        chunks = split_into_chunks(sec)
        all_chunks.extend(chunks)

    print(f"📌 Total de chunks generados: {len(all_chunks)}")

    save_to_jsonl(all_chunks, OUTPUT_PATH)
    print(f"📄 Chunks guardados en: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
