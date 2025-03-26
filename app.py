import streamlit as st
from query_engine_cohere import search_pinecone, generate_answer

# Configuración de la página
st.set_page_config(
    page_title="Asistente Oncológico: Cáncer de Mama",
    layout="centered",
    initial_sidebar_state="expanded"
)

# 🔻 CSS personalizado con mejoras
custom_css = """
<style>
/* Fondo con degradado suave */
.stApp {
    background: linear-gradient(to bottom, rgba(255,255,255,0.9) 0%, rgba(248,240,251,0.85) 50%, rgba(240,225,247,0.8) 100%);
    backdrop-filter: blur(8px);
}

/* Borde morado para el área de texto */
.stTextArea textarea {
    border: 2px solid #9c27b0 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}

/* Contenedor principal mejorado */
main .block-container {
    background-color: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(8px);
    border-radius: 20px;
    padding: 1.5rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    margin-top: 1rem !important;
}

/* Estilos unificados para secciones */
.section-title {
    border-left: 4px solid #9c27b0;
    padding-left: 1rem;
    margin: 1.5rem 0 1rem 0;
    color: #6a1b9a !important;
    font-size: 1.8rem !important;
}

.section-content {
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.treatment-item {
    background: rgba(245, 230, 250, 0.3);
    padding: 1rem;
    margin: 0.8rem 0;
    border-left: 3px solid #9c27b0;
    border-radius: 6px;
}

.section-text {
    margin: 1rem 0;
    line-height: 1.6;
    padding: 0.5rem;
}

/* Botón principal mejorado */
.stButton > button {
    background: linear-gradient(45deg, #d8b4ef, #b388eb) !important;
    margin: 1rem 0 !important;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
    transition: 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(179, 136, 235, 0.4);
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    try:
        st.image("logo.png", width=100)
    except FileNotFoundError:
        st.error("Logo no encontrado")
    
    st.title("Asistente Oncológico: Cáncer de Mama - Clinical Decision Support System (CDSS)")
    st.markdown("""
    Esta aplicación se basa en las **Guías de Práctica Clínica de la ESMO 2024** para cáncer de mama.
    Ingresa preguntas clínicas para obtener respuestas basadas en evidencia.
    """)

# Área principal
st.title("Consulta clínica sobre cáncer de mama")

query = st.text_area("📝 Escribe aquí tu consulta:", height=120)

def detectar_intencion(pregunta):
    pregunta = pregunta.lower()
    intenciones = {
        'diagnostico': ['diagnóstico', 'diagnosticar', 'evaluar', 'pruebas'],
        'tratamiento': ['tratamiento', 'terapia', 'fármacos', 'intervención'],
        'recomendaciones': ['recomendaciones', 'consejos', 'seguimiento']
    }
    
    detected = []
    for key, words in intenciones.items():
        if any(word in pregunta for word in words):
            detected.append(key)
    return detected if detected else ['general']

def procesar_respuesta(respuesta, intenciones):
    secciones = {
        'Diagnóstico': [],
        'Opciones de Tratamiento': [],
        'Recomendaciones': []
    }
    
    current_section = None
    for line in respuesta.split('\n'):
        line = line.strip()
        if 'Diagnóstico:' in line:
            current_section = 'Diagnóstico'
        elif 'Opciones de Tratamiento' in line:
            current_section = 'Opciones de Tratamiento'
        elif 'Recomendaciones:' in line:
            current_section = 'Recomendaciones'
        elif current_section and line:
            secciones[current_section].append(line)
    
    if 'general' not in intenciones:
        return {k: v for k, v in secciones.items() if any(s in k.lower() for s in intenciones)}
    return secciones

if st.button("🔎 Consultar"):
    if not query.strip():
        st.warning("⚠️ Por favor, ingresa una pregunta válida.")
    else:
        try:
            with st.spinner("Analizando consulta y generando respuesta..."):
                intenciones = detectar_intencion(query)
                respuesta = generate_answer(query, search_pinecone(query))
                
                if not respuesta:
                    st.error("⚠️ No se pudo generar respuesta")
                    st.stop()
                
                secciones = procesar_respuesta(respuesta, intenciones)
                
                with st.container():
                    for seccion, contenido in secciones.items():
                        if contenido:
                            st.markdown(f'<div class="section-title"><h2>{seccion}</h2></div>', unsafe_allow_html=True)
                            st.markdown('<div class="section-content">', unsafe_allow_html=True)
                            
                            for line in contenido:
                                line_clean = line.strip()
                                if line_clean.startswith(('-', '•')):
                                    content = line_clean.replace('-', '').replace('•', '').strip()
                                    st.markdown(f"""
                                    <div class="treatment-item">
                                        🔹 {content}
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div class="section-text">{line_clean}</div>', unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")
            st.stop()
else:
    st.info("💡 Ejemplo: '¿Qué opciones de tratamiento existen para HER2+?' o 'Recomendaciones de seguimiento postratamiento'")