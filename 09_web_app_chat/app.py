from pathlib import Path
import sys
import json
import subprocess
import time
import importlib.util
from datetime import datetime
import streamlit as st

# =================================================<ruta_repo>\09_web_app_chat"# ============================================================
# & C:/Python314/python.exe -m streamlit run app.py
#
# ============================================================


# ============================================================
# CONFIGURACION DE RUTAS
# ============================================================

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = Path(__file__).resolve().parents[1]

MCP_SERVER_DIR = PROJECT_DIR / "08_agents_mcp" / "mcp_server"
TOOLS_PATH = MCP_SERVER_DIR / "tools.py"

LLM_CLIENT_DIR = PROJECT_DIR / "08_agents_mcp" / "llm_client"
LLM_CLIENT_PATH = LLM_CLIENT_DIR / "llm_client.py"

ORCHESTRATOR_DIR = PROJECT_DIR / "08_agents_mcp" / "orchestrator"
ORCHESTRATOR_PATH = ORCHESTRATOR_DIR / "run_decision.py"

FONDOS_DISPONIBLES_PATH = PROJECT_DIR / "01_decision_input" / "fondos_disponibles.json"
DECISIONES_DIR = PROJECT_DIR / "01_decision_input" / "decisiones"

AGENT_LABELS = {
    "research_agent": "Research",
    "macro_agent": "Macro",
    "risk_agent": "Riesgo",
    "mandates_agent": "Mandatos",
    "synthesis_agent": "Síntesis",
}


def _orchestrator_progress_path(decision_id: str) -> Path:
    return ORCHESTRATOR_DIR / f"run_{decision_id}_progress.json"


def _orchestrator_summary_json(decision_id: str) -> Path:
    return ORCHESTRATOR_DIR / f"run_{decision_id}_summary.json"


def _orchestrator_summary_md(decision_id: str) -> Path:
    return ORCHESTRATOR_DIR / f"run_{decision_id}_summary.md"


def decision_id_actual() -> str:
    return st.session_state.get("decision_id", "DECISION_001")


def leer_alias_decision(decision_id: str) -> str:
    """Devuelve el alias corto de la decisión, o cadena vacía si no existe."""
    try:
        p = decision_file_path(decision_id)
        if p.exists():
            d = json.loads(p.read_text(encoding="utf-8"))
            return d.get("alias", "")
    except Exception:
        pass
    return ""


def decision_file_path(decision_id: str) -> Path:
    if decision_id == "DECISION_001":
        return PROJECT_DIR / "01_decision_input" / "decision_actual.json"

    return DECISIONES_DIR / f"{decision_id}.json"


def cargar_fondos_disponibles() -> list:
    if not FONDOS_DISPONIBLES_PATH.exists():
        return []

    try:
        with open(FONDOS_DISPONIBLES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("fondos", [])
    except Exception:
        return []


def generar_decision_id() -> str:
    return f"DEC_{datetime.now():%Y%m%d_%H%M%S}"


def generar_alias(hipotesis: str) -> str:
    """Slug corto legible para identificar la hipótesis en la UI."""
    import re as _re
    stopwords = {"en", "el", "la", "los", "las", "un", "una", "de", "del", "al",
                 "se", "que", "y", "o", "es", "si", "por", "con", "para", "a",
                 "su", "no", "lo", "le", "les", "como", "pero", "mas", "mas",
                 "puede", "podria", "seria", "tiene"}
    texto = hipotesis.lower()
    texto = _re.sub(r'[áàä]', 'a', texto)
    texto = _re.sub(r'[éèë]', 'e', texto)
    texto = _re.sub(r'[íìï]', 'i', texto)
    texto = _re.sub(r'[óòö]', 'o', texto)
    texto = _re.sub(r'[úùü]', 'u', texto)
    texto = _re.sub(r'[^a-z0-9\s]', ' ', texto)
    palabras = [w for w in texto.split() if w not in stopwords and len(w) > 2]
    slug = '_'.join(palabras[:4])
    return slug[:30] if slug else "hipotesis"


def crear_decision(hipotesis_texto: str, fondo: dict) -> str:
    """
    Crea una nueva decisión a discreción del gestor: guarda un archivo de
    decisión en 01_decision_input/decisiones/{id}.json (mismo esquema que
    plantilla_decision.json) a partir de una hipótesis en texto libre y un
    fondo elegido, y devuelve el decision_id generado.
    """

    decision_id = generar_decision_id()
    alias = generar_alias(hipotesis_texto)

    decision_data = {
        "id_decision": decision_id,
        "alias": alias,
        "fecha_analisis": datetime.now().strftime("%Y-%m-%d"),
        "nombre_decision": hipotesis_texto[:120],
        "descripcion_corta": hipotesis_texto,
        "tipo_decision": "hipotesis_libre_gestor",
        "estado": "hipotesis_de_analisis",
        "hipotesis": {
            "descripcion_libre": hipotesis_texto,
            "fondo_codigo": fondo.get("codigo"),
            "fondo_nombre": fondo.get("nombre"),
        },
        "cartera_referencia": {
            "nombre_cartera": fondo.get("nombre"),
            "codigo_fondo": fondo.get("codigo"),
            "tipo_fondo": fondo.get("tipo_fondo"),
            "divisa_base": fondo.get("divisa_base"),
            "benchmark": fondo.get("benchmark_principal"),
            "datos_disponibles": fondo.get("datos_disponibles", {}),
            "nota": "Cartera seleccionada por el gestor desde el registro de fondos disponibles (01_decision_input/fondos_disponibles.json).",
        },
        "agentes_a_activar": {
            "agente_research": True,
            "agente_macro_house_view": True,
            "agente_riesgo": True,
            "agente_mandatos_asset_allocation": True,
            "agente_sintesis_comite_virtual": True,
        },
        "instrucciones_para_agentes": {
            "regla_general": "Analizar la hipótesis como apoyo al proceso de decisión, sin emitir recomendaciones automáticas ni instrucciones de ejecución.",
            "identificar_informacion_faltante": True,
            "distinguir_hechos_supuestos_estimaciones": True,
            "mantener_supervision_humana": True,
        },
        "advertencia": (
            "Este archivo define una hipótesis de análisis creada a discreción del gestor "
            "para el prototipo InvestCopilot. No constituye una recomendación de inversión "
            "ni una instrucción de ejecución. La decisión final debe ser revisada por el "
            "gestor o por el órgano correspondiente."
        ),
    }

    DECISIONES_DIR.mkdir(parents=True, exist_ok=True)

    with open(DECISIONES_DIR / f"{decision_id}.json", "w", encoding="utf-8") as f:
        json.dump(decision_data, f, ensure_ascii=False, indent=2)

    return decision_id

REGLAS_RESPUESTA_PATH = PROJECT_DIR / "00_contexto" / "03_resumen_para_agentes" / "reglas_generales_de_respuesta.md"
LIMITACIONES_PATH = PROJECT_DIR / "00_contexto" / "03_resumen_para_agentes" / "limitaciones_del_prototipo.md"
CONTEXTO_BASE_PATH = PROJECT_DIR / "00_contexto" / "03_resumen_para_agentes" / "contexto_base_para_agentes.md"

RIESGO_METRICAS_DIR = PROJECT_DIR / "04_portfolio_riesgo" / "metricas"
RIESGO_CARTERAS_DIR = PROJECT_DIR / "04_portfolio_riesgo" / "carteras"
MANDATOS_DIR = PROJECT_DIR / "05_mandatos_asset_allocation"
MANDATOS_BENCHMARK_DIR = MANDATOS_DIR / "benchmark"

# Datos reales de cartera/benchmark/métricas (los mismos que usan los agentes
# especialistas) para que el chat libre pueda anclar respuestas de riesgo y
# mandatos en cifras concretas, no solo en la narrativa ya generada.
DATOS_GROUNDING_RIESGO_MANDATOS = [
    RIESGO_CARTERAS_DIR / "cartera_real_fondmapfre_bolsa_america.csv",
    RIESGO_CARTERAS_DIR / "comparativa_modelo_vs_bam.csv",
    RIESGO_CARTERAS_DIR / "comparativa_modelo_vs_bam_pesos_sector.csv",
    RIESGO_METRICAS_DIR / "metricas_riesgo_bam_vs_escenario.csv",
    RIESGO_METRICAS_DIR / "resumen_riesgo_bam_vs_modelo.md",
    RIESGO_METRICAS_DIR / "resumen_metricas_riesgo_bam_vs_escenario.md",
    MANDATOS_DIR / "reglas_control_prototipo_bam.json",
    MANDATOS_BENCHMARK_DIR / "benchmark_stoxx_usa_900_tr_pesos_sector.csv",
    MANDATOS_BENCHMARK_DIR / "comparativa_bam_vs_stoxx_usa_900_tr_sector.csv",
]


# ============================================================
# CARGA SEGURA DE MODULOS POR RUTA EXACTA
# ============================================================

def cargar_modulo_por_ruta(nombre: str, ruta: Path):
    """
    Carga un módulo Python por ruta absoluta.

    Esto evita conflictos con otros paquetes que puedan tener
    el mismo nombre en el entorno Python (p.ej. 'tools').
    """

    if not ruta.exists():
        raise FileNotFoundError(f"No se encuentra el módulo en: {ruta}")

    spec = importlib.util.spec_from_file_location(nombre, str(ruta))

    if spec is None or spec.loader is None:
        raise ImportError(f"No se ha podido crear spec para: {ruta}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


try:
    mcp_tools = cargar_modulo_por_ruta("investcopilot_mcp_tools", TOOLS_PATH)

    listar_tools_disponibles = mcp_tools.listar_tools_disponibles
    leer_json = mcp_tools.leer_json
    ejecutar_orquestador_decision_001 = mcp_tools.ejecutar_orquestador_decision_001
    validar_estructura_proyecto = mcp_tools.validar_estructura_proyecto
    resumen_rapido_decision_001 = mcp_tools.resumen_rapido_decision_001
    calcular_escenario_riesgo_sectorial = mcp_tools.calcular_escenario_riesgo_sectorial
    calcular_escenario_riesgo_multisector = mcp_tools.calcular_escenario_riesgo_multisector
    calcular_escenario_renta_fija = mcp_tools.calcular_escenario_renta_fija
    # Nota: las tools de cálculo las usan ahora los agentes durante el orquestador.
    # El chat es Q&A puro sobre los outputs ya generados — no relanza cálculos.

except Exception as e:
    st.error(
        "No se han podido cargar las tools MCP desde la ruta exacta:\n\n"
        f"{TOOLS_PATH}\n\n"
        f"Error: {e}"
    )
    st.stop()


try:
    investcopilot_llm_client = cargar_modulo_por_ruta("investcopilot_llm_client", LLM_CLIENT_PATH)

    llm_call = investcopilot_llm_client.call_llm
    llm_build_context_from_files = investcopilot_llm_client.build_context_from_files
    llm_get_mode = investcopilot_llm_client.get_llm_mode

except Exception as e:
    llm_call = None
    llm_build_context_from_files = None
    llm_get_mode = lambda: "mock"
    st.warning(
        "No se ha podido cargar llm_client.py. El chat libre funcionará en modo limitado.\n\n"
        f"Error: {e}"
    )

# APP STREAMLIT - INVESTCOPILOT CHAT DEMO
# ============================================================
#
# Guarda este archivo en:
# 09_web_app_chat/app.py
#
# Ejecuta desde PowerShell:
#
# cd "<ruta_repo>\09_web_app_chat"
# & C:/Python314/python.exe -m streamlit run app.py
#
# Esta app crea una interfaz tipo ChatGPT para consultar:
# - outputs de agentes (incluido Research, el 5o agente);
# - sintesis final;
# - resumen rapido;
# - orquestador;
# - tools MCP locales (incluye calculo real de escenarios de riesgo
#   sectorial equity y de renta fija via function calling).
#
# El modo LLM depende de INVESTCOPILOT_LLM_MODE (.env). Con vertex_ai,
# las preguntas libres del chat llaman de verdad al LLM, con tools.
#
# ============================================================




# ============================================================
# CONFIGURACION STREAMLIT
# ============================================================

st.set_page_config(
    page_title="InvestCopilot",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>
    /* ── Reset Streamlit chrome ── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* visibility:hidden (no display:none) — permite que los hijos lo anulen.
       Con display:none el nodo desaparece del DOM y el botón de expand sidebar
       queda inaccesible aunque tenga visibility:visible propio. */
    [data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }
    [data-testid="stToolbar"] { visibility: hidden !important; }
    .block-container { padding-top: 1.5rem !important; }

    /* Botón de re-expandir sidebar: hijo de stHeader, anula visibility:hidden del padre */
    [data-testid="collapsedControl"] {
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        position: fixed !important;
        top: 50% !important;
        left: 0 !important;
        transform: translateY(-50%) !important;
        z-index: 9999 !important;
        background: #B71C2A !important;
        color: white !important;
        padding: 12px 6px !important;
        border-radius: 0 8px 8px 0 !important;
        box-shadow: 2px 0 8px rgba(0,0,0,0.3) !important;
        cursor: pointer !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: white !important;
    }

    /* Ocultar el botón de colapso del sidebar — demo sin distracciones */
    [data-testid="stSidebarCollapseButton"] { display: none !important; }

    /* ── Sidebar dark ── */
    [data-testid="stSidebar"] {
        background-color: #B71C2A !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding: 0 !important;
    }
    [data-testid="stSidebar"] * {
        color: rgba(255,255,255,0.85) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
        margin: 0.5rem 0 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: rgba(255,255,255,0.85) !important;
        border-radius: 6px !important;
        text-align: left !important;
        font-size: 0.875rem !important;
        padding: 0.4rem 0.75rem !important;
        transition: background 0.15s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.12) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: #6366f1 !important;
        border-color: #6366f1 !important;
        color: white !important;
    }

    /* ── Main area ── */
    .main { background-color: #f8f9fb !important; }

    /* ── Breadcrumb ── */
    .ic-breadcrumb {
        font-size: 0.8rem;
        color: #6b7280;
        margin-bottom: 0.1rem;
    }
    .ic-breadcrumb span { margin: 0 0.3rem; }

    /* ── Page header ── */
    .ic-page-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #111827;
        margin: 0 0 0.1rem 0;
    }
    .ic-page-subtitle {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }

    /* ── New decision card ── */
    .ic-form-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .ic-form-title {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.75rem;
    }

    /* ── Primary button ── */
    .stButton > button[kind="primary"] {
        background: #6366f1 !important;
        border: none !important;
        border-radius: 6px !important;
        color: white !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #4f46e5 !important;
    }

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        margin-bottom: 0.4rem !important;
        background: white !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stChatMessage"][data-testid*="user"] {
        background: #eef2ff !important;
        border-color: #c7d2fe !important;
    }

    /* ── Scenario proposal card ── */
    .ic-scenario-card {
        background: #fffbeb;
        border: 1px solid #fcd34d;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
    }
    .ic-scenario-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #92400e;
        margin-bottom: 0.4rem;
    }

    /* ── Badge ── */
    .ic-badge {
        display: inline-block;
        background: #e0e7ff;
        color: #4338ca;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        margin-left: 0.5rem;
        vertical-align: middle;
    }

    /* ── Status indicator ── */
    .ic-status-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #10b981;
        margin-right: 0.4rem;
        vertical-align: middle;
    }

    /* ── Sidebar nav item ── */
    .ic-nav-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.45rem 1rem;
        border-radius: 6px;
        margin: 0.1rem 0.5rem;
        cursor: pointer;
        font-size: 0.875rem;
        color: rgba(255,255,255,0.75);
        transition: background 0.15s;
    }
    .ic-nav-item:hover { background: rgba(255,255,255,0.08); }
    .ic-nav-item.active {
        background: rgba(99,102,241,0.25);
        color: white;
    }
    .ic-nav-icon { font-size: 1rem; width: 1.25rem; text-align: center; }

    /* ── Divider ── */
    .ic-divider {
        height: 1px;
        background: rgba(255,255,255,0.08);
        margin: 0.5rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# UTILIDADES
# ============================================================

def tool_data(response: dict):
    if not isinstance(response, dict):
        return None

    if response.get("status") != "success":
        return None

    return response.get("data")


def pretty_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def normalizar(texto: str) -> str:
    if texto is None:
        return ""

    texto = texto.lower().strip()
    texto = texto.replace("á", "a")
    texto = texto.replace("é", "e")
    texto = texto.replace("í", "i")
    texto = texto.replace("ó", "o")
    texto = texto.replace("ú", "u")
    texto = texto.replace("ü", "u")
    texto = texto.replace("ñ", "n")

    return texto


def bullets(items):
    if not items:
        return "- No disponible"

    return "\n".join([f"- {x}" for x in items])


def leer_json_contenido(ruta: str) -> dict:
    response = leer_json(ruta)
    data = tool_data(response)

    if not data:
        return {}

    return data.get("contenido", {})


def leer_json_real_con_fallback(ruta_llm_data: str, ruta_script: str) -> dict:
    """
    Lee el output real (LLM) de un agente, con fallback al output
    determinista en modo script si el LLM no devolvió un bloque JSON
    parseable en esa pasada (puede ocurrir: el modelo no es 100%
    consistente generando el bloque ```json``` junto al markdown).
    """
    data = leer_json_contenido(ruta_llm_data)

    if data:
        return data

    return leer_json_contenido(ruta_script)


def leer_sintesis_json() -> dict:
    decision_id = decision_id_actual()
    data = leer_json_real_con_fallback(
        f"06_sintesis_comite/{decision_id}_sintesis_llm_data.json",
        f"06_sintesis_comite/{decision_id}_sintesis.json",
    )
    if data:
        return data
    # Fallback: el LLM produjo markdown pero no bloque JSON parseable → leer el .md
    md_path = PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm.md"
    if md_path.exists():
        return {"_texto_libre": md_path.read_text(encoding="utf-8")}
    return {}


def leer_macro_json() -> dict:
    decision_id = decision_id_actual()
    return leer_json_real_con_fallback(
        f"03_macro_houseview/outputs_macro/{decision_id}_macro_llm_data.json",
        f"03_macro_houseview/outputs_macro/{decision_id}_macro.json",
    )


def leer_research_json() -> dict:
    # Sin fallback a script: Research Agent no tiene modo script (ver research_agent.py).
    decision_id = decision_id_actual()
    return leer_json_contenido(f"02_research/outputs_research/{decision_id}_research_llm_data.json")


def leer_riesgo_json() -> dict:
    decision_id = decision_id_actual()
    data = leer_json_real_con_fallback(
        f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm_data.json",
        f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo.json",
    )
    if not data:
        md_path = PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm.md"
        if md_path.exists():
            return {"_texto_libre": md_path.read_text(encoding="utf-8")}
    return data


def leer_mandatos_json() -> dict:
    decision_id = decision_id_actual()
    data = leer_json_real_con_fallback(
        f"05_mandatos_asset_allocation/outputs_mandatos/{decision_id}_mandatos_llm_data.json",
        f"05_mandatos_asset_allocation/outputs_mandatos/{decision_id}_mandatos.json",
    )
    if not data:
        md_path = PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm.md"
        if md_path.exists():
            return {"_texto_libre": md_path.read_text(encoding="utf-8")}
    return data


# ============================================================
# RESPUESTAS PREDEFINIDAS
# ============================================================

def respuesta_resumen_decision() -> str:
    decision_id = decision_id_actual()

    # Primero intenta el resumen estructurado (vía tools.py)
    response = resumen_rapido_decision_001(decision_id=decision_id)
    data = tool_data(response)

    # El MCP tool devuelve texto_libre (sin guion bajo) cuando no hay JSON parseable
    if not data or data.get("texto_libre"):
        texto = (data or {}).get("texto_libre", "")
        if not texto:
            sintesis = leer_sintesis_json()
            texto = sintesis.get("_texto_libre", "")
        if texto:
            return f"## Resumen de {decision_id}\n\n{texto}"
        return f"No he podido leer el resumen rápido de {decision_id}. Ejecuta el flujo completo primero."

    hipotesis = data.get("hipotesis", "No disponible")
    clasificacion = data.get("clasificacion_consolidada", "No disponible")
    resumen = data.get("resumen_clasificacion", "No disponible")
    conclusion = data.get("conclusion", "No disponible")

    alertas = data.get("alertas_consolidadas", [])
    faltante = data.get("informacion_faltante_consolidada", [])
    preguntas = data.get("preguntas_revision_humana", [])

    return f"""## Resumen de {decision_id}

**Hipótesis analizada**

{hipotesis}

**Clasificación consolidada**

`{clasificacion}`

**Lectura ejecutiva**

{resumen}

**Conclusión**

{conclusion}

### Alertas principales

{bullets(alertas[:10])}

### Información faltante relevante

{bullets(faltante[:10])}

### Preguntas para revisión humana

{bullets(preguntas[:8])}

---

**Mensaje clave:** InvestCopilot analiza. La persona decide.
"""


def respuesta_research() -> str:
    data = leer_research_json()

    if not data:
        return (
            "No he podido leer el output JSON del Research Agent. "
            "Puede que aún no se haya ejecutado para este caso — prueba con `Ejecuta el flujo completo`."
        )

    tesis = data.get("tesis_inversion", "No disponible")
    argumentos = data.get("argumentos_a_favor", [])
    en_contra = data.get("argumentos_en_contra", [])
    catalizadores = data.get("catalizadores", [])
    riesgos = data.get("riesgos_cualitativos", [])
    faltante = data.get("informacion_faltante", [])
    conclusion = data.get("conclusion", "No disponible")

    return f"""## Visión del Research Agent

**Tesis de inversión**

{tesis}

### Argumentos a favor

{bullets(argumentos)}

### Argumentos en contra

{bullets(en_contra)}

### Catalizadores

{bullets(catalizadores)}

### Riesgos cualitativos

{bullets(riesgos)}

### Información adicional necesaria

{bullets(faltante)}

### Conclusión cualitativa

{conclusion}
"""


def respuesta_macro() -> str:
    data = leer_macro_json()

    if not data:
        return "No he podido leer el output JSON del Agente Macro."

    clasificacion = data.get("clasificacion_macro", "No disponible")
    escenario = data.get("escenario_central", "No disponible")
    argumentos = data.get("argumentos_a_favor", [])
    riesgos = data.get("riesgos_macro", [])
    conclusion = data.get("conclusion", "No disponible")
    alertas = data.get("alertas", [])

    return f"""## Visión del Agente Macro / House View

**Clasificación macro**

`{clasificacion}`

**Escenario central**

{escenario}

### Argumentos a favor

{bullets(argumentos)}

### Riesgos macro

{bullets(riesgos)}

### Alertas

{bullets(alertas)}

### Conclusión macro

{conclusion}
"""


def respuesta_riesgo() -> str:
    data = leer_riesgo_json()

    if not data:
        return "No he podido leer el output del Agente Riesgo. Ejecuta el flujo completo primero."

    if data.get("_texto_libre"):
        return f"## Visión del Agente Riesgo\n\n{data['_texto_libre']}"

    resultado = data.get("resultado", "No disponible")
    cartera = data.get("cartera", "No disponible")
    escenario = data.get("escenario", "No disponible")
    lectura = data.get("lectura_principal", "No disponible")
    alertas = data.get("alertas", [])
    faltante = data.get("informacion_faltante", [])

    # Tabla de métricas cuantitativas (disponible cuando el agente llamó a la tool de cálculo)
    metricas_str = ""
    metricas = data.get("metricas", {})
    if metricas:
        actual = metricas.get("bam_actual", {})
        escenario_m = None
        # La clave del escenario varía según el sector calculado — buscar la que no sea "bam_actual" ni "diferencia"
        for k, v in metricas.items():
            if k not in ("bam_actual",) and "diferencia" not in k and isinstance(v, dict):
                escenario_m = v
                break
        diferencia = metricas.get("diferencia_escenario_menos_actual", {})

        def pct(v):
            if v is None or v == "No disponible":
                return "—"
            try:
                return f"{float(v)*100:.2f}%"
            except Exception:
                return str(v)

        def pp(v):
            if v is None:
                return "—"
            try:
                val = float(v) * 100
                return f"{val:+.2f} p.p."
            except Exception:
                return str(v)

        def fmt(v):
            if v is None:
                return "—"
            try:
                return f"{float(v):.4f}"
            except Exception:
                return str(v)

        if escenario_m:
            metricas_str = f"""
### Métricas cuantitativas calculadas

| Métrica | BAM actual | Escenario | Diferencia |
|---|---|---|---|
| Volatilidad anual | {pct(actual.get("volatilidad_anualizada"))} | {pct(escenario_m.get("volatilidad_anualizada"))} | {pp(diferencia.get("volatilidad_anualizada"))} |
| VaR 95% anual | {pct(actual.get("var_historico_anualizado_95"))} | {pct(escenario_m.get("var_historico_anualizado_95"))} | {pp(diferencia.get("var_historico_anualizado_95"))} |
| Tracking Error | {pct(actual.get("tracking_error_anualizado"))} | {pct(escenario_m.get("tracking_error_anualizado"))} | {pp(diferencia.get("tracking_error_anualizado"))} |
| Máx. Drawdown | {pct(actual.get("max_drawdown"))} | {pct(escenario_m.get("max_drawdown"))} | {pp(diferencia.get("max_drawdown"))} |
| Beta vs benchmark | {fmt(actual.get("beta_vs_benchmark"))} | {fmt(escenario_m.get("beta_vs_benchmark"))} | {fmt(diferencia.get("beta_vs_benchmark"))} |
"""

    return f"""## Visión del Agente Riesgo

**Resultado**

`{resultado}`

**Cartera**

{cartera}

**Escenario**

{escenario}

**Lectura principal**

{lectura}
{metricas_str}
### Alertas de riesgo

{bullets(alertas)}

### Información faltante

{bullets(faltante)}
"""


def respuesta_mandatos() -> str:
    data = leer_mandatos_json()

    if not data:
        return "No he podido leer el output del Agente Mandatos. Ejecuta el flujo completo primero."

    if data.get("_texto_libre"):
        return f"## Visión del Agente Mandatos / Asset Allocation\n\n{data['_texto_libre']}"

    fondo = data.get("fondo", "No disponible")
    benchmark = data.get("benchmark", "No disponible")

    # Resultado: puede venir del campo top-level (script mode) o dentro de analisis_sectorial (LLM mode)
    analisis = data.get("analisis_sectorial", {})
    # El LLM puede usar alerta_prototipo_sectorial (dict o str) o alerta_actual_prototipo (str)
    _alerta_prot_raw = analisis.get("alerta_prototipo_sectorial", {})
    alerta_prot = _alerta_prot_raw if isinstance(_alerta_prot_raw, dict) else {}
    alerta_prot_str = _alerta_prot_raw if isinstance(_alerta_prot_raw, str) else ""
    alerta_actual_str = analisis.get("alerta_actual_prototipo", "")
    resultado = (
        data.get("resultado_preliminar")
        or alerta_prot.get("clasificacion")
        or alerta_prot_str
        or alerta_actual_str
        or (data.get("alertas_mandatos") or [{}])[0].get("nivel_alerta", "")
        or "No disponible"
    )

    # Datos del sector analizado — solo si hay análisis sectorial real
    sector = analisis.get("sector_analizado")
    _tiene_analisis_sectorial = bool(sector)
    sector = sector or ""
    peso_actual = (analisis.get("peso_actual_bam_pct") or analisis.get("peso_bam_actual_pct")
                   or data.get("peso_it_actual_bam"))
    peso_escenario = (analisis.get("peso_escenario_bam_pct") or analisis.get("peso_bam_escenario_pct")
                      or data.get("peso_it_escenario_bam"))
    peso_benchmark = (analisis.get("peso_benchmark_pct") or analisis.get("peso_benchmark_actual_pct")
                      or data.get("peso_benchmark_tecnologia"))
    desv_actual = analisis.get("desviacion_actual_pp") or data.get("desviacion_it_actual_vs_benchmark")
    desv_escenario = analisis.get("desviacion_escenario_pp") or data.get("desviacion_it_escenario_vs_benchmark")
    alerta_comentario = alerta_prot.get("comentario", "") or analisis.get("impacto_hipotesis", "") or alerta_prot_str

    def fmt_pct(v):
        try:
            return f"{float(v):.2f}%"
        except Exception:
            return str(v)

    def fmt_pp(v):
        try:
            return f"{float(v):+.2f} p.p."
        except Exception:
            return str(v)

    alertas = data.get("alertas", [])
    # LLM mode usa informacion_no_disponible; script mode usa informacion_faltante
    faltante = data.get("informacion_faltante") or data.get("informacion_no_disponible", [])

    # Validación de la regla real conocida (puede ser string o dict)
    validacion_raw = data.get("validacion_regla_real_conocida") or data.get("validacion_regla_conocida", {})
    if isinstance(validacion_raw, dict):
        # LLM mode: dict de reglas
        validacion_lines = []
        for regla, detalle in validacion_raw.items():
            if isinstance(detalle, dict):
                compatible = "✅" if detalle.get("compatible") else "⚠️"
                comentario = detalle.get("comentario", "")
                validacion_lines.append(f"{compatible} **{regla}**: {comentario}")
            else:
                validacion_lines.append(f"- {regla}: {detalle}")
        validacion_str = "\n".join(validacion_lines) if validacion_lines else str(validacion_raw)
    else:
        validacion_str = str(validacion_raw) if validacion_raw else "No disponible"

    return f"""## Visión del Agente Mandatos / Asset Allocation

**Resultado preliminar**

`{resultado}`

**Fondo**

{fondo}

**Benchmark**

{benchmark}

**Validación de la regla real conocida**

{validacion_str}

{f'''### Datos clave — sector {sector}

| | BAM actual | Escenario | Desviación vs benchmark |
|---|---|---|---|
| **{sector}** | {fmt_pct(peso_actual)} | {fmt_pct(peso_escenario)} | actual {fmt_pp(desv_actual)} → escenario {fmt_pp(desv_escenario)} |

{"> ⚠️ " + alerta_comentario if alerta_comentario else ""}
''' if _tiene_analisis_sectorial else ""}
### Alertas

{bullets(alertas) if alertas else "_Sin alertas en el formato disponible._"}

### Información no disponible para validación completa

{bullets(faltante)}

---

**Nota:** esta validación es preliminar porque no se dispone del mandato completo ni de todos los límites oficiales.
"""


def respuesta_sintesis() -> str:
    data = leer_sintesis_json()

    if not data:
        return "No he podido leer el output del Agente Síntesis. Ejecuta el flujo completo primero."

    if data.get("_texto_libre"):
        return f"## Síntesis / Comité Virtual\n\n{data['_texto_libre']}"

    clasificacion = data.get("clasificacion_consolidada", "No disponible")
    resumen = data.get("resumen_clasificacion", "No disponible")
    acuerdo = data.get("puntos_acuerdo", [])
    tensiones = data.get("tensiones", [])
    alertas = data.get("alertas_consolidadas", [])
    conclusion = data.get("conclusion", "No disponible")

    return f"""## Síntesis / Comité Virtual

**Clasificación consolidada**

`{clasificacion}`

**Resumen**

{resumen}

### Puntos de acuerdo entre agentes

{bullets(acuerdo)}

### Tensiones detectadas

{bullets(tensiones)}

### Alertas consolidadas

{bullets(alertas[:12])}

### Conclusión

{conclusion}
"""


def respuesta_informacion_faltante() -> str:
    data = leer_sintesis_json()

    if not data:
        return "No he podido leer la síntesis para extraer la información faltante."

    if data.get("_texto_libre"):
        return f"## Síntesis completa de {decision_id_actual()}\n\n{data['_texto_libre']}"

    faltante = data.get("informacion_faltante_consolidada", [])

    return f"""## Información faltante consolidada

Para validar completamente la hipótesis haría falta revisar:

{bullets(faltante)}

---

**Lectura:** el prototipo separa claramente lo que sabemos, lo que asumimos y lo que debe validar una persona.
"""


def respuesta_preguntas_gestor() -> str:
    data = leer_sintesis_json()

    if not data:
        return "No he podido leer la síntesis para extraer las preguntas de revisión humana."

    if data.get("_texto_libre"):
        return f"## Síntesis completa de {decision_id_actual()}\n\n{data['_texto_libre']}"

    preguntas = data.get("preguntas_revision_humana", [])

    return f"""## Preguntas para el gestor o comité

Antes de avanzar con la hipótesis, convendría revisar:

{bullets(preguntas)}

---

**Objetivo:** InvestCopilot no cierra la decisión; prepara mejor la conversación de inversión.
"""


def respuesta_alertas() -> str:
    data = leer_sintesis_json()

    if not data:
        return "No he podido leer la síntesis para extraer las alertas."

    if data.get("_texto_libre"):
        return f"## Síntesis completa de {decision_id_actual()}\n\n{data['_texto_libre']}"

    alertas = data.get("alertas_consolidadas", [])

    return f"""## Alertas consolidadas de {decision_id_actual()}

{bullets(alertas)}

---

**Lectura ejecutiva:** las alertas no implican necesariamente rechazo o incumplimiento; indican puntos que requieren revisión humana.
"""


def respuesta_estructura() -> str:
    response = validar_estructura_proyecto()
    data = tool_data(response)

    if not data:
        return f"No he podido validar la estructura del proyecto.\n\nJSON de error:\n{pretty_json(response)}"

    estructura_ok = data.get("estructura_ok")
    faltantes = data.get("faltantes", [])

    if estructura_ok:
        return """## Validación de estructura

La estructura principal del proyecto está correcta.

`estructura_ok = true`

No se detectan rutas clave faltantes en la validación básica.
"""

    return f"""## Validación de estructura

Se han detectado rutas faltantes:

{bullets(faltantes)}
"""


def respuesta_tools() -> str:
    response = listar_tools_disponibles()
    data = tool_data(response)

    if not data:
        return f"No he podido listar las tools.\n\nJSON de error:\n{pretty_json(response)}"

    tools = data.get("tools", [])

    return f"""## Tools MCP disponibles

{bullets(tools)}

Estas tools permiten consultar archivos, outputs, estructura y ejecutar el orquestador del prototipo.
"""


def _leer_progreso_orquestador(decision_id: str) -> dict:
    path = _orchestrator_progress_path(decision_id)

    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _render_progreso(progreso: dict) -> str:
    iconos = {"pending": "⏳", "running": "🔄", "success": "✅", "error": "❌"}
    lineas = []

    for agent_key, label in AGENT_LABELS.items():
        estado = progreso.get(agent_key, "pending")
        icono = iconos.get(estado, "⏳")
        lineas.append(f"{icono} {label}")

    return " · ".join(lineas)


def respuesta_ejecutar_flujo(placeholder=None, decision_id: str | None = None) -> str:
    """
    Lanza el orquestador para decision_id (por defecto, la decisión activa
    en la sesión) y, si se le pasa un placeholder de Streamlit, actualiza en
    vivo qué agente va corriendo (en vez de un spinner ciego durante los
    ~1-3 min que puede tardar el flujo completo).
    """

    decision_id = decision_id or decision_id_actual()

    if not ORCHESTRATOR_PATH.exists():
        return "No se encuentra el orquestador en el proyecto."

    progress_path = _orchestrator_progress_path(decision_id)
    summary_json_path = _orchestrator_summary_json(decision_id)
    summary_md_path = _orchestrator_summary_md(decision_id)

    # Limpiar progreso de una ejecución anterior para no mostrar estados viejos.
    if progress_path.exists():
        progress_path.unlink()

    inicio = time.time()
    timeout_segundos = 600

    # El subproceso escribe sus logs a un FICHERO, no a un PIPE.
    # Con stdout=PIPE y sin drenar el pipe en el bucle, el buffer del SO (~64KB)
    # se llena con los logs JSON de los 5 agentes y el subproceso se BLOQUEA al
    # escribir el siguiente log → poll() nunca devuelve → cuelgue hasta el timeout,
    # aunque todos los agentes hayan terminado. Redirigir a fichero lo elimina
    # (los ficheros no tienen ese límite de buffer) y deja un log persistente.
    run_log_path = ORCHESTRATOR_DIR / f"run_{decision_id}.log"
    log_fh = open(run_log_path, "w", encoding="utf-8", errors="ignore")

    proceso = subprocess.Popen(
        [sys.executable, str(ORCHESTRATOR_PATH), "--decision-id", decision_id],
        cwd=str(PROJECT_DIR),
        stdout=log_fh,
        stderr=subprocess.STDOUT,
    )

    try:
        while proceso.poll() is None:
            if time.time() - inicio > timeout_segundos:
                proceso.kill()
                proceso.wait(timeout=10)
                return f"El orquestador no terminó en {timeout_segundos // 60} minutos y se ha cancelado. Puede ser un problema de red con el LLM."

            if placeholder is not None:
                progreso = _leer_progreso_orquestador(decision_id)
                placeholder.markdown(
                    f"Ejecutando flujo {decision_id} ({round(time.time() - inicio)}s)...\n\n{_render_progreso(progreso)}"
                )

            time.sleep(1)
    finally:
        log_fh.close()

    if placeholder is not None:
        placeholder.empty()

    if not summary_json_path.exists():
        salida = run_log_path.read_text(encoding="utf-8", errors="ignore") if run_log_path.exists() else ""
        return f"El orquestador terminó sin generar resumen. Salida:\n\n```\n{salida[-2000:]}\n```"

    with open(summary_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    status = data.get("status", "No disponible")
    message = data.get("message", "No disponible")
    agents = data.get("agents_executed", [])
    results = data.get("results", [])
    duracion = round(time.time() - inicio, 1)

    if status == "success":
        st.session_state["show_post_exec_actions"] = True

    # Detectar agentes con error para F3-C
    failed = [r for r in results if r.get("status") == "error"]
    succeeded = [r for r in results if r.get("status") == "success"]

    if status == "success":
        agent_summary = f"✅ {len(succeeded)}/{len(results)} agentes completados correctamente."
    elif failed:
        lines = [f"⚠️ {len(succeeded)}/{len(results)} agentes completados. Fallos:"]
        for r in failed:
            agent_name = r.get("agent", "agente desconocido")
            err_msg = r.get("message") or r.get("error") or "sin detalle"
            lines.append(f"\n- **{agent_name}**: {err_msg}")
        lines.append("\n\nPuede reintentar desde el formulario «Nueva decisión». Si el error persiste, revise las credenciales de Vertex AI.")
        agent_summary = "\n".join(lines)
    else:
        agent_summary = f"Estado: `{status}` — {message}"

    return f"""## Ejecución del flujo completo ({decision_id})

{agent_summary}

_(completado en {duracion}s)_
"""


CHAT_LIBRE_SYSTEM_PROMPT = """Eres el asistente conversacional de InvestCopilot, un prototipo de copiloto de
análisis de inversión multiagente. Respondes preguntas de un gestor sobre los
resultados ya generados por los agentes especializados (Research, Macro, Riesgo,
Mandatos, Síntesis) para el caso de inversión activo.

Reglas que debes seguir siempre:

1. Apoyas el análisis, no tomas decisiones. La decisión final es siempre humana.
2. No emitas órdenes de compra, venta, suscripción, reembolso o ejecución.
3. No presentes tu respuesta como una recomendación automática de inversión.
4. Diferencia hechos, estimaciones, supuestos y opiniones analíticas.
5. Si la pregunta excede la información disponible en el contexto, dilo
   explícitamente en vez de inventar datos, métricas o límites.
6. Cierra con un recordatorio breve de que el análisis requiere revisión humana
   cuando la respuesta tenga implicaciones de inversión.
7. Para preguntas de mandatos o límites, usa los pesos y desviaciones reales
   del contexto (cartera, benchmark STOXX USA 900 TR, reglas de control).
8. DETECCIÓN DE ESCENARIO REFINADO: Si la pregunta del gestor implica un escenario
   diferente al analizado (distinto sector, distinto delta en p.p., distinta fuente
   de financiación, distinto fondo, u otra variación de hipótesis), responde la
   pregunta con los datos disponibles y añade AL FINAL —en una línea propia— el
   marcador exacto:
   [PROPUESTA_ESCENARIO:{"hipotesis":"<texto completo de la hipótesis refinada>","notas":"<por qué difiere del escenario actual>"}]
   No incluyas este marcador si la pregunta es solo una consulta sobre los resultados
   ya calculados. Solo cuando el gestor plantea una variación que requeriría recalcular.

Responde en español, de forma clara y profesional, sin formato JSON ni bloques
de código innecesarios (excepto el marcador [PROPUESTA_ESCENARIO:...] cuando aplique)."""


def respuesta_libre(user_question: str) -> str:
    """
    Responde preguntas libres llamando al LLM real con el contexto completo
    de la decisión activa (outputs de los agentes + reglas de respuesta del
    prototipo). Si no hay LLM real disponible (modo mock, error, o
    llm_client no cargado), cae a una respuesta de apoyo basada en el
    resumen estructurado y deja claro por qué.
    """

    decision_id = decision_id_actual()

    resumen = resumen_rapido_decision_001(decision_id=decision_id)
    data = tool_data(resumen)
    respuesta_base = data.get("resumen_clasificacion", "") if data else ""
    conclusion = data.get("conclusion", "") if data else ""

    comandos_disponibles = """- `Resume la decisión`
- `Qué dice Research`
- `Qué dice Macro`
- `Qué dice Riesgo`
- `Qué dice Mandatos`
- `Dame la síntesis`
- `Qué alertas hay`
- `Qué información falta`
- `Qué preguntas debe revisar el gestor`
- `Ejecuta el flujo completo`
- `Valida la estructura`
- `Qué tools MCP hay`"""

    if llm_call is None or llm_build_context_from_files is None:
        return f"""## Respuesta de InvestCopilot

No se ha podido cargar el cliente LLM en esta interfaz, así que respondo con el resumen estructurado del prototipo.

Tu pregunta ha sido:

> {user_question}

Para esta versión de demo, también puedes preguntarme con comandos directos:

{comandos_disponibles}

### Resumen actual de {decision_id}

{respuesta_base}

### Conclusión actual

{conclusion}
"""

    contexto = llm_build_context_from_files(
        files=[
            decision_file_path(decision_id),
            PROJECT_DIR / "02_research" / "outputs_research" / f"{decision_id}_research_llm_data.json",
            PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro_llm_data.json",
            PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm_data.json",
            PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm_data.json",
            PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm_data.json",
            *DATOS_GROUNDING_RIESGO_MANDATOS,
            REGLAS_RESPUESTA_PATH,
            LIMITACIONES_PATH,
        ],
        title=f"Contexto {decision_id} para chat libre",
        max_chars_per_file=4000,
    )

    # Historial reciente: últimos 6 mensajes antes del actual (el actual es el último)
    _hist_msgs = st.session_state.messages[:-1][-6:]
    _hist_lines = []
    for _m in _hist_msgs:
        _rol = "Gestor" if _m["role"] == "user" else "InvestCopilot"
        _txt = _m["content"][:500].replace("\n", " ").strip()
        _hist_lines.append(f"{_rol}: {_txt}")
    _historial_ctx = (
        "## Historial reciente de conversación\n" + "\n".join(_hist_lines) + "\n\n"
        if _hist_lines else ""
    )

    llm_mode = llm_get_mode()

    respuesta = llm_call(
        system_prompt=CHAT_LIBRE_SYSTEM_PROMPT,
        user_context=f"{_historial_ctx}## Pregunta actual del gestor\n{user_question}\n\n{contexto}",
        mode=llm_mode,
        temperature=0.3,
        max_tokens=2000,
        max_context_chars=45000,
    )

    if respuesta.get("status") == "success":
        texto = respuesta.get("data", {}).get("response_text", "").strip()
        nota_tool = ""

        if llm_mode == "mock":
            return f"""## Respuesta de InvestCopilot (modo mock)

El LLM está en modo `mock` (no se ha llamado a ningún modelo real), así que esta no es una respuesta real a tu pregunta.

Tu pregunta ha sido:

> {user_question}

Para ver respuestas reales, activa `INVESTCOPILOT_LLM_MODE=vertex_ai` en el `.env`. Mientras tanto, comandos directos disponibles:

{comandos_disponibles}

### Resumen actual de {decision_id}

{respuesta_base}
"""

        # Detectar marcador de escenario refinado
        import re as _re
        _match = _re.search(r'\[PROPUESTA_ESCENARIO:(\{.*?\})\]', texto, _re.DOTALL)
        if _match:
            try:
                propuesta = json.loads(_match.group(1))
                st.session_state["pending_scenario"] = propuesta
            except Exception:
                pass
            texto = texto[:_match.start()].strip()

        return f"""## Respuesta de InvestCopilot

{texto}
{nota_tool}

---

*Generado por Vertex AI ({llm_mode}) a partir de los outputs de {decision_id}. También puedes usar comandos directos como `Qué dice Riesgo` o `Dame la síntesis`.*
"""

    return f"""## Respuesta de InvestCopilot

No he podido obtener una respuesta del LLM ({llm_mode}) para tu pregunta.

> {user_question}

Detalle del error: {respuesta.get('message', 'No disponible')}

Mientras tanto, puedes usar comandos directos:

{comandos_disponibles}

### Resumen actual de {decision_id}

{respuesta_base}
"""


_CONECTORES_CONVERSACIONALES = [
    "por que", "porque", "como", "cuando", "quien", "cual", "cuales",
    "aplica", "deberia", "podria", "habria", "tienes en cuenta", "no aplicas",
    "no usa", "no tiene", "por tanto", "entonces", "ademas", "sin embargo",
    "a pesar", "teniendo en cuenta", "dado que", "en base", "es coherente",
    "es consistente", "tiene sentido", "explica", "explícame", "detalla",
]


def _es_comando_directo(q: str) -> bool:
    """Mensajes conversacionales largos o con conectores van al LLM."""
    palabras = q.split()
    if len(palabras) > 8:
        return False
    if any(c in q for c in _CONECTORES_CONVERSACIONALES):
        return False
    return True


def responder_pregunta(user_question: str, placeholder=None) -> str:
    q = normalizar(user_question)

    if not q:
        return f"Escribe una pregunta sobre InvestCopilot o la decisión activa ({decision_id_actual()})."

    # Comandos de ejecución siempre activos (no son conversacionales)
    if any(x in q for x in ["ejecuta", "ejecutar", "lanza", "correr flujo", "run", "orquestador"]):
        return respuesta_ejecutar_flujo(placeholder=placeholder)

    if any(x in q for x in ["validar estructura", "validacion estructura"]):
        return respuesta_estructura()

    # El resto solo se activa si el mensaje es un comando corto y directo
    if not _es_comando_directo(q):
        return respuesta_libre(user_question)

    if any(x in q for x in ["tools", "herramientas", "mcp"]):
        return respuesta_tools()

    # Síntesis ANTES que research — "tesis" es substring de "sintesis"
    if any(x in q for x in ["sintesis", "comite"]):
        return respuesta_sintesis()

    if any(x in q for x in ["research", "catalizador", "catalizadores"]):
        return respuesta_research()

    if "tesis" in q and "sintesis" not in q:
        return respuesta_research()

    if any(x in q for x in ["macro", "house view", "escenario macro"]):
        return respuesta_macro()

    if any(x in q for x in ["riesgo", "risk", "var", "volatilidad", "drawdown", "tracking error", "beta"]):
        return respuesta_riesgo()

    if any(x in q for x in ["mandatos", "asset allocation", "stoxx"]):
        return respuesta_mandatos()

    if any(x in q for x in ["informacion faltante", "que falta", "faltante"]):
        return respuesta_informacion_faltante()

    if any(x in q for x in ["alertas", "principales riesgos"]):
        return respuesta_alertas()

    if any(x in q for x in ["resumen", "resume", "caso"]):
        return respuesta_resumen_decision()

    return respuesta_libre(user_question)


# ============================================================
# ESTADO DE SESION
# ============================================================

if "decision_id" not in st.session_state:
    st.session_state["decision_id"] = "DECISION_001"

if "pending_scenario" not in st.session_state:
    st.session_state["pending_scenario"] = None

if "show_nueva_decision" not in st.session_state:
    st.session_state["show_nueva_decision"] = False

if "show_post_exec_actions" not in st.session_state:
    st.session_state["show_post_exec_actions"] = False

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hola. Soy **InvestCopilot**, tu copiloto de análisis de inversión.\n\n"
                "Puedes lanzar una nueva hipótesis con el botón **Nueva decisión** "
                "o preguntarme directamente sobre el caso activo:\n\n"
                "- `Dame la síntesis`\n"
                "- `Qué dice Riesgo`\n"
                "- `Cuánto cambia la volatilidad`\n"
                "- `Qué alertas hay`\n\n"
                "_InvestCopilot analiza. La persona decide._"
            ),
        }
    ]


# ============================================================
# SIDEBAR — navegación
# ============================================================

_llm_mode_now = llm_get_mode()
_dec_id_now = decision_id_actual()

with st.sidebar:
    # ── Brand ──────────────────────────────────────────────
    _LOGO_B64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAMCAggHCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAcICAgICAoICAgICQkJCAgLDQoIDQgICQgBAwQEBgUGCgYGCg0NCg0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NCA0NDf/AABEIARkEAAMBIgACEQEDEQH/xAAdAAEBAAIDAQEBAAAAAAAAAAAAAQgJAgYHBQQD/8QAZxAAAgEDAgMEBgQFChEKAggHAQIDAAQRBRIGITEHCBNBCRQiUWFxIzJCgRVSkaG0JDNic3R1gpKxsxYlJjQ1NkNTY3KUorK1wdHSGERUVZPCw9PV4ZXwRVZkZaXE1OMXGUaDhKOk/8QAHQEBAAMBAQEBAQEAAAAAAAAAAAECAwQFBgcICf/EADoRAAICAAUCAwYDBgUFAAAAAAABAhEDBBIhMQVBBhNRByIyYXGBkaHBFEKx0eHwFSNSgvEzYnKSsv/aAAwDAQACEQMRAD8A2pAUoKtAKlWlAKlWlAKUpQClSlAWpSrQCpSlAWlKUApSpQFpUpQFpUpQFpUq0ApSpQFqUpQFpUpQFpUq0ApUq0ApSlAKVKUBaVKUBaVKtAKUpQClTNKAtKlKAUq0oCVaUoBSlKAVKUoC0qUoBVqUoBTFWlAKV+bUtSjgjeWZ0iijUvJJIwREVRkszMQFUDmSTisEe8Z6R5QJLThza7Z2vqk0ZMIAYh/UoWKtK2AdtxIvge0rotwtWSb4KuSXJnvStffd67/Nxaqltru66h5BNQjTNzGMD+uol5XCg7j4kKLIBgeHKcuc7+GOKba/gS5tJo7iCQZSWJgyN8MjoR5qcEHkQKOLQjJPg+pilKVUsWpSrQClKUBKtSlAWlSgoBVqVaAUpSgFKUoBSpmmaAtKlWgFKlWgFKUoBSpSgLSpmlAKtSrQClKUApSpQFpUpQFpUq0BKtKUApSlASrSpmgLSpSgLSpSgLUq0oBSlSgLSpSgLUpSgLSlKAUqVaAlR+h+Vcq4v0NAUVa41aAtKUoBSlKAlWlKAlWlSgLSpmlAWlSlAWlKUBKVaUApSpQFpUpQFpUq0BKtKUApSlAKVM0zQFpUoKAtKUoBSlKAlWpTNAWlTNKAtKlKAtKUoBSlKAUqZpmgLSpSgLSlKAVKtKAUqUzQFpUpQFpXCSUAEkgAAkknAAHMkk8gB1zWN3bF3+tC0cvDDI2p3acjBZYaJGzgia7bFuhXqyI8koGD4fMZlK+CG0uTJMmsbe3jv26PoZe3gb8J367lNtaupihcY9m6ugGjhIJGY1Esw6+HjJGB3bT3y9d1/fFJOLGzYjFpYNLFuUY9m4udwmuASDuUeDC6na0JGS3hsUYUAAAAdABgD7hWscP1MZYnoemdt/eL1biV86hOPVlcPFYQrss4mU5V9h3PNKpwRLO7lWGUEWSK80Nc91exd37ur6nxOyyWqrBp+5lk1GYZh9jIdLdAQ11KGG0hCsSkMGlVl2HbZIx5Z062TkPkP5K732XdqGoaJMZ9PuDAzkGWMgPBPgYAmiPJ8AABwVkUDCutei9u/dD1DQA88Wb3TkXcbmNcSwKBz9ahBJVQOfjR7o8AlvCwM+J265APkenyqFTRVpxZsW7Gu/Fp+o7IdQC6ddHluds2chzgbJ2x4THI9ibbzOA8mDWSkUwYBlIZSAQQQQQehBHIg+8Vpkihr1Psp7fNV0XC2lwXgB52lxult8eYRN6tCSPOF0GeZDcwc3h+htHF9TaXSseezLvo6bfbY7wNp855fSHfbMf2M4A2Z/wyxjyyayAtLxJFV42V0YZV0IZWB6EMMgj4g1i01ydCafB/apVpUEkq0qZoC0qUzQFpUpQFpSlASrSlAKUqZoC0qZpmgLSpVoBSlKAUpSgFKlM0BaVM0oC1KVaAlWlKAUqUzQFpUzTNAWpSlAWlKUBKtKlAWlTNM0BaVKUBaUpQEq0pQClKlAWlSlAWlKlAWlKUAri/Q/KuVcZOh+RoC1alWgFKUoBSlKAVKtKAlKtKAmKVaUApUzSgLSlSgFKtKAmKYq0oCYq0qUBaVM1aAVKtKAlKtKAlKVaAUpUoC0pSgJSrSgJTFKtASlWlASrUpQFqUq0BKVaUBKVaUApSpQFpSv5zzqilmIVVBZmYgKoAySSeQAHMk9KA50rynifvWcN2J23Gtaer4JEaTrNKcddsUPiSMfgqk15FxT6S3h+AH1WO/vmHIeFberqcfsrxrdsH3hDU6WVckjLOmK1t8e+k/wBTlDLpmnWVpnpLetLevjz+hhe0RW9xMsij8Vqx+7Re85r+r8rrVbtY87vBs5XsYSRnky2pjaSPn+tzPIp5ZBIBq+hlHiI2u9pXeO0PRQfX9StoZArN6ur+NdMFGTstYBJcOeY5LGeZA8xWKnad6UOMZTRtOaUk49Z1AmFAMHDpbRFpZOePZlktyASTzG06+4oAMkADJySBzJPUk+ZPvNf0Iq6gjN4jO+9rHb5rHEAZNUvpJ4GYN6mipDZLgDA9XjAEqgjcPWWnYNghsgY6CsYHQYpurtnZf2V6lrztHpVnLe7H8OWSPYtvE/LKy3MjJAjoCC0e8yAEHYdy514M+Tqtdl7POze/1m49W060mu5ftmND4UI5c552xDACCCBK6s4ztDYNZwdjfoyoU2Ta7dG4YFW9RsmeK3GMHZNckLPONwJIiW2BB2neM7sota4r0PhS0WI+q6fAiO8VrbxqJJAgLO0dvEpklbAJZ9p55LN1NUc/Q0UO7MduwD0ctnaeFda6yX90uGFlEzfg+F/2ZKxyXhU8vpVSE8j4JIBHr/b/AN7LSeFohC36ovBH9Dp1rtDKighTKw+jtYBtwC3tHGER8YGKfbT387/VIbuLSkfTLZY0Hj7gb+TfKqHDozR2q7Sw+iMkvMMJYyuDijxXbs0FuzMzu1vKzPIzPI7GaXLO7ku7seZZiWY5JJNRob3kHNLaJuV4B7VIr6KEyAQzSRoxQtlCXUNiNzjd1xtYBvga8l7be5PY6mXubEjT7xsswVc2kzEkkyQj9bcknMkO3J5sklfD4egxBB+0Q/za16Hwz2lzW+FfM0Y8mJ3qP2LnPL4Nn4EUcGt4lViKW0jAnjvse1HR3Ed/bNFk4WZcyW0h90c4AUk+SMEkxzKCvhQwVtatNcstSjaJlSVXBElvOitkeYaNsqy/Ebh8a8J7S+5LazlpdMl9TkPPwJMyWpPuT+6w5+BkQcsIOeSn6kvD7xMK7e3ruXAfHF7pbFrK5kt9x3MqYMTnlzeJw0bEgY3FN3Ic+Qr9nGXY7qWlZN5avHGDjx0Iktz7j4qZCg+QkEbZ8q+Na2labMy3Rk7wP30JRhdQtQ/+GtTtb74ZG2k/FZR/iivduEe2vTL/AAIbuMO3SKb6GXPuCS7S2Pem4e4msBLa0r6cNmPdWbgjVYjRsfBq1gnwvxzfWePAup0Uf3PeXi+6N9yD7lFeq6B3l71MCeGGce9N0L/ecuh+5FrPQzVYiMl8UryfSO8dZycpYp4T79qyL+VDu/zK7lpvaXYTY2XUXPycmM/kkCmqUy6kmdnpX87e4VwGVgynoykEHHI4I5deVf0qCwqUq0BKVaUBKYq0oCYpVpQClTNWgFSrSgJSrSgJTFKtAKUqUBaVKUApVpQEpirSgJSrSgFKlWgFKUoCUq0oCYpVpQEq1KUBaVKtASlWlASmKtKAlWlKAUpSgFKUoBXF+h+Vcq4v0PyoCilBVoBSlKAUpSgFKUoCUpVoCUFWlASlWlAKUpQEpSlAM0q0oCUq0oCYq0pQCpVqUAzQmlWgIDUrlSgJilWlAKUqUApmlKAZqZq1aAlMVaUBMUq0oBSpSgFKYq0BKVaUBKYq0oCV5j3n9S8HhzW5Pdpl4PvaB0H52r06vDu+7e+HwprR/GtRF98s0cf/AHqlckS4NPCW+K5VPEr2jur93wcVXtxam6NottbC4eRYhMzbpVjVAC6BSck7ju+rjHPNdTdHGlZ4xvri84AySAPeTgVs10H0YGhIc3V3qd3708eK2jPv520Mc4/gzgj317Dwx3VuGNJCyR6TYK0Y2i4u0W4lUfG4uzI+TjJO/JIzWetGvls1HcDdn9/qrKNOsbu9DglZLa3kkgwOR3XIX1dP4cqk4OM4NZI9n3o3ddvGDXslppsOAcM5uronzBhi2woMYwxumOcjYOpzh4s71fD2mDY1/C7Ly8GzRrlh8D6urRp/DZBXgvHfpHeTJpemktzCzX7hVHub1eBizj9iZ4ifeKapPgVFcs792Y+jy4f00rJcRy6pOvMPfODCDkMMWkQjtjtIG0ypK45+1zNd97Q+8joOgJ4MtzF4kYCpY2SrNMvUBfBi9iBeR5zGJB76158f95PXtXG26v5EjOMw2W+zgJ8wyxSGV0P4k00qnz3YFeZR2wHlj/3ppb5I118KMs+1Pv36ndT2lvpsK2Fvc+rsZXCzXjJLKUKg84YPZHVRK3Pk64BOKenySTX17PM8ks8sV6ZZpXaSVyEfG6RyWIUeyq5wqgKAAAB3IWwNzpP7VY/pL1+rhfQNzXLpCLibxZITEZRDtgl8QSSZJGT0TOcJnJFaJJcGTbfJ5zokR9XvP2uD9ISv68TQgW9py62sn89LXcIdCjjTUlRt8aiJY3/GUXSBW5ADmPMYB6+dfk4r0tTb2WP+iyfz81SVM6tEOYIP2iH+bWv3BK/Pocf0EH7TF/NrX7AetWsijgBjBBwRzBHIgjzB8iPfXdNF7S7iAhZPpk5fX5OB8H8/4Qb510ts1/a7zhD71H5uVVaTLJtcHtmkdoNpcDaXCM3IpLhc58gSSjZ92c/Cup8Y93HSr7LiI20rc/EtSIwT1yYyGhbPmdgb4155Z229lUc2LAAe855AV2dWu7KQ/TNCuchGO9SD7ozlfvAFZOFcM2WJfKPPOIe6few5NrNFcr+K30EuPgDujY/w0roOp8BXlqcT200WPtMh2f8AaKCh/jVlTpXaxk7ZI8gKSXQ7TyGT7ByOf+NXZdO49tJlJ8Tbj6yyArjPvzlcffiouS5RNRfDMLbayzX1baxrLm94J0+7BYwQPn7cYUN/Hjw35TXWr/sCs25xvNF8AwdfyOpb/PFNY8sx8gs68U7ee8ElgHsrB1a8xtlmGGS0z1UdVa6/YnIiyC2Tha9J77S3PDljb+qTbnvpnt/G2bZIEWIyMY8MR4r42h/scyBnaV18iM88nJJJJJySTzJJPMknmSeZPOrrfcze2xtp9Hzqxm4VsCxJZJtQjYklixW/uTuZjksxDAkkkkkk5zWRtYrejYus8NhP71qF6p/hssv/AIlZVVhLk6o8IUpSqliZpmlKAmatWlATFMVaUBKtKUAqUpQDNM0q0Bxq1aUBMUxVpQClKlAM0zSrQEzSlWgJSrSgJirSlAKVKUAzTNMUoBmmatKAlKtKAUpSgFTNKtATNM1alAKVaUBKCrSgFKUoBXF+hrlXF+h+VABVoBSgLSlKAUpSgFKVKAtSlMUAzTNKYoADSrSgFKUoBSpSgFM0xTFAM0zSmKAVaUoBSpSgLUzSlAM0zTFMUAzSrSgJVpSgFKlKAtTNKYoBmmaYpQDNKtKAUpUoC0qUoBmmaYpigGaZpVoCVjv6QCfbwpqX7J7Bf42oWo/krImsbfSGrnhS+/b9O/1hbVaPKKy4Zqc8Os0vRW2edT15vxLDSwPgZbjUS35fBX8lYW7DWc/orLci4158dYdKT+K+on/v10S4Zzw5O499ztW1Sy1KC1s764toDZJJJHCVTdI80y7i4XxQdqAYDhfhnnWImsyS3TiS5kkuZB0kuJHncfBWlZ2UfAECsrO+bpUMutKZLjwitjbjb4MknLxLg53IccyenXl8a8M/oWtf+mj/ACWb/fUR4IlydBWz+Fc/UK9I0fg2Bi+yQXbqhaO3CSW5kbco+ux57VJbYpDNj4HPyeJ9GWKcoikDEZKbvEMcjKpeLcPrlHJQHmT05nNWKHXNJ4SkuCwQD2V3MzMqIq5ABZ3KqMkgDJyTX8tQ4YeJ2jkUq6nBH5xgjIIIwQQSCCCOtejJYR2Mbwzx+NPOE8aDeUWBFO9Azp7XrBOGwDhByPM1+aPSJNQnZvYjVVUuxyIreGNQiliSThVUKBks7dOpwJPmDSMXOkcv7nY/pL11zUNMLTSKFLEzSAKAWJJdgAB1JPTAr0/TStxfWawKxitjbqGfAbwbeTxJJpOgQc2JHkNo5k4rhwdp+7UY28jLOwI9xSUgj8xpYo6hqlmtnDJbcnuJtnrGDlIFRg6xAjk8xYAu3NU+qMnJr8/FOn/qexyCP1LJ9/08p5e/kR9xr98GkAbTgH6p5+fmQfn5123iS4W6R0Tx5DLKJQkuCtuArAxw4Y+ydwXkEG1V5ZoQZM6LD9DDz/uMX82tfQiTnjGc5/kpoWiOYIzgAJFEGz1+ovl1P3V+3TdR9XkWRAGK/j9PMHkMfy1Yg/Fb2Tv9VSR5noPvJ5CvtXOhRrbrIZdzKzAxx4Yjz6+4eZwRzr8epytKzHPPJJQdPmo93w6/OvzxORHkcisg/wA5T/w1AOEeqGMhokCFSCG+s2R8Ty/IK+lxHrJuJWEhAdfZRui4H2W93PPtflr8yWglGUGHH1o/ePxk+XmnUdRkdOWpaQ7yysBhRI4LNhVBBxjJwM/AZPwpY7Hz7FWVpAw2lY3yD8cD/b1r+djE+4GPJb4DP5R7vnXa9Ca3EUwl+lKoqq+1gq7jgLn65Xdgk45AHAr4V5cSKSh9jH2UG1fgeX1gRzBycipsUfet+HI/AaYSeHLuGY4z7Xs9dpBz054HSvo8D8WSNcxQ75GRi4O9txOI3I65I5gdDXT7icqsQHI4Z8jkebYH5lr7PBcwe7gY+y4c5x0f2GByPJufXzrOS2Lxe6o8c9KNF/SrTH/F1Pb/ABrO5P8A3a1th62Zek7t86HZH8XVIj+W1uh/trWf4dRDgvPk2S+izvy+i6op6Ra1Ii/JtN02X/SkNZnVhP6Kkf0o1n9/W/1RpNZs1jLk3jwhSlSqli1KUoBmmaYpigGaZpSgFKtKAUpUoC1KUoBmmaYpQDNKVaAUpSgFKlKAZpmlKAZpmmKUApVpQClSlAWlSmKAZpmmKUAzSlWgJVpSgFKlKAUzSmKAZpTFKAUq0oBSlKAVxk6H5Vyri/Q/KgArlXEVyoBSpSgLUq0oBSlKAlWpmlAWlSlAWlSlAWpVpQEq0qUBalM0oC0qClAKtSrQEpVpQCpSmaAtK40oDlUpTFAWlKUApSpQFpUzTNAWlSmKAtSlKAtKUoBUpSgLSpSgLUpTFAWsfu/jZ+JwtqI9z2Lfxb+2P+ysgK8h73Fh4vDmqr1xAr/9nNG//dqVyVlwzUKmnVnV6MWEK2te/Fh/+brEhtErML0cdoEm1lffHp5/zrwVvLg5ofEfT712n2j6uTNJcB/VLcYijjZdu6bHNpFOTk55e6vHfwHYf3y8/wCxh/8AOrJbvCaBdyaiGhtY5kNvEN7W8Mp3BpMrvcFsAYOM4GfjXmp4av8A/oEP+R2//DRcEyW55t+AbA/3S7+Xgw/+dX6LSO2tsvbeM0/RJJkjVYARzeNFZw0pHIFuScyATXokfD18P+YQ/wCR2/8Aw1+lNGvx/wAwg/yK3/4akijyLR+CnuHIU4ABeWVydsafakkb7/mzchzNfWm09pytlZofBDbiW9lp3Uc7iduiIo5qp9mNfea9Ln4b1CZREbcRRlgzBIooEJHINIUxlV5n2sgdfdX4tSgjhQ29uQQ2PHnAwZiPsJ5i3U9B9s8zywKWKOnLpgOLK0ZSrZa4uW9gTbAWY56raxAEgdXxuOcjP610dbBFlR1mmmDiGVQfDijGUdgGAJnJ3JgjCDJ5kiv32GnNE6yR8mXOOQIIIIIIIIKkEggjBBr7ltw5JdsrSBVijG0LGoRFXJJVFUYGSSSepP3UIs6Xw5wA9xzxtiH1nPIcvIe813uK0tbaPbEgMnQuRn89dwms3aOOCKPYgyfdn4seQA+dczwQyj2WUlebuEJSPPLBZsKzA8uRIB9+DixXk7Xo2hyT+GEOSyrzJIx7I99W80tlZkkGGUkFlwen4wHX5jn8DX0bYnCtncq7RuaHBbH4gDJj/GJ5feAf0x26SfWjU7j7I8QqQM9QJCRjy5SgE+XWq2Wo+PqmgvGy+IyR7lVwd2c8sZAQMx5j3fkr9tsIJIZQ29pd0bBlAjDkZABzvAY7jzKjd7Pnkn9lxpKCNQrMXywMMo2MFGTuQn7Q6ZGVwQCMCvwLppCS8iRsU5x0+kTr1x1681PkeRwsUfhttU8N1McSIysMM252BB/ZnAPyVa/Zr87XLvIf1xCwZPLYpIDoPgPrqOn1uhO3+dvbmZlABMmQAQPrjI5H9mPJj1HI88Ey50mVJGJPhEOxDM20j2jggfWP3Kc02B+aIYgf9lLGP4quT/KK52X0wEJyW6ROBkqc/UYDmYif4hORyyD9m5toTArfXfe8jxplE6BC4yu4RjAyBggs2NoAx8+yuCzqoCpHkFlQbQVX2juOSzcgfrMaCjjrujeFJslYLtVAFX2mICjn+KATnmSPlX9eDQPW4Aict55sctyVvkB9wr+Xjb8+J7WSWz9pSTklCfLPVT7J+B9ofd4J07bcow9pRnDAcslW5EdVOAeR/PyJhvYlLc8c9JZAW0O1H/3nD+j3Na1106tm/pD492k2a+/UUP5La5rX4uhfCohwWnyZz+jB0oxaPqbf33WZJB92nabFy++M1mLWN3cE0nwtBJ/vl9cufu8OP/uVkjWUuTePCLSlKqWFKlKAtKhpigLSuNXFAWpSrQClKlAWlSmaAtKmaUBalKUBalWlAKVKZoC0qZpQFpXGrQClKtASrSpQFpUzTNAWlcatAWpTFKAtSlWgFKVKAtSmaUBaVKUBalKtAKUpQCuL9D8q5Vxk6H5GgKKtQVaAUpSgFSrSgFKUoBSlTNAWlTNKAtKlKAtSlWgJSrSgJVqUzQFpUzTNAWlSrQCpVpQEq0qUBaVM0oC0qZpQFqVaUBKVaUBKtSmaAtKlKAtKlKAUq0oCUq1M0Aq1M0zQFpUzTNAWujduOmePo+px/jWVx+URlh+cV3ivw6/YeNBNF/fIpI/46Ff9tEQzVWvDfwrJruMW/hXmoLjHiWsDf9lLIP8Axq8/g4dBA5eQ/kr17uy6f4Oot5eJayr+R4nH+ia6JPY5YcndO3jh6CW7ieWRkY24UBYvEBCyPzzvXH1umK82HCVp/f5P8m//AHa9l7adLLSW7fsJF/Iyn/bXni6TVY8GkuT4UXBFq52pP7Z+r4kOxC3kpfe23J5ZIxmvjXPDewlWXaykhgRggiu8/gf4V9SOR8DcEcgAAvGjtgdAWZSTjpzPSpK6TziXhBkALRMoboShAPyyKi6L8K9T1C4WRXCowMjiR9zbgGUEYQYGB7XmScYFf00PgvxWG4FV8+XP/wBqWNJ55pPC5kIyMKDzP+wfGvWtH4TDgJHGFRVALNyBPn867Np3DEaEAIFUdM4ya/RqdyVPhqwAI9pgAdiHqeoG7A5fyHlUX6E0fJn01I9hSJG25VN5GZH6FghIG1fInPPyx1+VPYSH6JW88yiI5G4fjsM4WPGPZXGQenIDmycy4PsjAUNnLHyyTzbByxAxlufM5NfwXkv1uvLauV5eZ6AEnp5nrUg5NuLZIXYvRZCzeyOg2liQWPUgdSTmvzldxJZgPPAjXGOQCqcZHLkMg4Ar+8kyqpLbVAy7uxwAqgkliSFCgZJJ6D5Vj9rffl0GGQxxtdXShiDPb2y+CSCRlGneFpU81kRSjggqzAg1JVmQa6jI5VWkXbyAyp2oo6ezsxgfxh5MK+hpk7AsImWN5BtOMtC5H2uftRuRkZ88+R510rs37SrDWrf1jT5lnjV9kgKNHLFIBnw5YnVXRiMMuRtdSGUsCDXcIbbkcx5zyGM8j7+WedQKP47JldctJjeuQWJ2ncOWc4I9zDkfgQRX8blPGJY/rnMn9mPf/jgdR5gZ6g57Jp+rOpXejOq9CVJIz1znJI/3Dryr8t7YlTvQLtJyMDkOfLmOYHzwR+ciT4TxbfDI6qgOfizM3y6MAR0Nftg0Ysryou0BcMDyCl/ZJXPVCpblzKnlz5V9DVbzxWyoVCBj2QBuA8wcZB+HuxXz9rDGCck56+7kPnzzQHypLVV97n71X/iP+bX3OD3cXES5wrbmZV5LjY20EeeOTZPPmK/paaX4rAHEZ6knAUgdcDyOPu+VfU4YtQLjPPIVj0wMchyz1HkKhsmKdni3fuj32mnx++6kf+LCV/79YcLw/wDCs3O9paeM1inXaLh8fMxKP9tY9nhYe6phwVnyZV90bS/B0K1GMb5Lp/y3MoH5gK9krpPYvpvg6VYpjGIFb/tCX/71d1rF8nRHgUq0qCwqVaUApUpQFpUpQFpUpQFqVaUBKtKUApUzTNAWlSlAWpSrQEpVpQClKmaAtKmaUBaVKtASrSlASrSpQCrUpmgLSpmlAWlSrQEpVpQEpSlAWlSlAWlSlAWlKUBKknQ/I1yrjJ0PyNAUVa4iuVAKUpQCpVpQCpVpQEpirSgJivIe9Z2x3HDmiz6naxQzTRT2cSxz7/DIubuG3Ynw2VsqshYAEZIAPWvX6xj9I9/apd/uzSv9ZWtWiraRWTpNoxoHpP8AW/8AoGl/kuv/AD6y97nvb1dcT6bPeXcMEMkV9JahbfxAhRILeUMfEd23kzMDg4wB8a0/rWzT0YB/pFe/vvP+h2NazikjKEm3uZhVKVawNyUpSgFMVaUBAKValAWlKUAqUpQClWlATFKtKAlWpSgLSlKAlKVaAlMUpQDFfK4r4rttPt5bu8njtraBd808rBIo1yF3Ox5KuSBk8udfWrw7vu/2q61+5k/SIalEM/b/AMsjhX/r/S/8rj/313ns+7VdN1mOSXTb23vo4pPCle2kWVY5NofYxXID7GVsHngg+YrRoEFbGvRZJjTdW/fJP0OCtJQSRlGbbpmbdKlC1ZGxa8S7cu9/ovDh8G6nM97gEWFoBNcgEMVabBEdsjbW2vcPGGIIXceVeQ9+LvnNpG/R9JkA1N0HrdyAGGnRSKGVUGcfhCaNg8YIZYEIlcHdCkmtd5ixZmZ5HdizySO0kkjH6zySOWeSRjzZ3ZmY5JJJzWsYXuzKU62RmJxn6UHVpmcWGn2VnHn2HuGlvJiuOrKpt4o3z9keMBge02cV57cd/vipzn8IRJ+xSxtdv+dGzf51eHcMcK3OoTi1s7eW6uGG4QwIZJNucb2C/Ujzy8R9qA4G4V6/pfcc4rmXf+B3j9yzXmnI7fJReMR8n2mtKijLVJnb+HvSNcSwMDM2n3aZ5rLaGJiPcHt5YwPnsb5Vkh2R+kp0u8McWrQtpMzcjNvNxYBsE5a4EcbwJgZLzxJEp5GTpnArjvsC1zSImn1HSru0hTJeZvBmhQAZLPNaTXEUaAcy0jqB8K6D4vuqNKYUpI342d4kqK8bq6OAyOjBkZTzDKykgqRzBBINf1rWf6N3tA1v8ISWFsrXOjKGa9Ert4enSsgaJrZ2JCPMcb7JF2yBzP8AREO02zDFYNU6OiLtGKWqcKeHLKmPqyOo+QY4/NXYuy2wMV/A2MAl0P8ACjf/AG4r0LibhoePI2PrEN+UDP581+bSdD2SxuBja6n84z+atL2MtNM77r1rEyqZVVgCQM+RI8vnivifg22ZcrCDjkcgjH8Lpz+ddov4cqfd1OACcfI8q+IIME5LEHl8x8s4BHyqiZoz5UnDdswzzjPkM/78g/dXBOEYB9Zm/Nz/ADV9o6f09ke/IPP54xz/ACV/b1Ns43MT5eyMD/5+FTZWj5dnpduh5RnPlkEn89fQggPU4UdAOmfnX6uS8yMkedfOuW382znyHkB7+vX41Ao/hqV6S2081XqE5lj+LnoB7wMnAPSvlyqCCcEsx9wKgcs/Mk49/Tzr63qwxgA/E/7OnSuT2PuBx06VZMHwZtP6c9xxk+WCfI/IYHLlXFrbmOQ5cuQHQV9z1PzwBUFpRyFGOXfaim/oZ1MwZJIthOOWPUmu4FvdwPLw/VjJv/we+tZO33Vu2vtJSVHjkRXjkVkkR1DI6MCrI6kEMrKSCpBBBIrFviL0b2jTTNJb3eoWUbEt6vC9vJEhJJIiNxbyyImT7KM7qgwqhQAo0jLszJ2eC+j2muvw7cLGG9UOlzm65ex4q3Nr6mWPUP7V0EGeambrt5fL9IWx/oljBJH9I7DkCR/z/WPca2BdkHYhYcP25t7CJgHbfNNK3iXE7jOGll2rkKCQqKqRoCQqrk1gP6RbA4nj5f8A0Dp/+sNZpdsnsY+cLQfqq0ILf11beZ/v8fxrdml26EgYAzkjHWtKHCo/VVp+67X+fjrdpJCcn50kRESSxSH2kKn3r0/JX6LmFXI27OmBjIP38/8AaK/ILei24FZmlnN9LKj6g5+4kn+Wv28O2mGY8xyxj3ZP/tX5IYGHPn+WvvaOzFSW9+OfwFQ2WR4t24WBmu4x5RwKPvZ3Y/mxXn/9DBx08q9u4t04S3EjY/FUfco/25r5thwzukQY6uuflkZ/NVk9ijVs9AuNSg02yMtzKkFtZ24aaaRgscUUMftyOx5KiqpJJ5AV53/ywuFv+vtM/wAqj/31/Pvk5/oT4k/eXUf0aStNiqfOojG1ZectPBvJ7Pe17S9ZEraZfW18IGVZjbSLIImcFlVyvRmUEge6u31gd6K39Z1r9usv5uas8aq1TLRdqyUq0qpYlMVaUBMUpWMPb/36LLRZ3srSE395HkSgOI7eBx/c5JcMTKPNI0bb9oqcCssTFjhrVN0j2Ol9IznVcdZfJYbnPml2Xq26SXzbRk9VrADh/wBJldCQetaXC0Ofa9WncSqPeolXY5+BZM+8Vmj2X9qNnrdol5ZS+JE/JgRteKQY3RSqeayLnmOh6gkEE54WZw8XaD3/AA/iet1rwn1XosYzz2C4xeykmpRv0uLaT+Tq+x22lWldJ8iSmKtKAmKVaUBKtKmaAtKUoCUq0oCYpirSgJilWlAKVKUBaVKtASlWoTQDFKwd7evSFPb3EtposMMghcxvfXAZ43ZcBvV4kdCyq25fEkYAsuQjqQx8Lfv08Sk59ciHwFtFt/IQTj7683E6hhQend/Tg/W+mey/rmfwI46hDDjJXFYkqk0+HSTav50zatVrCHuk97zWda1VNPvRaSQtbzzNLHC8UymLYBzErRlSXAI8MHmOfkc3a68HGjjR1R/M+F670LNdEzX7Jm9OulL3XqVPjctKUrc+eJSrSgJSrSgJVpSgFKVKAtKUoCVJOh+RrlXGTofkaAoq1BVoBSlKAUpSgFSrSgJSrSgJmsY/SPH+pS7/AHZpX+srWsnaxi9I/wD2qXf7s0r/AFla1eHxL6lJ/C/oapRWzT0YH9gr3995/wBDsa1lrWzX0YH9gr3995/0OxrWfBjh8nRvSGds+r6VqtjDp2o3NlFJp5lkjhMYV5PWZF3nfG53BQF5EDHv5Yxl0PvYcR+sW3i65feF61beNueIL4Pjx+NuxF9Twt+7HPbnGDg17P6UM/050797G/Spaw3zSKVCTdmZvb96R++upZbbQcWVqMot/JGsl5MeYMkMMyNFbR9CnjRyyMDllhI21jHrnbJrV22+bWtXLeZj1K8twf4FtNDGPkFAHuFd97uvdG1PigNPC0dnp6OY2vp1MglkRtskVtCjK0rRkFXkZ440f2Q0jLIiZD6z6K9vCPq2tfTgchPZjwWPmD4c+9AeYz7eOuGxgrjEe9Lcxf4K70/EWmNG0GsXkiIcmG8f16KUY+rJ6yJJseeY5onyPrVsJ7pvfPt+Jg1ncxpZ6tEhcwKxMN1EvWe0ZsN7PWW3Ys8OR7UikSHWF2g9n93o95NYX8Xg3UBG5c70dG5xywyAASQSDmr4B6qyo6ui/j4U44m0q6t9Rtl3XFjKLmEZwXZAweLdg7RPE0kDH8SRhzBIJpMiMmmbCvSHcS69pJ0/UdL1O6tLKTfaXcMPhlVuDiS2m9uKTaHQTxvzA3LDgZJrDV+9lxOQR+Hb8cuoNvkfEfqfqOvMEVtW7aOAIuJNCurRSv6stBLaSMu4Rz7RPaS45cklEbEAglcjIzWlq5tyjvG4CyRu8UiZBKSxOY5UOPtRyKyH3FSKiG6LztOzc13X+1v8P6HY3zsDO0fg3YHLF3ATFPy5YDuviLy5o6kciK9VrW56MvtRFrfXmjyMRHfr65b5Psi6t0WOZBk8mmtgjAAYItmPU89kVZSVM1i7R+TWtXjtoZZ5mCRQRvNK7HCpHGpd2JPIBVUkn3CtO/FPe94luLu7uIdbvYIJ7qeW3gRbdEgtnldreBVaAt9FCY4yWJZmUsTkms2PSSdr3qGjppkbAXGsO0TLyJ9Rg2Ndkr5pIXhtm+E55HnWsTx8cz5da0gu5lN9jN/uI8ecSa5rLPeaxez6dYQNLcRSGAJNPNmK1hbZbqSnKaZsOpBhjHtBmFZ49onaPZaNZy32oXCW1rCAXkfJJZjtSONFBeWaRiEjijVndiFVSTivHe4n2VfgnQLd5I/DutR/V9wGGHUSqBbxN1wYrYRgrnAkaQ/aNYF98/vAtxFq0iRs34P02aa2s48sEkljcxT3rIcKzysjJC5BK2+NpXx5QYa1Mm9MT0rtj9JbqV40kWjRLp1tzVLqdEnvXBGPEEbb7a3weaqy3JPInacrWOmvdu2u3hBn1vVWb8aO+uLXPx22b28Y+SoFHkBXyezjs2u9ZvYNPsY/FuZzyBYKkcSlRLcSsfqwQBgzsAzHKqqu7xo2wLgb0XulRRL+Eb29vJyq+J4DpaWwfHteEgjkn256b525eQq9qJTeRhLw13kOIrEqbfW9RG0g7Zp/XFYA52uL1bjKt0OMNjowPOstewP0lO91tuIYooVO1V1O3BWEEkgm8tzu8BB7JNxE7RjLF0gVC549sHozY44JJtEu7h5kBcWV60TrNtBPhw3CJCY5G+yZ/EUnALIDuGA9wjI7xupSSKSSKRD9aOWJ2jljYDo8cisjDyZSPKm0hcom+6CdXUMrBlYBlZSCrKRkMpHIgjmCORFfh4i4ggsoJrq5mjgt7eN5ZppWCRxRoCzu7NgKqgZJNYOejS7dXkWbh+5k3erxNc6buLFlt1cLcW2WJ+jgeSN4VGAkchjVQsSivq+lG45lh0/TtOicql9cSzXIGcyRWaxlIjgj2TPNFKc5z4IGPayMtO9G2razz7tq9JjezyNDoMCW1sB7N9dxF7qbOfajtX2pbKORXxxLIckNFEVwcade7xfEN4P1RrepufMx3LWn5FshbIv8FRXnmTWeHd79HVZ6jptjqOp3t1uvraC7S2szBEkUVxEssaSSvHO0kio43GJo03ZA3AbjttEx3kYf6T2vazbtuj1nV8j8fVL6YfxZriRfzV6jwJ36+KLBvav11CPIPhX9vC+FH2Vlt1tphn8Z3kOff0rLjVPRh6Cw+hu9VgbyInt5V+9ZbVifuYV4j2i+jS1S3kjGnXUd7byzRRSMQltdWsUkio9xtkZoJxAjNMwVkYhCFikJCmuqLJ0yRlh2fdvd1rXC15rPqp06dbPUWiAkWdfFtYZQJ4WeNN0QmQhfFiGShypHXWfxF3muJNRtZLS/1m4urW4ULNA9tpyLIoIcAtBZxSgBlU+y6nl5jIO3247MYF0iTR7YC2tjYSafDsUHwYngaBWC+yCVB3YyNxHUZzWAHbb6PVNB0i81IarJcGziVxE1qkYkzIkeC4mYryfOQD0qsWi00zDsPXe+z3t71nRY5ItM1CSzjmkEsqRw2ku+QIqBybi3mYHYqrhSo5dM866EKyT7qXdBTiu1u7hr+SzNrdC3CLAswcGGOXflpEx9fbjB6Zzz5at+pilfB+Xs474PFM2qaTDLrU8sNxq+k200TWunBZILnUbWCZCyWauN8UjrlHVhnIIIBraH2q8fx6Ppt7qMoylnbyTbfN2VfYjHxkcqg+LViVwr6MiK0vLK7/DEz+p31leiP1SNRI1ldQ3SxlhMdocxBSwBwCTg13L0lPEJg4bMOcet39pDy8xGzXRX5EW/5KxdNqjdXFOzV/q+qTXc011cyeLc3MrTXEuMeJNJzdgMnaufZVcnYgVc4UV3bsK7D7niTUodPt2MSsDJdXIUN6rbJjxJQGyrSklY4lYEGR1JBVXrz5Ja2Pei74MRNP1LUSo8W5u0tQ+OfgWkSsqZ93jXExI8zj3CtW6RjFWzKjsr7I7DQrVLPT7dYYl+s31pZn85J5Wy8sh82YnHQbQAB3KlWuY6zg6AggjIIwQeYIPUH3isQu3X0d1lqt5Fc6dKulrLKfwhHFGGRkYMWntIiDHDdlsAqVMB3GQxllYS5gUqU2uCGk+TrPZz2b2WjWkVjYQLBbQg7VGSzMTl5JHbLSTSNlnkclmJ69K7KRTNYx9/HvFS6BpsdvZP4eo6kzwwyj61rboAbm6Xmp8QArDERnbNMj7WEbCiVsPZHwu9B36LHRJpLKxiXUtTjCrKu8pZ2pPlPMoJknVcsbaH2h7IkeDerVhBxZ3w+Jb52Z9Tkt0YYFvYxx2sS8zzVkU3JODj27h+g88k+QflPmSSSSTzJJOSWJ5kkkk5JJzWQfdr7mWocTJ62ZFsNODsi3MieLJcMjFXW2hDJ7KMCpmkYJuUhVk5leilFbnNqcnseSRdq2rh/EGs6xuzn+y2oFf+zNyU+7bXqHAXfe4k058tfnUIuX6nv4o5VAHXbNGsN0C3veeQDAwOoOT116K7T9h8PWNREmORkjs3iz8USCJyvwEoPxrDvvA93TUOF7iOK8VZbeckWt9DyguHAZni2MxkhuURTIYX3Ap7SSShJPDaosmmjYz3a++FpvEwFt4fqWqLH4kljK+8SKOTvZzlUFzGh+su1JYwVLxqGUtkA0RPwFaHtM1OaCWKeCV4J4ZElhljYpJHJGwZHVh5gjmDlWXKsGVmB3Kd2LtlHEejW1+wVbnBt72NRhUu4fZl2A5Iil9mePJJ8OVM88ispxrg0hK9ma/e9D3ites+JNatLXWLy3tra6gjhgiMISNW0+ymYDdE7c5JXbr9qvk9iXfA1W21aym1XV76bTYmna7iIjk8VfVLgRII0hDMxuDDtwy4IBJChq6n3wIwOLeIff67b5/+F6fXkpbFbJKjFt2ZG9rXf117VJGFnL+CLTcdkVuI5Lp05gesXUiOQzDDFbYRBG9kSSgb28WftP1YyeKdY1jfndy1bUQuf2sXIjx+xC4+FZDd3buC32uQR319OdNspl3QIIxJeXEZxtlCswS3iYZKeIHdwQdiDG71viT0VsHhN6lrNz432ReQQSQk+4+rpA6g/je3j8U9KjVFbFqkzHbs678vEOmPmS6/CcPLNtfhTyHUJdRoLmNm/HdrgL18Nuh2Hd3vvHadxRA8lpuiuYNou7KbAngLDKuMcprdzkJPHlCysp2OjoupjtE7PbzRr2XT7+HwbqEKzKGDo8b58OaFxgSQSbW2vgHKsrKjI6L/AF7Ne0+80K+g1OyG6e1JYwl2jS6hYES2spBA8OZeQLh1jlEUu1jCtRKKYjKjcN2uSywaVqk0TtFLDp97LFIuNySJbyMjrkEblYBhkEZFanLTvRcTbVzr1+TtGT+pvd8LetrnahrUN5w5qN3A2+G40a7nib8aOWzkdD8DgjI8jWla0xtX/FX+SohwTPY2R+j27StS1aPVTqF7PemGS1ERn8P6MOkxcLsRBhiqk5B6CsePSSJjiiP94dO/1hrVe0eiyGY9a/bLL/Qnrx/0l4xxVH+8Gnf6w1qov3if3THDhRf1XZ/uu1/SI63kPbczWjjhMj1uyz/0y0/SYq3b9pHGdvpFjd6jckiC0heeTHNm2j2UUDJLyMVRQASWYDBzSfYQ7nn/AG6d4HTuGrcS3zs00ob1azhw1zcFepVCQEhUkB55CsSEgFizKrYA9pff61/USVtZI9Ig3eylqiTXBUHpJdXEb5yMZMMMBHPB868U7Qe0O91m8n1G/ffc3BBZVZ2igRRhLe3Dk7LeIclUBQzF5CN8jk/W7G+xq/4ivRY2EQZwokuJ5CFgtITuAmnPNsMylI441Z5H5ABVleO6ikrZRtt7H4tT7XNYnbe+s6vu6+xqd9EP4sNxGv5q7Twj3qeJdPZDBrN4yJ1iumS9ikGMYf1pZZcDrmOWNs9SelZeaR6K2y8NfWNZv2mx7Rt4bWKLP7FJoriTHzlJrxDvH9xG+4fge+tZ/wAI2EQ3TnwxFdWsY6yyIGZJoR9uSLa0f1jHtDOhSi9hpktz3DsC7/1rqMsdprcUdjcyuI4ryIt6jM7AbRMHy1k7vlV3vJCTs+lRpFjGY1zaeHHJIvIrFIysMHBCHBHkff51onZsjHkeWDzyD5fKtjPo8+3ibVLO60K9lLz2cG6zmfm72LjwjE5LEySWchADHbmGWFTuZHdqTjW6LwnvTMJ5u9fxNqdgYL3W7i4t721CXNu1rpqxyxzxYljLRWKSqjBiMrIrAfaroPiVmL2qejfh0DRL+/TVprj8GafNcLE1rGni+qwlgjOJW2b9mCwU4znBrDjYa0i7WxSV3ud27P8Att1jRhKul6hLYico03hw2kviGMEIT6zbz42hm+ptznnnlj0ngPvccVy39hHLr11JFJfWcUsZtdLCvHJcxJIhKWCuAyMRlXVhnIIIFf37p3dPXitL53vns/U3gQBIFm8TxlkYk7pE27dmMDOc1kjw36MeK1uba4/DMr+r3EFxsNnGN5glSUKT4xwGKYJAyAaq2lsyYqXKM4KZpSuc6RSlKA8w7y/aM2j6Jf3kZ2zLF4UBIziedhDE2B1Cu6t93l1rT88pYlmJZmJZmJyzMxyzMTzLMSSSeZJraX39NPaThm82gnw5bSQgfipdRFj8lGW+6tWVfN9Tb8xLtX6s/r/2M5bCXTcfHSXmSxdLffTGMXFfS5N/8FrJTuCdpEljriWRZvA1NHiZeqieGJ5opMZwCUSSMkAk7kB5AYxqBr2Luf2DS8TaQFBOyaaViB9VEtLglj7huKrk+bAedcGXk44sWvVfns/yP1HxllsLH6JnIYyTisKcl8nFaov6ppG3GpSlfZn+d4zXCWYKMkgD3kgD89c6xy7/ALcleG7gqSp9Zsuakg/1zH5jBrLFxPLhKfom/wAD1elZF9QzuDk1LT5mJGGqrrVJK671ZkPHfITgOpPuDAn8xr82oa/BDgSzQxZ6eJIiZ+W5hWmrgDtNudLukvIHZpo0lWLxHdkR5I2jEhXPtFNxYKeRIGa+Br+o3F6z3dy89yWY77mYvIu9m5qZGyi+0cBAQBkAAchXjy6okto7/X+h+9R9jeNHHccXNxWFSqWjeUnfuqLkuNt73vZbG763ulcBkZXU9GUhlPyIyKXN2kYLOyoo6szBQPvOBWoLsJ7wuocO3CyQSPLanAnsnkYwun40aklYph1DqAD0YEY2/I7Wu23UdeuXlvZ5CkjbYbNHf1aJS3sRxwg7Xk5gGRlMjnHQBVW76nDTdPV6f1OBex7P/tjwpY0Fl0r86t3/ANui+V9dNd+xuH0/ie2mO2K4gkb8WOWNz+RWJr6Wa0Z2MzW8m6MyQTRn60bPDLGev1lKujdD1B6VsN7j3egn1TfpWoyeJdwx+JbXDfXuIVwrpKc+1PEcHfy3ow5ZVidcvn1iy0yVPtvZ5Pin2ZZjo2Ueey+MsbCj8dR0yin+9VyTj677c8GX+aFq+Hxvxnb6ZaT3t04jgt42kkbBJwozhVGSzsfZVVBLMQAOdat+3Xvc6prsrKk0tjYhz4NrbyPE7p0U3UkbAyuRzMYIiUnGHKhz0ZnNQwFvu+y/vsfI+FfBue8R4kll6jhx+PEl8Kb7JLeUvkuO7Vo2l3XGtnGdr3dsje5p4lP5C4NfRsdRjlXdHIki/jIyuPyqSK0faXw3NdbjBbzXBB9swwSTYY8/aKI2G8+ZzXY+DeP9T0K4VrWe5spkIcwN4kaSA+Uts+1ZEbBGWTI57WUjI86PVU370dvr/Q/Vcx7Hqi4ZbPQljJfBKKjv6Wpya/8AU3PveoDguoPuLD/fX9I5QRkEEe8EEVpc7Qu0m41O+ub5y0T3LrI8ccknhqwjRDt5jkSm7B6Zxzxk7FO4rfluF4CxZiJb/mxLH+uZscyc8ulduXzixpuKXHf13PiPE3s+xugZDCzmNjKUpyjBwUfhcotv3tTTpqtluZE/hOL++R/x1/31/cyjGcjHXORjHz6Voyi1KRlwZZeYPPxH8/vr0jtJ7xOp6okFu1zJBaQRRQQ2sEjor7ECBpipDTyuRna3sDkAuRublfU4q7j9N+f5H12N7G83GeGsPMwcGm5ycdOhKq21Nybv5JVuzbZJxzZK203lqG/FNxED+QvmvrW12rgMjK6noykMD8iMitIFzwVdRIZJLK5SMAs0j2syIFHMsXaMKABzySBXYOzjtk1PR5UlsLyWIL/cS7PayDriSAt4bD9koVxzwwyapHqm9Sh+f9Eb4/sec8FyyWdhiTXZxpN+mqM5V90bpM15b3luL2s9B1WaCQLMlnKEII3KzjwwQPeu7P3V8vu0d4+DiWzZ8LDeW+1bu2znYWzskjJ5tDJglT1BDKeamtX/AGnapKdR1RfElKfhG/BUs5TAu5hjBO3A6YrszOaUcNShvqTp+h8X4R8FYuf6riZXNyWFLLyhKcJK9XvL3VuuVw9007R1bTrQu8cS4BdkjUnoCxCgn4DIz8K2mcDdz7hu1tYo5rO3upRGviz3D+JJI+0bm+sFQE5wqKqjyFasV/8AnH/z1r6Znuvfc/8A+6vByuPHCu4av0/Jn9O+MvD2a6wsKGXzry8Y22la1t1T2lHjfb5m2vs/7uWiaTeNqGn2q287QPbsY5pGi8N3jdgImkaNW3RJ7SgHGR516cLtPxl/jD/fWDnZO8o7PNUctIHEepkMxYOMO2MEncMeVYX8PcYT29xbzmaZxBPDNsMsmG8KVZNpyx+ttx0PWvYlnY4KjUK1JS22q/sfzx0/wFm+vY2bc825Ty+I8FOacnPQnVNy2XZK3Ru0uLlUG52VVHVmIUD5k4FfPteK7WRtiXNu7noqTRsx+ShifzVp87WO3XUdduXkvLiQrIdsVnHI4t41z7KRwBsO/PnIys7nzA2qv7u7rwzu4h0eKSJo2a9jdQ6NGSIVaY43AE4EfPFVXUlKajCOzdbv+jPQxPZPPK5HEzWczcY4kMOU3hxjq+GLlp1OSt9rSr6m4mvy3+rRQjMskcY98jqg/KxArEHvd9859Nlk0vSSvracrq6I3C2LLkRwg+y1wAwYsdyR8hhjkLg5Daarrs7Aeu6pcZ3sGaW4KbicE7iUiU8wo9hcDAAAxWuP1COHLRFan8v4d7PC8P8As1zXUcqs/nMaOXwGrUprdx/1U3FJPs29+apm5C244spDtS8tXb8VbiJj+QOTX2lbPStNus93DXLSMzTaRdxontFxGrlcc84iZ3GMZzjlXbOw3vbapocifTSX1iWBktbiVpMJjBNtI7EwuBghcmI4I2ruLjKHUt6xYOP4/wAGkz2M17K/NwJY3SM7h5lx5itKv5JxnJX6J19TbPSvgcBcc22q2cF9aP4kFwgdGxg+5lZTzV0YFWU8wwI8q7BXsp3uj8HxMOWFN4c01JNpp7NNbNNeqJigq0qTMUpSgFcZOh+RrlXGTofkaAoq1xFcqAUpSgFSrUoC0pUoC1M0pigGaxj9I/8A2qXf7s0r/WVtWTlYxekf/tUu/wB2aV/rK1q8PiX1KT+F/Q1TCtmvowP7BXv77z/odjWspa2bejB/sFe/vvP+h2Na4nBjh8niXpQ/7M6d+9jfpUtYV6zfeDDNKBkxxSSAe8ohYD78Vmr6UL+zOnfvYf0uWsIeLf60uv3PN/NtUx4REviN8nZjwZHpmnWVjCoWO1toYQB71QbmJ82Z9zEnmSSfOuzVE6D5Va5jqNfHpTuGIxNot6OUhS9tXxjDpm3miLeZMREu33CV/hjBI1sH9Kh+saL+6Lv+ajrXyBXRDhHLPk3Xd3aZn0DRWY5ZtLsST7ybaOtb3f8Aux8aTr73MMYS11dHvVKghReB8X64ACqzu8VyTnMj3ErY5Ma2P924f1PaJ+9Vh+jR10Dv09kJ1nQLhoo/Eu9OPr9qoALsYlIuIkJI9qW2aVVBIBk2ZIHMZRdM2kriapeEeL5tOu7S+gz41lcw3MYUgFzE4ZostyCzx74G/YSNzHWt4XAvGkGp2Vpf2zb7e9toLqFsEExTxrImVYBlYBsMrAMpBBAIIrRSGDYIOQeYI8wehFZgdiHetbTOD9VshL/TCzYQaXuJJ8LUmKo4GV3LYyesSFUIxGsK5BYGtZqzKEqPKO+B2xfh3X7yVHDWto3qFmRnBjtyRNLzA/XbozEFcholhbPPl8Lu6dkH9EGs2OnvEZLZ5DNfdNq2cCmSUSZ6rOwjtcAE5nBxgMy+U21mI1VFHsqAqj3ADAGTzPIVsn9GX2Sm2sLrWJlIl1GQQ2wb7Nnasw3geRnuDIxI+tHHD7qS91ER95mSHeJ4ofTOH9ZvIQBLa6XeyQj7IlS2k8Ll+KH29PKtJUVpsAXJOABkkknHmSeZPvJ5mt3XeE4NfU9B1mxjOJbvTL2CI+Qle3kERPwEm2tJKSggHmM88HkR8CD0I6EHpTD4LYnJ7X3YO8oOFJbyddNS/mukhiV3uzbeDFGXd1UC2uN3iuyFjlf1tRg+WQY9Krcf9QQ//FX/APTa8A7qnYPZcUXdzZT38tlcRwrPbokccnrEasUuMbyPahLQnA6rIT5HGTw9Fdbf9dXX+Swf8VHpvciOqtj4Z9KnN/1BF/8AFG/9OrETtn7Q01rU7rUktBZetskkluspmUTCNY5JBJ4cWfEKByPDX2ix5liazaHosLX/AK5uv8lh/wCKuLeivtv+ubn/ACWH/jqLiuCXGT5MSu6frrWnEuiSqxUNfJbOB9tLxHtQp+HiTI/LHNB8Qc5vSP8AZDPqWkwX1rG802lSySywxIZJZLOdAs5jRfaZ4XSGchQ7GOOUBWJGPl8AejXttOv7K+/CtxMbK7t7tYmt4lWRreVZUUsGJALIMkDOKzMqkpb2i8Y7UzQNDchwGUgqwBVgQQQRkEEciCOh869k7Ke9rxBoUS29pfB7SMYjtLuGOeGIZJKxNhLhEJP62J9igAKqc87Be13uDaDrDtNHHLply7M7y6eYokkdjuZpbaSOS3Znb2mkVEkY5O/mc49cS+iyvFYmz1i3kTyS6tZInPzlilkX8kP5KvqT5KaJLg/BoXpSNTjKC50mwuVyBI0NzPaOBnmyo8V4rtjOELRgn7Qzke9dm3pHtAv3jhuvWNLlkOFa7QG1zgn2ruEvFCpxya48FScDOSAcJ+0fuS8SaSjzSWC3dvGrvJPYXCT+FGi7i8kEgguSMA8oYZsY54rw5MEZHMEcvcQanTFjW1yb8IZgwDKQVIBDAggg8wQRyII5gjrXiPfd/tU1n9zx/pMNeGejH7V554L7R5naSOyWK5sy7FjHDO0iS26kkkQxSIrxr0QSlFAVVC+49+A/1Kaz+54/0mCsapmt3GzT6rVse9Fmf6Wat++SfodvWt5K2PeixP8ASzVv3yT9Dt62nwYw5M26xE9J3oxl4egm8rXU7WU//wB2Oe1H+dcCsuxXnneD7Mvw5ouoacNokuLdvALAELcxkS27HP4syIc8uXmKwWzN5K1RpIjStmXowOIVfR721yN9tqDOV8/DuIYnRvkXWVQf2B9xrWkpIyGVo3UlXjcYeN1OHjcc8OjAqw8mBHlXsPdX7w/9C+qi6kRnsrlFttRWMFpRCrM0VxGijMslq7MwjGWaKScIGdlRuiStUc8HTNymaZr5nD3EUF7BFc2ssc9vMgkimiYPHIjdGVhyI/k6V9PFcx1ClK8A7e++jpXDd1b2kwlupncG7S1AkextiGxPKvV3LAbbdMzMm5gpwivKVkN0e/1qk9I5rUk/FDxsx8K0060hjTyV5WluJnHxkEkKkf4IVtI4c4mt72CK6tZo57edBJDNEwZJEboykfkPmDkHBFauvSN6M8HE7Ssv0V5p9pLE/kzxNNbzIB1zGI4WJ/wo9xq8OSk+DGvSdN8ae3g3FfWbm2tQw6q1zPHbqR8Q0gNb2eFuG4bG2t7S3RY4LaGOCGNRhUjiQIigD3KBWiTT9SMM0E6rua3uILlV6bntpknQZ+LxrW9Pgvi2HUbS2vbdxJBdQxzxOp5FJFDD4gjO0g4IIIOCDVsQphn28V5J3ruAo9U4e1S3dQWS1kuYD5pcWqmeF19x3JtPvVmU5DEH1uvHe9x2kxaRw/qM7sBJNbvaWyZ5yXN0pijVQOZ27jIx+zGjscBTWS5Nnwaa0ckZ99Z4eit4mYya5Yn6iLp94vP7c5u4H5eXs2sXz+6sDkbGB7qz39FdwwQdb1Dntk9RsVz03W4ubh8H5XkefkK6J8HNDkxf74I/qt4h/d1v/qrTq6/2GcHRapreladcKHgvL1IpkPSSJEkuJY296SRQujDzVj0612TvgEf0WcQ+/wBdt8//AAvT66n2O8cR6Rq+manNnwbG7SaZlBJSBleGeTaMs3hwSyPtUFiFwAxIBv2+36EPn7m8dUAAAGAOQA5AAeQ+FXFfzhlDAMpDKwBVgQQQRkEEciCOYI61/TNcZ1mFXpQeCI5NMsdSCgT2t4tsXx7Rt7tHyhPu8eKEj3ZPvNa4edbGPSh8fxJp1jpYdTPdXa3bp9pba1SQbz7g1xJEFz12vj6pxroBrohwc0+TZV3atee57OLgOcm3sNdtF+EVvJexwr/AhCIPgtazbT6q/wCKv8grZz3cOHGtezqbxBg3Gn63eAf4K6e8lhP8KFo2++tY9sPZX/FH8gpHv9RLhfQ2C+iv/W9a/bLL/Qnrx70mX9tUf7wad/rDWq9g9FgMR61+2WX+hPXj/pMT/VVH+8Gnf6w1qqfvF/3DHLhEfquy/dtn+kxVsh9J9rxi0G2th0vdTt0ce9baOW8X8ksETfwa1v8ACD/quy/dtn+kxVsi9J1oAl0G3ufKx1K3dz7hcpLZr+WW4iX+FVnyiseGaxkJFbXPR4cApZcOQ3OAZ9Sllu5XHmgcw26DrhUhjXl0LtI2BvxWqUHPStqXo6u0NL3h6O0JUXGmTS20qDr4Tu01tIAfsvE+wnp4kUo+zTE4Iw+TKSuE8KsCrAMrAqykZBBGCCDyII5EHka5gV/G7uljRpHYIiKWd2OFVVGWYk8gAASSegrnOk0c9r3AiaTq+p6dDnwbK9lhhB6pAcSwR+8iOGWNATliFBJJJJ713MNWkteK9EeNsLNPcWs4/Hgnsrn2Dy6CdLeTlj2ol+IPRO1fj9NX1XUtSjBEV9eSzxbgVYw+zFAzKwDKzQRxsUYBlJ2kAg16D3K9FkuuKtGWNcrBLc3c5yPYggs7gB8ZyR6xJbx8snMinoCR2Pj7HIufubJ++UP6k+I/3l1D9GkrTar1uR75r/1JcR/vNqH6O9aa0Gaph8GmIbCfRXN9DrX7dZfzc9Z5Vgb6K1cQ61+3WX83PWeNYz+I0hwKxD7+XeKvdIW10/T5DbzXSPNNcqFMkcKMqhItwKq8rE5cglVUgYLBly8rBX0lnAkhOnamoJjQSWkx/ELsskLH3AkOn+My++vPzspRwZOHP6Xv+R+ieAcvlMx13LYWdSlhtvaXwuWl6E1396tu7pdzGDQe8txBavvi1a7JyCRKyzo2DnBWZXGD0O3aceYrJ7si9I7zWLW7baOQ9ctFZh0OTLbc3A5DnC0hJP1FxWDW6uJr5vCzWLhu1J/fdfh/I/sTq/gbovU8NwxcvGL7Tw0oSX3iqf8AuTXyNyWqXWn8TaVdQ21zDc215bzQeJC6vtLoVycHKSI3PDAFSOgxWn7iTQJbK5ntJ1Kz20rwSqQR7cbFdwz9hxh1boyMpBIINfu4H4+vtKnW4sLmW2kBBPhuRHKB9maLPhypjydTjqNpAI7z2qdp1vxEi3VzGtnrMSBJHjBFpqMajzzlre6TmULsY3B2buaeH0ZjHjmIp1Ul+DX19fRM+Q8L+G854SzeJhxbxsnjNe8l7+FJcOUVdxadSlHjZtJI8oIrOf0c3Y66+s61Om0ODa2WRgsgObiZef1GYLGvIfrbnmCKxv7uXd/n4huTn6HTrZg19dnAVVXazQISR9O6HO7mIl9pvsK+R/bV33LbTYF0nhtI9tvGtv65t+ghWP2NlqnLxXAX9dP0eTkeLzxbKRjh/wCfibJcerf0/vf6Dx11DM9Wvw/0iOvFnXnyXw4ULupS4Tl3XOnanqMlO2zvKaZw7H+q5S9wwJitIcPPJy5ErnEaeXiSlU8skkA4JdqHfx1vUXYWsi6Zb5O1IArzMvPHiTyIeeMHESR4Pmax81XVZbiV5p5JJppG3SSyu0kjt72diSfcOeAAAMAAV+XFUx89iYjqLpfLn8f5HT4b9mPTOlwWJm4rHxu7mrgn6Rg9vvK3324PWuBe9XrmnXMdz+ELm5jVw01vcP40c0QPtp7eTGxXO10KkNjO4ZU5r9+LWEuuE2uE5pO+nTJ/iyTROPzGtbWicPS3k0NrCC0tzLHBGAM+3KwReQ8hncT0ABJxitj/AH1dCFpwh6uOludMhHyilhT/AGVtl5zlgY2ptrS6v6M+V8Z9PyGU6/0h5bDhDFljx1KCUbisSGltKlzaT+3YwG7FuGYr/V9MtJxuhnvYElX8ePduZD+xcLsbz2k4wa3GwcOQJCLdYYlgCCMRBF8MIBt27cY245Yx0rUR3bP7YNH/AHfF/I1bhxXV0tLRJ/P9EfI+2XGxP8Ry8NT0rCtK9rc3br12W/yNOXeJ4Li0zXNTsoF2QQ3CmJB0RJoYpwg9yqZSoHkAKzG9HL2eWo0641Boke6lupIRI6gtHFEFARCfqhmLM2OZJ5khQBix3xm/qo1j9ttv0G2rM70dX9gG/d1z/KtcuVilm5LstVfiv5n13jbOYz8GZSbm9U1l9bveV4bbv1tpNnzfSG9m1vLpA1BY0W5s54QJFADNDPIsTxsce0uWVwD0ZB7yDhV3Z9Xe34g0iVTgi8SP5rMrwuPvWQ/mrYT37R/U1ff49r+kxVrn7B/7N6T+77b+cFXzirMxa+T/ADM/Z/iSzHhLO4eK24x8+KT7J4SdL5W2/uZe+kx43dINN05SQtxJNdS46MtsI1jRvh4kwcfGMVjF3WOyOLXtZgtJ8+rIj3NyoJBkjiwBEGBBUSOyBiOewMBgkEZGek24ac/gm9AzGhubV+R5PKIpYyT5AiGQc/PFY/8AdF7V4NE1qG4um2W00clrNIekQk2lJWxk7FdVDH7KsWPJTWWYp5v/ADOLX4Uvyvn7nb4WWLh+CJy6b/13HGfu/Fr1NOq31aK09+KNrmh6DBaRJDbxRwxIAqRxqERQOgAAAr4/H/ZpY6vA1vfW0VxGwI9pRvQ+TRuMOjjqGUgg12GzvElVXjZXRgGVlIZWB6EEciD76/FxHxLb2UL3F1NHBDGpZ5JXCIoAyck/yV9K0qp8H8mYWJjxxlPDcvMvZpvVqvtW939zTR2lcKpp+oXtkjNIltcywo743sqN7JbAALY6kAZPPArYt3D1H9C0H7dqH6TNWuztV4mjvtTv7uHd4NxdTSxFgVYozHaxU813DDYIBGeYB5VsP7h0uOFof26//SJa+d6fXnzrjevpZ/WHtM81+G8m8a/M8zB13zq8qWq/nfJrAt19kfKto3ct7DNPstIstQEKyXt9bx3MlxIAzqJlDrFFnlHGgIXCgFiCSSTWrm1k9kfKtrPcy7VLK/0WwtIZk9asbWG3uLcnbKjRJs37DzMb7cq65BHLOQQK9O0vGd+jr8Tq9rs81HpOD5Dnoc/8zTdVp21V2v12uj31owRggEeYPMVr89IV2G2tibbVbSJYfWZjb3Uca7UaQo8kc+0eyrHYyOQBuJTzHPYJmsDPSL9sVrcLbaRbyrLLDP6zdlCGWLbG6Rws3MeKxfxCoO5VQZxvXPr57T5MtX2+v9/kfhXs3lnF17AWV1U2/Mq68unertXFX+9Vbni3ci4xaz4js1BOy8WW0kXPJgyGVCR0yrxDB6jcfeaz0739ov8AQ3q5CgH1brgZ/XE86wA7mHDLXfEmn7eluZbp/gkUZTJ+G+VB99bBe+D/AGtav+5v/ESuDJ3+y4n+7/5Pv/aEsOPizJvD+J+Rrr1811f+2vsapOEx+q7T91W388lbtYLRdo9leg8h7q0l8Jf13afuq2/n0rd1B9UfIfyVHSn8f2/U29tTazGTr/RifxieU96pAOG9ZAAA9QuOnL7BrUKqFsAcixCg+4sQM/dmtvneu/tc1n9wXH+ga1E6ePpI/wBsj/01rHqe+LG/T9We17IJuHTM7Ncqd/hA3MdmnZJp+kW0VvaW0Uaoihn2gySNjm8khyzsx5kk+dfS451BLOzurrYube3mmHIdY42Yc/Lp5V2CHoPkK+Jx9oHrljd2wODPbTQg/GSNlH5zX0daVUfsfzCsxPGzKxMxOUrmnJttt297bNJlxdSSs0sjF5ZWaSR26vI5LOx+LMSeVZx9jnfS4e0KwgsoLG/+jRfGkEUG6eYgeJK58YEs7ZPPAAwAAAAMGJoXjLI6lZELI6HkVkQlXVvirAg/EVm32N9y3h/XrGG9t9S1LLovjRB7PdBNgeJE49UJBRsgHJBGCCwIJ+TyPm6n5VXXfn+/U/tXx3Ho37FgLqvneRfu+Tem6Vaq24+H70eif/zJ9F/6JqP/AGcH/n1hZ3hOM9O1PU5L3TIJbaG4RXmhlRE/VOW8SRQjuoWVdhIGPbDHnuNZkn0Zukf9Yap/Hs//ANJX5NR9HFokCGSbVdRijXmzyS2SKo+LNagCvRxsLM4sdM1Gj8z6B1zwd0TM/tOSnmVNpxaak00/Vd9+D+fo0OJXez1K0ZiUguY5ox5ILhDvUfAvGW+bH31mfmvHO7p3dLHh2OdrK5uLpL3wXMk7QsNqK2zwzDFECrBycndnlzr2SvUy0JQwoxlyj8U8W5/LdQ6vmM1lL8uck1a0u9K1Wu3vWKlWldJ8gSrUq0ArjJ0PyNcq4SdD8jQHIVagq0AqVaUBKtKlAWlKlAWlSmaAtYxekfP9Sl3+7NK/1la1k5XgXfl7O77V+HLmz062a7unudPkSBJIY2dYL2CaTD3EsMQKxoxw0i5xgZJAq0eUVmri0ahhWzX0YH9gr3995v0OxrCte5rxcP8A+nrv/LNG/wDVKz69H/2Zajo+kXVvqdlLYzyalLMkUslrKzRNa2iLIGtJ7iMKXjdcM4fKn2QCpOs2mjKEWmY3elB/szp372H9KlrCLi/+tLr9zzfzbVsY9IJ2C63rGp2M+l6ZNfxR2BhkeKexiCSesSPtIu7u2Y+yQcoGHPrWJ+vdynjCWCaJeHroNJFIik3ujYBdCoyRqZOMnngH5UjJJEOL1G6CPoPkK5VxQch8quawOgwS9Kf+saL+33n81FWvutmPpD+x/Vtah0oaVYS3zQTXLTLFNaRGNXjjVCTd3NupBIIwhYjHSsKx3OOLv/q9ef5Zo3/qldEWqOecW2bTu7d/a9on71WH6NHXojrnl1B6jyP/ALV0nsM0Ka00XSba5jMNxBp1nDPCxRmiljt41kjZoneNijAqTG7oSOTMME94xXOzdGlHvIdkLaBrd9YKhW2EnrFieWDZ3H0kaqAAAIH8S1A5nEAJPtV5yqVs99IB3cbvXLeyvdMtWutQs3aFoEkhiaaznwWwbiaCEtBKiOu+QFUecLzcg4Qf8jji7/6u3n+WaN/6nXQp7HPKG+x59wTwhLqd5aWEGTNe3EVuhXBKeIwEkuG5FYIt87ZyNkbHBxit3nBHCEGmWVpYWy7Lezt4bWFck4jgjWNMkklm2qMsxJY5JJJJrCfuD91HUdNv7nVNZsZLKWGH1exilmtZixnObifFrcXKAoiJEhZlcCWYAYY5zzxWc5XsaQjW7I4rUR31O7rLw9qstxEjHTNSmluLaQBisFxK7Sz2bnmF2uxkgBI3Qnao+gYnbwa+JxlwXaanbSWl7bxXVtKAJIZlDocEMrAH6rowDI64ZGAYEEA1SLp2WlG0aL9F1qe1miubaaS3ubeQSwTxHbJFIucMpIIPIlWRgySIzI6urspzd7NfSgzxRiPV9NFw6qoF1YyrG0p+0ZLWYKkbcgcxzlWJP0cQAz+Ptk9Gddws8uhXKXMXNlsrx/DuEGSdkd1jwpcD2V8dYm6b5WOWrHDUO69xNCcTaHqEZyRhUhuAceYa0muEI+O6uhuMjFKUTLriv0p9usbCx0e4ebltN5cRQwjnzLeALiRto5hQF3Ebd6Z3DGPWO+Zr82qw6s13iW3LiG0QMlisMm3xLdoA30iShV3SSs8wYKyumxAvXrPuycRSnEeiai7e4wrDn+FcPDGPvcCveuyH0aup3hSTWJV0yE4L28LRXN8QR9XehltIWB+0Guh+x86j3UT7zM4O733gLPiewF5a+xJGwivLZmzJa3G0MYmOBuVlIkjcAB42VsKSQPLfSA9tz6Po/qltK0V9qpa3ieJyksFsoBurhHVleNwhWCORDvSWdGH1CV967Muy6x0OzisdPgW3t4vIZZ5HP1pZpGy80znm0kjMzHz6V5D3n+5ra8USR3XrlzaX0MPgROCZ7UxhncLJauQFO9yTJbvBI/shzIEjC5Kr+Rq7r5mHHZR6RbXdNRIb5IdYiUgeJM3qt4ELc/p4YmilKKcKJLcM+BulyS9ZDaP6UDRnX6ax1KBvMBLeZc/BlnBP3oKxZ7QO4DxPYE+BZx6pHnAexuIEfGPrPBey2zD3bYnnP8tee3Xds4iiOH0XUVPuFu0n54i6/kJrRqLMk5IzC7T/AEn9qbaWPStPuXuZEKRy3vhQ28RcbfEZI5JZZTGCWEQEYcgKZIwxddfCPyGTk+Z5cz5nkAOfwAHyr0ux7snEk3KLQtRc+4xxwdf2VzLAg+9hWQHY56NPULoxy61Munweyz2lvJHPesOpjaZC9rAfss0bXPLO1lOGq3uxIalI7R6LTgaTfquplSIWWCxhYggSSIzT3BQkYdE3QIWUkB969UYDLbvM8Dyapw/q9lCN001lN4K/jTRjxYl/hSIq/fXceDOCbXTLWGzsoEt7aBdsUUYwqgksxPmzuxLu7Es7sWJJJNfaK1g3bs2UaVGgq1mVlV1IKsAyn3gjIP3g17z3Ve9ZLwpPcBrc3djeeGZ4FdY5YpYlcLPAWXa7uGWOSOR1UoiMrIUKy5Dd6L0eEtxcT6loJj3TF5p9LcpErTEAs1lKxWKMysGZoJykZkcsJYhkViZf92jiGA4l0TUUbzVYRNj+HbNNGfmrsPjW1pmFOLMuta9KRE0tslppMqxPc263c17PGnhWrSqLh4Y7fxjJMsRYqHeNAcE7sbDnbDIGAYEFWAII6EEZBHwIrTPoHdS4lvGVIdEvNrsEZ5/BtYoweReQ3UsTFFHNhGkjkZ2o5wDto7FuG7yx0nTrS/lSa8trSGCeVGZ1d4kCbt7qrO20Dc5Vd7ZbAzis5pdjWDb5MJe/n3P5Emn1/TI2kSU+JqlqgLGN1QKb2FBk+GyqDcRoOTAzAe1OTgsgBGQQQeYI5gg+4+6t+zDyrEjt59Hjp2qNJc6W66VduWd41jDWEzsxdna3UoYZXYsTJAyhmYs0ch51MZ+pEod0YD9kPb9q/DzE6bdtFEzF5LWRRNaSseZZoW+o7EktJA0UjfaZsCshrX0ourqoD6Xp0rYwXE1zCCffsxN88b68h4z7lPFNjIyHSpLqIDIubGa3nhYftbSxXYbHUG1Az0Lda6PN2G60pw2kamD7vUrg/wAkZFabMzWpbHsPaJ6QfiHUY2iikt9NjbAY2UZM5HLcvjztKVDDI3RJHIMna6kAjGokksSSzMzO7Mxd3dyWd3diWeR2JZnclmYkkkkmvT9G7rXElyQINDv2yQMyLDaqufMtdzW64Hngk/A1kx2R+jCmkZZdcvBHHyJsrBj4jczlZb1gNqsMAi3jDrz2zA4IWkKlI6r6ODXtdGoyW1mhk0XLSaj4+5ba3lZco1o+0/q+RsF7dDsaMtJJsYxNJlF35O7k/EWmJLaKW1HTmee2QbQbmJ1xPaZYdZAFlj5r9NFGpIV3z71wZwTaaZbx2ljbxWttFnZDCgRAWJZ2IH1pHYl3dss7EsSSSa+3WLlbs3UaVGgtB8GUgkFXVkdWBwyujgMjqQVZGAZWBBAIIr2ju/d7LVOFw8VsIrqxdmkawuGKRLKxLPJBMiu9u8rHdJ7EsbNl/C3s7Nnf3ku4pYa+8l5aONN1J/akmSMPb3T7Qoa7hBQtJhVXx43SQqAG8QKoGC/Gfcj4osJSh0t7yIZIubGaCaFhk8vDeWK7VsYJBttozgM2DWupPkxcWnsZHaj6VRPBPg6JIbjbyWW9RLfd8ZEgkl25/wACCfhWI3bh29ajxNcrcX8i7It3q1rCCltbhvrFFJZnlYYDSyMzEDA2KStIe7fr7EKNG1HceQBtZFH8ZgFH3sBXpXZt6PjiTUWzcwR6RDnBkvJIppiOXtR21pNKSDzGJprdgR0xjJaUHqkeBcNcIXOoXENpZwvPczuscMSAkszEDcxAOyJM7pJWGyNAzMQAa3Kd3XsWj4c0i005WEkkamW6lAYCa7mPiXEgDFmEe87Y1LHZEsadFFfA7Ae67pnC0ZNsrXF5IpWa/uAjXDqSCYo9qhYLbKp9DGAGKKzmRxvPr4v8daznKzSEa5NNne9/tt4i/d1v/qvTq8rBr1vvdSA8WcQ/u63/ANV6fXwewThCHUdd0qyuVL211ctDOqsUJQ207Da64ZWDqjBgeorfhfYxlyesdgHfv1Ph+COylhTU7GMhYkmmaG4tovNIZxHKJI0+xDMnLO0SxoFVfX+LvSms0e2w0fbKeRkvboGOPkfaWKBC0xBwNhlgGDndy2nyTte9H9rOnOW0xTrNqWAUK9vBfRrjrPFNJbwTYI5vbNuYsMQKASPLf+TbxBu2/gbUN3THq7EfxwSn37sVSovctclsdS434uutVu5r++ne4u7gjxJXwPZQbY4o0UBIoIxkJEgCglmOWeR2+92Mdi91xFqMGm229RKd1zcoARZ2o/XJ23eyGx9HCpDb5mQbSokK+r9l/cH4h1CQeuQpo9uG9qS7eGed1BGfBtrWeQ5YbgDcSQbTg7XHKtiXYX2Jadw1aC2so2LvtNxdy7WubqQfbldVUbRk7IkCxxgkKoycpToKLfJ+XtVijtdB1K2hUJDBpN5DEg6LHHZyIi/coAz51pks39lf8UfyVuJ7U7xrnT9St4kLyzWd7DEmVBeSSGREUFiqgsxAyzADPMjrWsuHurcS7R/SW4HIf860v/8AX1EEJmU/ow7rbFrJ/wALZf6FxXkPpIbjfxRGf/uHTh/+Ia1XufcV7LNS0iLUhqFq9m00ls0Yklt5N6xpLvYG2mnACl1GGIJJ5A9a8277PYNrep67FeWGnyXlsdJs7fxYp7OMCWK71KV0K3N1BJyS4jOQhX2iM5BFK94n90xN4WH6rsv3bafpMVbpO0HhuDVLO70+5Xdb3cLwSgfWCuOTKfJ0bDqeoZQa1X8N91/iOO4tnfR51VLm3d2NzppCqkyMzELfFiFUFiFBYgcgTgVtNm1qMnIcLnqDn82Acj84pPsRDuacu0bsyvdEvJdPvVxNCeUiqViuYj+t3MOc/RSjnjLeG4eMsTGxr9PZZ2qX+hXi32nzmGYKUdWG+GeI8zFPESBJHn2hgq6NzV1yc7Pe2jsh07iG3EF7s3oG9XuovZurZmwSYpDG3sMVUvE4aKTaNynAIwd487iWt2rsdPWPWIuZAtnit7lUz1khu5YYjtGATFO5Ynkg6CU0+SHF3se38OelR+ixeaKfGGRm1vFaJh5MRNCjx5/EBm2/jt1rwvvC99rVOJYHsjHHp+nyH6W2t5WlkuUVsqlzcskRMLYVngjjjVsFHaZCwbod13auIIztbRdRDe4W7Pj+FHuU/cxFff4V7lvFF9IqJpMtvG3W4vJbe3hQfs1MrXR9wEdtJzxnAyQqK3JuT2PFmQAE9AOZJ8hWzT0endul0m0k1a9Ro73Uo4xDBIrI9tYj6RBIjgNHcXDESSIyqyKsSMAyPX6e7v6PSx0eSO81OVdUvYyrxRmILY20iPvSWOF97y3EbBCs0zYRkDpHE2TWXIqs53si8IVuzovbrwM2q6Jq2nqcPe6deWyH3PNbuiH7mIrSMkRXkylWHJlPJlYcmVh5MpyCPIg1vzNYM96b0ez39zNqehvFFNcM0t1p0pEUM07uWkuLaUDEM0xZnljkBjkk9vdEzyl6wlWxM43wYu91zvNS8K3ksvg+tWl0iR3UAYJIDGWMU0LEFfETc6lHwrq31kKDOTHFvpUrZFQ2ek3BAkjM73Usa7LcMDOYYrczvNOIw3hoWiUvjLctpxG1Duv8RwHE2iagjfirEk/+fayTxH5q5r9Wh91HiS6ZVi0S9O5gpaUQ2yID1Z2upYRtHU7d7e5WOAdGoszTktjczaXqyorowZHVXRgchlYBlYHzBBBFfF474Gt9UtJ7K7jEkFwhSRckHHUMpGCrqwDKwIKsAR0r4HYDwheabo2n2WoPFLdWtusMjxMzptQkRLvcKzskWxGfau5lJAAIFegVzNJ7HbhYs8OUcSDakmmmtmmt019DUn28d1LUuHpXYxyXdhkmK8iQsFTGcXSoD4DqMgufomxkFd2xfGBIPI5++t6EsQYEEAg8iCAQR8QetdA1Tu96DPI0suj6ZJI5yztZW5Zj72Jjyx+Jya8PE6ZveG6Xo/5/39T+kOi+2TFwMFYXUcDzJJV5kJKLl/5Raq/Vpr6GnnStNluXEVvFJPKekcEbyyH+BGGb78Vlb2Hej8vb1kn1hjY23JvVkIN3KOu1yMpbqeWcF5CCRiIgGtgPDnBNnYoEtLS2tkHRYIY4lHyEaqK+1itcLpsI7zd/LhHk9e9rufzsHg5DDWBF7Od6sSvk6Sj+DfozyTtH7t9nf6QNHt3l062QDwxanapK89s6HInic85Fc5fJO4HDDXX2ud0vWdEZi9u13bAnbdWaNKu3PIyRKDLCcczkMg/HNbb8VGQHkRn511ZjJwxvk+zX8j4nwz486j0GUlhtYmHOWqcJ95PmWr4k39WvkaKxOPeOXL5f+9fu0bS5rqVYLeKS4mf6sUKNJI3lkIgJwPMkYHUkVuR4h7ENGvX8S60rT7iTp4ktnA74929oy2Pvr6vCnZ3YacpWysrW0UnJFvbxQ5PvPhquT868xdLle8lX03P1/F9tWH5P+Vk35nzmtKf2jb+lL6mM/c77n7aSy6pqir6+VPq9vkOtmrjDMzAlWumU7SykrGpZVLbmY9q9IG4HDVzk4/VNl+kx1kfX5dQ0yOZdksaSIcErIodcjocMCMjyr1nl4rBeFHa01fPK5PwuXijNZnrGF1fOe/OGJCelbKoSUlCPOlfj6u2zT73arlf6IdG5j+v4fMfshW4vFfGtuC7NGV0tbdXU5VlhjDKR0IIXII94r7IFUymWeBFxbu3fFdvqz0fGviuPiTNYeZjhPD0Q0U5ar95u7pepqM75MgXijWMkD6W26kD/AJja1mh6Ohs6ASOnr1z/ACrWR95wpaysXktoJHPVnhjZjjkMsyknly51+vTtKigXbFHHEuSdsaKi5PU4UAZPvrLCybhjvG1c3tXq0+b/AEPU6344j1PoeB0dYDi8JYfv671eXFx+HSqu75dHgvfxnA4avsnA8S1HPkOd1EB+U8q10dgs6nW9J9ped/beY/vgrcnfadHMpSWNJEOMpIqupxzGVYEcjz6V82DgiyRgy2lsrKQyssEQII5gghcgg8wR0qcxlHi4ixFKqravR36lvDXjqHRelY/TXgObxXN69dadcFDjS7qr5Pk9rPZfba3YXFhcg+HMuFdcb4pF5xzJkEb43AYZBBxgggmtUfbP2A6jw9M0d5EWgyRFeRKxtpV3YUlsEQyMCMxSEEEkKZANx3GGv4XlgkqlJEWRTyKuoZT8wwINXzWUjjq+Jep5vhDxxm/Dc5RhFYmBJ3LDbrf/AFRe+l1zs0+62RpW4V7TNQ09SlnfXVtGfsQzyLGMnJIjDbASSSSFBNf1jfU9duEiDXupXBb2I2kluCpblkB2KQr73OxAOpFbXrnuy8POxY6LpuScnFpCoJ65IVQDn5V3DhbgSy09PDs7S2tE67LeCOFcnqSI1XJPmTzNebHpk+Jz935X/wAL8z9SzPtayEU8bKdPSx3+/LRz6txWqX4q/U0z8e8JSaXeT2Fy0fj2zIkuxspuaJJSFJAJAEmM4GSK2QdwsA8LQYwR41/8f+cy173d8F2cjs8lrbO7HLO8EbMxwBksykk4AGSfKv0HTI4YXSFEjQK5CRqqKCQSSFUAZJruy2T8mbldp3Sr5+t/ofFeKfaC/EPT8HJTwdM4zhOU9Sak1Fp1HSqtu+XXBo7tgAo+Vd/4n7JdS0y3stSMcotbq2gu7e9t94EXjRhzHJImGt5U3bckqrggqxJZV88gHsj5VuH7tVsknDmiq6qynS7IFWAZT9AnUEEGvGy2XWNKUeNrX4n9CeOvFON4ewMtjQw44kJyccSEv3o6b2fZ/Zr1Rqquu1/VpY/CfU79o8Y2+tz8x7iwfcw9+Sc+ea+Hwvwtc30y29nby3MzEARwoXbmerEeyi56vIVUdSRW3m87s/D0jF20XTSzEliLSFck8ySFQAknmSRzruHC3A1lp6eFZ2ltaxjPsW8McK8zknEaqMk8yfOuxdMnJ+/Pb8/z4/M/Mp+13J5fCf8Ah+RUMR+rjGN+r0K5fl9TxTuhd2McOWzzXJV9Su1Xx2U5SGNSSlvEeWQCdzvgF3+CoB2LvhP/AFNav+5v/ESvZK/jeWSSqUkRXRuTK4DKR7ipBB+8V7HkxWE8KOypr8e5+DYnXMxmepx6nm3rxPMjiPtelpqK9EkqXojSJwlcL63acx/XVv5j+/JW76D6q/IfyV8QcB2IwfU7XI5g+rxZH+ZX3RXNk8o8unbu67Vx92fV+OPGMfE2Jg4kcF4flqSpy1Xqafoq4PKe9d/a3rP7guP9A1qG0u5XxYvaX9di8x+Otby7u0WRSjqrowwysoZWHuKkEEfA18ccBWP/AEO1/wAni/4Kpmsm8eakpVXyvvfqjs8H+OY+Hspj5WWA8TzXdqemvd08aXfqfbi6D5Vypileofkpgv3wu5lPPPLq2kR+K8p33lkpAcuBgz24OAWYD6SLILHLLliVbC7SdfvdKuCYZbqwuV5OFaW2l5ZwskZ2sQMnCyKQD5Vu5xXW+KuzbTtQG29sbS6AOQLi3ilwfeN6tg/EV4+P09Tlrw3pfP3/AEP3Hw57T8bIZVZDqOCsxgpaVbSko9ou04yS7XT+ZqfbvRcREYOsXmP8aIH+MIt3566bqmvahq8oWWa81GYncsRaa6cHGMpCN+33ewg6/Gtso7rvDmc/gXTfvtYiPyFcfmruvDXA9lYoEtLS2tUHRbeCKFR90arXOunYktsSe31b/ifQy9qHScsteQ6ZGOJ2bWHCvvCLf8DyPuYaJq1posVtqsBgaB2S0V3DTeqnmiyquRGUJKIpYt4YTO0givealK9zDhoio+m25/PvUM487mcTNSjGLnJycYqopyduk29vuWlSrWh54pSlAK4ydD8jXKuEnQ/I0ByFWoKtAKVKUAq0pQEpVpQEpVpQClTNM0BaVM0oC1KtKAlKtKAlWpTNAWlSlAWlSlAKVaUBKVamaAtKlM0BaVM0oC0pSgJSrSgJSlKAtKmaZoC0qUoC1KtKAmKVaUBKtSlAWlSmaAtKlWgJTFWlASrXlveU0DVLjSLk6Ndz2mo249ZgMAhLXPhAs9ownR48XCZRWIUpJsbcAGB1df8AK94oPP8ADl6PgY7NSPgQbQEEeYIBB5GrxjZnKek3H3sO5TjqOY/3ffXXWuKwt7jHfBu7q+k0nWbyS6e7zJYXUwhUrMiqHsj4SRA+KgM0JKMdyTqXG6FTmfxPblD4ij2Sefwb3/I/y/OlU6Yu1aNRHeyP9VfEH7tt/wDVenV/buptjibQ/wB3f/lriu794ru+a9e8Q6vd2ulXNxbXNzDJDPG1sEkVbGzhYgPOj8pInXmo6e7Br9Hd67u+u2Wu6RdXWk3Vvbw3fiSzO1sUSPwZl3nZcO23cyr7Kk5IyAMkdLqvt+hhvZszF1VFzXx/WfjXIXVc9Gtn2BcVRPX44YiQDuALAlV55YLnPwHQ4yeeK/PHecxUUTZ5ddarh3/x3/0jVXWfjXS9S1j6STn/AHR/9M1+j1/wFEj4MjDMcZ6AHpJIPd+Kp69Ty66UUPQItaEAy312GAh8lP2nHx8l+/3Vw/C5my7sFRcAsBgD3Ig82PkPvNec2V6ZS0kjkIpzJIeZyeir+NI3kPLqcAV/ReIGnO1cRwxjOT9WNfxmx9aRj7ubHkOQ5KJs7yuuoekTEftjZ+/C1z/Daf3lv47f8FdKXjZiyxwFo1LBVwdrOzEDdIR1JPl0Ucq+odXnYExXLy7WKvh3Ta38MrlTzwR+QVBGx999fQf3Fv47f8FetcBaSI4RIU2PKAxUkkhfsg5AIODkjHInHlXmvZjol1dT75nl8CIhmzISJH6rHyY8vtNnywPtV1nvedvcumrFYWExivJNs00qBS0EAJ2KNwZRJOykYIJEaseW9DVXvsXWytmTGaVrHPeS14f/AErc/kg/8qs0u65BqcmnreapdTXEt5tlgjl2AQ22PojhEX25gTIc9EMYwCGzDjRMZ3wezVamaZqhoWlSlAWpVpQEpirSgFKlM0BaVM0oC0qVaAVKtKAlKUoBVqZpQFpUpQFqVaUBKVaUBKtKlAWuE0W4Ee8EflGK5UzQLYwyX0ZGngY/CmoY/wAS1/8AJrKzs74MTS7G0sI3aRLO3it0kfAd1iQIGYKAu4gZOABmuw0rnw8vh4buCp/f9T6TqniPqXVYRw89jyxIxdxTrZ1XZLsKVaV0HzZMUxVqUBaVKZoC0qZpQFqUpQClWlAKlWpQCrUpmgLSpVoBSpVoBXCXofka51wl6H5GgOQq1BVoBSlKAUpSgFSrSgJTFWlASlWlAKlWlAKlKtASlWlATFMVaUBKtKlAWlSlAWpSrQEpVpQExSrSgJSrSgFKVKAZpVpQEpirSgJilWlAKVKUBalWlASlWlATFMUq0AqVaUApSlASlWlAStW3f+7uB0jUPwraR40/U5WMqoh222ovvlm3FcqsV5zlUsFAn8VdxMsS1tKrrnaFwBa6vZz2F7EJbe4Ta6nGVIIZJIyQdk0ThZI5BzR1VhzFWjKislaNGEOUZHVikkbpLG6nDRyxsJI5EPlJG6q6t9llB8q25d0fvGRcT6dsnMY1K1RI7+EHG/ORHdxp1ENxtLcsiOUSR5OwM2sTtp7Irrh7UZtOuwWMeHguNoVLu3b6lxGATjnlJEODHKjjG3Yz/N7Nu1K90O9h1CwcLcQE+w5YQzxsMSW84QgtDIMZ67HVJAN0a43a1I5oycWbgte01oH2/ZPNW94/3jz/AC+dfktNSAG18lD7vrIfxl+PvHRh91f07JO1mw4s0xLu1YgElJoXwJ7O5Ue3FIPeucq4zHNGyupZXBr4+sWT28hjcc/snyZfJh/u6g1Rb7M0ltufXSAmRY8jDn2XHNWX3j3/AOL1zyqXeFCspJVt31htYFTg8skY59c+8eVflnuD6vCRyIebBBwR9Q8j5GvvQ6OLq5kV3YBUQgA+0cqvIZyAASSeXU/HNLI+h+az1JhDJz+qyKDgZAfduAOMgNjnj/fX4otQ5j51/W+tfCS5QHdslhGff9f8/kfjmvhLOcj51Ibo8KTV0D3UpwxikOxT9Xc8xUMw8wnXb0Jxmvx2dw07PJJIVQHdLKefM9FUfakboqDp8AK6Je6vgajzxiZf0phX5J+Iz6pAN3Lxbg4zyyBEAfmByq1Gdno8utG5YIuIbeIE8zlY0+07n7crn72OFHIV8/U+Jw2IoQREp9lftSOeXiP73boB0Uch5mumabxJ+p7rP/2f+cNfp0y8jjVZ5uYPOGLODMQfrNjmsKnqeRcjA8zSibO4X8ZiG7xEbY/hvsLZjk5kDmBn6pwy5GQa+pwzBdatcR2sZ3MSWZtoCRL9uaTaBnHIZPNmKqDk103SLu71WeO1gRZJZXLBERYxno80pUD2EByztnAOBksAcvuH9A0/hTTZbi5lUbVV7q5K+3LJ0SKJR7RXcdkUIySWyclmNVbotGN/Q49o/HNnwnpO5QGZQY7WEn27m5YE5cjntzmSVwMIgOB9VTrc13iua8mlubhzJNPI0krnzZj0A+yijCqo5KoVRyFfa7ae2G41+9a7mzHGoKW1tuytvDn6vXaZXI3SyD6zAD6qIB1vhDhS51K6hsrRPEuJ22xqThQANzSSNg7Yo1Bd2wcAYAJKqbRVKyspW9j13uxdjx12/XxFJsbUrLdt9lznMdr8TMQd4HSIP0LJnZOkYAAAwByAHIADoBXTOx/sqt9DsYrO3GdvtzTEAPcTsBvlfHmcBVGTsjVEHJRXdqxlK2dEI0iYpirSqFyYq0qZoC0qVaAmaGrSgJimKtKAmKVaUApSlASlWlASmKtKAmKYq0oBSlSgLSlSgFKtKAlMVaUBMVaUoCValWgFSrSgJSrSgJilKtATFWlKAUpSgJSlWgJTFWlATFKtKAUpSgFKUoBXGTofka5Vwk6H5GgOQq1BVoBSlKAUpSgFSlKAUq1KAUpVoCUFWlAKlWlASrUpigFKtKAlKtKAlWlKAUpUoBTNKUAzSlWgJSrSgFKlKAtSlKAUzSrQEzSrSgJVpSgFKlKAZpmlKAUpVoCUq0oBSlKAVKUxQCmaYpQHjnee7uFtxTYeA7eBeQFpbG7AyYZcYMcg5eJazckljPltddrxxuuoTi/g26025msr6Fre6t3KSxnmM+TxvgeJBIPbjlAAdCDgHKje/Xgfer7qVtxPbiSMpb6nAuLa62jEijJ9WucDc9uSSVIO6JzuXILo+kZVszKcL3RrE7DO2u94bv1vrM7gwEd1auxEN3BuDGOQDIWVeZinCl4WLYDK8scm23s27SdN4p09Lq0fcp9mRDhbi0nAG6KVee11z8UkQhlLqysdNHFPDdzp9zLZ3kD213AQs0Em0shI3KcozI6MOayRsyMOYJ5193sn7ZNR4fvFvdOm2SAbJYZNzW11F18O4iVlDgHnHICJIWJKsA8ivo42ZRlWzNsnFGiPbRRI5ziSYhh0YER4+R5H2T7j161+hL0DUEA/Y/zAr4/YJ3jtL4vtXWMeHcxget6fMR40JPSWNuQmgY/UuIuQOVbw3VkHa7/guSO8jnQb4ieZ+1HiIoNw8wcD2h5nmB1qt9mXa7o6hbakTbTH9nb/AJ/Er6/EGgrbxRyLKWLFQfq4bIySmOeB8zyrrunL+pJuf27b/wASv7X6fQ2n+LL/ADzVYp2MG7/VwfwmP8OB/wD9bV8y81MC1gwf7rcfyQ11XXdYKtqg/wDtLD8l49fJm139TQA+Us/8kVXM7O/6fqZ9Xuv/APH/AJw12jhng691ie0tLGIySeqRl3ORDAnizfSTyAERpyIA5s5BCqxr9Pdu7ut/xCjSYe002Twj68wB8ZUclltEJzKxHSYr4Ckg5lKtHWbmvcR6JwPpibvoY+SRRriS8vZgv3NLJgZZ2KxxLzJjUACjlWy5Lxje74P58G8G6Zwdp0txcTqCqhru9kGHmb7EMKDJwW9mK3j3M7EE72JasC+8D3jbniK63sDDZQswtLXdkKMsPHlwPauZEODzKxL7CZy7yfC7c+8Fe8R3AmuW8KCIn1azjdjDCD9tgcCa5I5GdlBAyqCNWYN53Y2kkzpFEjySysEjijUtJI7fVRFHNmPuFTGNbvkSley4Pq6ckk0kcUSPLLK6xxRoNzySOcKiqOrMeX+4AmtmXdY7uS6BbGa42yalcqpuHHNbdORFrEfNVbnJIP1x+f1UjC9Z7pndIXRFW/1AJLqki+yvJ47FGHOOJuYa4YZEkynGCUT2dzSZNYrOcr2RrCFbstM0xTFZGwpSrQEpVpQClKlAWpTFKAZpSlABSrSgJVpSgFKVKAUzSlAKUq0BKVaUBKtKUAqUpQCmatSgFKtKAmKtKUApUpQClMUoAaUxVoCUxVpQEq0qUBalKUApSrQEpirSgJVpSgFKUoBXCTofka51xk6H5GgKKUpQClWlAKUpQClSlAWpSlAM0zSrQEpVpQClKUApUpQFqZpilAM0zTFKAValWgFKVKAtSlMUApmmKYoBmmaUoC0pSgFKmaUAzTNKYoBmmaYq0BKtKUApSpQFqUpQDNM0xTFAM0pVoCVaUoBSpSgLUzSmKAZpmlWgPEu813VrHiq3US/qa/gB9Uv41BePzMMy8vGtJDjfESCPrI0bgMNU/al2R32hXb2WoQmKUAtG4y0FxFnAmt5cASJ7xyeMkB1QkZ3iV0vtY7HNO1+1NpqNuk8YJaJ/qzW8hUr4tvMBvhl2sy7kIyrMp3KzKdIyrkzlC+DShoPEM9lNHc2s8ttcwndFPC22WNveDghlOPajdWjcey6upKnYT3dPSNWt0EtNfMdjcZCx6gMrZT4TO64OAtjKSGBLsbdjtxIjOIlxg7yPcz1LhkvcJvv9KVSxv1CCS2VcZF9EuNnLLesxJ6vhWLer+wreCCLNa0pGCbizeRr/AAVFcxOYCkbS7H3LzjfZkqcA49rcfaXr1515rxRpc9slskinKiQFhzTJlJGG6cwQQDg/CtdXYR3s9X4bxHby+tWW4FrC7eR4lUAAraSZL2fQezGrwA7mMLM7NWwrsY76GhcQ7bcyi0vZBg2N7tUyHnkQSn6C5HInajeIF5tGlU3iabS+TNdHD3Bl/rF7qVpp9pLdzG8kVvDAEcWLxzunmYrFCoU7vbcMV+qGOAc2ewv0ftpapDNrZjv7hCZBaJu9Rid1XcJN21rsqRy8VEiPI+ESAR6bx/258OcHxNbjwIZSZJl07T4kM8kkjNI8kkce1Y2lkLM09yyB3YksxNYJdvXfa1fXd8ELNplgSPobWWRbqVVYnFzdoUYo427oIVjQgMjtOrEGbcuCumMedzLvvDd+Cw0VXs9MEV9foAm1G/Udp5fSyRgh5IwMi2iOcgK7wBg1a6eOOObzVbp7y/uHubmTkXfACJuLLFEigJFCmSFRQPMksxZ26xF7IAHIDoB0FeudgXdt1PiaQeqoIbJWdZtRlG6CNkO1o4kDq9zPuyCkZCIVYSSREKr3SUUVbcmdH4P4Su9SuYrOyge4uZj7EcY6KMbpJG+rHCmRvlchVyOeSoOzfut90i34dQXNyy3WqyLh5sfRWqsBugtARnHUPOwEkvTCJtjXv3Yn3f8ATuHIPCsosyuFFxdyhWurkrkjxZAq4RSWKRIFjTJ2qMkn0mspTvg2hCt2SrUpWRqWpmlMUAzTNKUAzSrSgFKUoBUpSgGaZpTFAM0pSgFWlKAUpUoC1KUoBmmaUoBmlKtASrSlAKVKUApmlMUAzTNKUAzSmKtAKVKUBaVKUApmmKYoBmmaVaAUpSgFKlKAtTNKUAzSlKAUq0oBSlSgLXGTofka5Vwk6H5GgOQq1BSgLSlKAUpSgFKUoBSpSgLSpSgFWpVoBSpVoCVaVKAtKmaUBaVKUBalKtASrSlAKVKZoC0qUoC0qUoC0pSgFKUoBSpTNAWlSlAKUpQClWlAKUqUBaVKUBaVKUAq0pQClShNAWlSmaAtSlKAtKlKAjoCCCAQRggjIIPUEe6sPe8F6O2y1Fnu9HdNNu23O9sVJsLh2OSdigvayE/agBj9piYXY7hmHVqU2uCGk+TRn2k9l+oaJceralaS2spOEZxmCfkxzb3C5hn5KWKoxdB9dU6V1SS3DAhgCD1BAIPzB61vb4y4Hs9Tge1v7W3vLaTG+G5iSaMlSGVtkgYB0YBlYYZWAYEEA1hv2x+jNt5i82iXZtHJJ9Tu901tn2iRFMP1RBkkfX9YVQMKqCt1iLuc8sN9jAEDmT1LHLE8yxPUknmSfMnma+zwjwjd6lOLaxtZ7y4bn4UCbyowSGkY4jhjO0jxJnjTIxuyQKzP7IvRpOdkuuXgAGCbKwJ546rLeOoYqfMQRRsPKUVmj2f9mGn6PD4GnWcFpETucQxqjSvgKZJnA3zSkAAySMzkADOAMHNLgLDb5MR+wn0ckURjutfkW4cDI06Bj6qGypBuJsLJcEbceEnhwkMwYTjaRmxp2nRwRpFEiRRRqEjjjUIiKowFVVACqB0AAFfoFKwbbN1FLgValWoLEq0pQClSmaAtKlKAtTNKUBaUpQClKlAKtSmaAtSlKAVamKtASrSlAKVM0oC0qUoC0qUoC1KtKAUpSgFKmaZoC0qUoC0qYq0ApSlAKUqUBaVKUBaVKUBaVBVoBSlKAUqUoC0qUoC0qUoC0pSgFcZOh+Rq1xk6H5GgOQq1BVoBSlKAUpSgFSrSgFKUoBSlKAUqUoC0pSgJVpSgJTFWlAKVKUBaVKtAKlWlASmKtKAlWpSgLSlSgLSlKAVKtKAmKYq0oBSlSgLSpSgP5XdxsRn67VZse/Azj81eear25W9vY2F/LHIsN88a/ZZoBJG8m+QD6yoEO7Zk+YBxXfdXH0Uv7W/+ia8P03Tw+mcLo8e4es2wdGTI2m0uVYOpGApzghhjnjzqyKNvses6/wAax27WQCmUXtwsEboy7V3RSSiQn7SFY8DbnORXWtU7UbqCaKBtKn33EkkcH6ptcS+Epcn9c9gFBuG/b7uvKum6nwxPp97plmqtLp41BZ7ST2ma1+hmV7Rzz+iBffCxwAuU57RXde0KMnUtDIBIFzd5IBwB6nJ19wzy50oi2fq1btGnha0i/B8rXN2twwtxPbgxi3K53SF/CO5WVhtY4zjrX6v6OJ47e6uLmxltltoWmCtNBIZQiuzKvhOwUgKPr4B3D3HHS+2po1v9Laee4toRFfBp7YyCRCVgCruiSRgHPIjbg4rn+EbWTS9Vitby7vWFrMzG68d3XfC6qqGWKP2SUPsru5+7IpQt2eqaJqguIYpgColjSQA9QHUMAccsjOK+ZwXxgt+kzqjIIbq4tSGIJZreQxs4x9liMgHnius8C9qtgYrS2WZvGMcEIQ29yv0mxV27mhCDnyyWA+NdZ7Nu0iysEvYbmVopPwnqEm3wLhvZe4Yq2UiZSCOYwaii1npltxijXs9ntKm3t4bhpCRsKzNIoGOoK+GSSeWCPjXXLftXlnDS2em3V1aqTi4DwReMFJBa3ildZJU5Ha2FD+Wa+JLYNd6nqyIzKtzo1rHHLtYAGX1tQwyBzXcGI6j4V/PhHtZgsrKKzu1ltL22gW3aD1eZ97xJsV7do43SWKTaGQq3Q8wKmiuo7bxP2kG3Fl4dpPNJfMyxQkxwSKVjMpEglZQrBQcqTkEYr9OncYXJSeS40+W1WGJpQXnt5PEKgsUURO5U4HVgBXlnFtzLJbcPS6jJc28vtNdywq8c8UrWrZ5RRsUJc7SAmMEjlXauGNVs3gvora9vbx2tpHIuzcOUUIy/RmWGMDcWGVBJPLlyNKCe52HhDtVt7+xa+hDERpI0sJIEsbxqXaN/IEgAq3RlII6186/7V5VtIb2PTppreSzS8d1mt18JWTxCjK7hmZFwSUBBzyzXQ4eDZbbTbbUbJCZH01Ib+1GVF1D4G0S7fO8txzViCzoGT3A9whhI4ZCgHI0cDGDnPqmMY65+HWppEWztfBnFc92N0llLaxlEeN5JYJBIH5gAROzKQMH2gOtfobi1fXhY7G3m1N14mRt2iURbMdd2TnPTFf24OBFpa56+rw/za11J4T/RApwcfghhnBxn1teWemfhVS+59bs67T7fVFl8LKSwSNHLC5G9cMQrjHJo3wSGHmCDgg1+Cx7XI3WykaCRIry6ntBIWUiGWJ5UTxP2M7RMFI6EqD1rzzgng2b1CG/sl239rPfDYfYF5beuzs9pLnGdww0LtyR8Hoc19jgfhg6noDQMrwSSy3kkRYFZIJ1vJpYW6BlaOQLzGD199WpFE2z0nivi9bRrZPDaWW7uEgjjQgEZBaSViekUMal2PM9AObCuu23adczSXC2+mTTpbXEts0guLWMGSLGcLJIrYIZSOXn8K+H2V6lNq1z+ELmF4fVLcWccUi7cXb7XvpQOnIqkKMPsiTmQ1dN0qe0W41MXWo6jZudSuisVq9xHGyEpiTEcDqWYhhu3ZIUcuQpRNnrmt9orQtbQLaSy3tzE8wtVkhHhRx7BI8szN4QVXdEypbcx5A1/ReMbwxFxpdx4qy+G0JntR7Ozd4ySmXw3jyQnUNuz7PI11Xj640uYWc0895bt4Ra11G3FxE6qdoZHmWMgGTAZop02tjJHkfrdkOtTzetK08t3axvGLS8mi8GWYFMyqQEjEixtgCURoGyeuKjsTbs58E9p09+w26bPHCJZYZJ2ntisbwsySAosniNh1K5VSD15jnX1ezjtGh1WGSSJWjaKV4ZYnI3oyn2Ty5FXXDKR8R1UgfK7EY9trOCCP6Y6geYx1u5Dnn5HyPnXn3CmjXsFnb3umxB7mTx7S4ic7EZGuZhb3Tg9WtHbJ5FmhZ18lwoW9j1PSe0yC4vbuyjDM9nGjyyDGws2cxr5lk5bj0BJHVTj4vD/AGqXd3DHcQaRO8Uq7kY3Vou4ZI6NICOY8wK+RwXwqthqM8Ee5lTSbfdKwJeaU3Fw0ssjfalkcl2JJOT8q6J2Y61YQWdobjVNUgljUM9uhuvBUq5bw9i2zAxkdVDHIJ51NIi2e13vafBFqKabICkkkKyRSsR4bszMBD7xIQhK55N0HPAP6NQ43K3U9pHbvNNDZx3ihXjUSiSWWIRKXICvmIncxC4I59a6NxBwhHqWq3kMobw5NLtWjlUFXilW4mMc0L4yk0ZIYEYI6HkTX5+zBLwavcJfAmaDTbe38cAhLpI7qdkuV8g0iyAOmcrIrfCopC2fetu1i6eeW2XSbgzQrG8q+s2nsLLu2HJlAOdrcgSRjniu48Y8TLY2k926M628TSsikbmCjJAJ5ZrrXDcX9OdTODg29hzxyOBNkA9Dj81fq7bB/SjUeRP6km5KMk+weQAySfuoTvTPw/8A8VZYhHJd6dcWtvI0aesGW3mSMykLGZVikZ0jLMAX2kKSM4r9eqdosy3U9rb2E101ukLyMk0EYAmUsgAldCT7J6Z6V8r+ga/vYYYby7g9V+hd4ra2eOWURlJFieWSeUKhKgPtjDMMjK5r8Zsb5tW1I2clvF9DYhjcQSShj4cu3YUli2457vr9RyGObYjc7JYdrNq1rc3MokthZuY7qGZfpYZQFIj2oWEjSB08Pwywk3LjmcV8qftfmij9ZuNKvYbP6zTloXkjjPSSW1jdpkQDBbAZkGcqMGujQ8Kz3Om3ThHl1RNTgvL63faglms5ImFvF0QwPBGhgOSGO3JB3Adu1ztttJreSKCK4nu5I2jWx9WmWbxHUrsl3osaKpPtOz7MA4JqaItn2uMe02SzRp1spLi0VI3FzHPbhGEm0LtVnDkZYDO3BznpU1ftKmtbWS5uNPmi2SQRxxePbu0pnkWIFWR2VQrMud5HX4V1ni/heW04cFq+XkhtrWJtuWyySxbgMcyAcgfAV9ft8jzpTfXA8eyJKZ3qouoSzLtBOVGWBAJGM4qNi1v8jsOhcUXksoSXTZreMhszNcWsiqQCQNscjOdx5DA5Z54r4w7V5J3lFhp9xexQO8UlwskEETSRnbIkJmdTMUYbSyjZkEBjXzuBtZ0/1gJDqeoXMsqPGsVy9w8fTeWAeBEDqEOGLDkSPOvwcB8eQaPbiw1ASWstu8io5hlkjuozIzJNE8SOGLg5ZDhw2QRQWdk1vtNmhtxdLpt00CwNPMXeCGSDwy/iI8UkgcsqpuygYMCMZrjL2pSx2VxfT6fLDDDbC5TM9u7TKRu2qEdijbSD7YA549+P68dav63ot9KkcyeJYXexJY2jlx4UgUmM+0N2MqCMkEch0r4PaRCx4ZnUBix0pBtAJbPgpyx1z8MUIbf5HbeKu0WO1MESxS3N1cqWhtYApkZFALyOzFUjhTcAZHYDJAGTX5tI7S83Edrd2s1jPNu9X8Vo5IpyilnSOaFmTxVUFvDbaxUEjODXWdZkbT9Rt9Rlikks5dOS0lljRpWtHSQSq7RoGk8CUMQzIp2soyMEGrq/FEesXNhHYq80Vtdrd3F34ckcUKxI4WNHkVTJLKzBNsYbC5JIpQs7Rw12qW91e3dhho7i1fGHxiZAqlniIPPYXAZT7QyD0Oa+tw7xat1NeQqjKbOdYGJIIctEku5ccwMOBz55Bry7TeCWvZdZaNjBd2+r+NZXG0jZItlZ8ieRe2lwY5UBwyk+YGPrdhN/NNJq0lxCbeZr5BJEckK6WsKPsbHtRsylkYZBUg5NKJTZ6zSpSqly1KtKAmKVaUBMVaUoBSpSgLSlKAlMVaUBMUxVqUBaVKZoC0qVaAVKtKAlMValAKtSmaAtKlKAtKUoCUq0oCYpVqUAq0qUBaUpQClKUBKknQ/I1yri/Q/KgKBVriKooC0pXFqA5UrialAcqtcTXKgFSlKAYq0pQClShoC0qGhoC1KtSgFKCrQEq1DQ0BaVBQUBaVBQUBalKUBalWoKAtSlBQFpXGgoDlUpSgFKlWgFWuJqCgOdK41GoDnSuFUUByqVxpQHKlcRQUBzpXE1KA51K40NAc6lQUoDlSuNSgOWKVxoaA50rhSgOdK4UNAciKVxqGgOdK40oDlVrhQ0BzpXCgoDnSuNSgOVK40oDnUxXGlAc6lcaUBzqYrjQ0BzqVxqmgLTFcaUBzpXEUFAWrXA0oDnSuFKA5UriKtAWlWoKAVa4rVFAWlcRVoC0rjVFAWpSlAKtQ1KA5UqGuIoDnUpQ0ApSo1AWlRqpoC0qGhoC0qCrQEpUrlQCpVqCgLSpRaAtK4rUoDnSuK1yoBXCTofka51wf8A30B//9k="
    st.markdown(
        f'''
        <div style="padding:0.75rem 1rem 0.5rem; background:#B71C2A;">
            <img src="data:image/jpeg;base64,{_LOGO_B64}"
                 style="width:100%; max-width:200px; display:block; margin:0 auto;"
                 alt="InvestCopilot Mapfre" />
        </div>
        <div class="ic-divider"></div>
        ''',
        unsafe_allow_html=True,
    )

    # ── Nav ────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="padding:0.5rem 0;">
            <div class="ic-nav-item active">
                <span class="ic-nav-icon">📋</span> Decisiones
            </div>
            <div class="ic-nav-item">
                <span class="ic-nav-icon">📊</span> Analytics
                <span style="margin-left:auto; font-size:0.7rem; opacity:0.4;">próximo</span>
            </div>
            <div class="ic-nav-item">
                <span class="ic-nav-icon">⚙️</span> Configuración
                <span style="margin-left:auto; font-size:0.7rem; opacity:0.4;">próximo</span>
            </div>
        </div>
        <div class="ic-divider"></div>
        """,
        unsafe_allow_html=True,
    )

    # ── Caso activo ─────────────────────────────────────────
    _alias_now = leer_alias_decision(_dec_id_now)
    _alias_html = (f'<div style="font-size:0.75rem; color:#a5b4fc; margin-top:0.15rem; '
                   f'font-style:italic;">{_alias_now}</div>') if _alias_now else ""
    st.markdown(
        f"""
        <div style="padding:0.6rem 1rem;">
            <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.08em;
                        opacity:0.45; margin-bottom:0.35rem;">Caso activo</div>
            <div style="font-size:0.82rem; font-weight:600; color:white;">{_dec_id_now}</div>
            {_alias_html}
            <div style="font-size:0.75rem; opacity:0.5; margin-top:0.2rem;">
                <span class="ic-status-dot" style="background:#10b981;"></span>
                {_llm_mode_now}
            </div>
        </div>
        <div class="ic-divider"></div>
        """,
        unsafe_allow_html=True,
    )

    # ── Acciones rápidas ────────────────────────────────────
    st.markdown(
        """
        <div style="padding:0.3rem 1rem 0.1rem; font-size:0.7rem; text-transform:uppercase;
                    letter-spacing:0.08em; opacity:0.45;">Acciones</div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("▶  Ejecutar flujo completo", use_container_width=True):
        prog = st.empty()
        answer = respuesta_ejecutar_flujo(placeholder=prog)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.button("📄  Resumen del caso", use_container_width=True):
        st.session_state.messages.append(
            {"role": "assistant", "content": respuesta_resumen_decision()}
        )
        st.rerun()

    # ── Confirmación humana ─────────────────────────────────
    _aprobacion_path = PROJECT_DIR / "01_decision_input" / "decisiones" / f"{_dec_id_now}_aprobacion.json"
    if _dec_id_now == "DECISION_001":
        _aprobacion_path = PROJECT_DIR / "01_decision_input" / f"{_dec_id_now}_aprobacion.json"

    _sintesis_existe = any([
        (PROJECT_DIR / "06_sintesis_comite" / f"{_dec_id_now}_sintesis_llm_data.json").exists(),
        (PROJECT_DIR / "06_sintesis_comite" / f"{_dec_id_now}_sintesis.json").exists(),
        (PROJECT_DIR / "06_sintesis_comite" / f"{_dec_id_now}_sintesis_llm.md").exists(),
    ])

    if _sintesis_existe:
        st.markdown("<div class='ic-divider'></div>", unsafe_allow_html=True)
        if _aprobacion_path.exists():
            with open(_aprobacion_path, "r", encoding="utf-8") as _f:
                _ap = json.load(_f)
            st.markdown(
                f"""<div style="padding:0.5rem 1rem; font-size:0.78rem; color:#10b981;">
                ✅ Revisado · {_ap.get('timestamp','')}</div>""",
                unsafe_allow_html=True,
            )
        else:
            if st.button("✅ He revisado este análisis", use_container_width=True, type="primary"):
                _aprobacion_path.parent.mkdir(parents=True, exist_ok=True)
                with open(_aprobacion_path, "w", encoding="utf-8") as _f:
                    json.dump({
                        "decision_id": _dec_id_now,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "revisado_por": "gestor (sesión web)",
                        "advertencia": (
                            "El gestor confirma haber revisado el análisis generado por InvestCopilot. "
                            "Este registro no sustituye la aprobación formal del comité ni constituye "
                            "una instrucción de ejecución."
                        ),
                    }, _f, ensure_ascii=False, indent=2)
                st.rerun()

    # ── Coste de hoy ─────────────────────────────────────────
    try:
        _agents_mcp = PROJECT_DIR / "08_agents_mcp"
        if str(_agents_mcp) not in sys.path:
            sys.path.insert(0, str(_agents_mcp))
        from cost_tracker import get_today_summary
        _cost = get_today_summary()
        _pct = _cost["pct_cap"]
        _status = _cost["status"]
        _color = "#ef4444" if _status == "cap" else ("#f59e0b" if _status == "warn" else "#6ee7b7")
        st.markdown(
            f"""
            <div style="margin:0.75rem 0 0.5rem 0; padding:0.6rem 0.75rem;
                        background:rgba(0,0,0,0.25); border-radius:6px;
                        border-left:3px solid {_color};">
                <div style="font-size:0.7rem; color:rgba(255,255,255,0.55); margin-bottom:0.2rem;">
                    Coste hoy (LLM + Search)
                </div>
                <div style="font-size:0.82rem; font-weight:600; color:white;">
                    {_cost['total_cost_eur']:.4f} EUR
                    <span style="font-size:0.7rem; font-weight:400; color:rgba(255,255,255,0.5);">
                     / {_cost['cap_eur']:.1f} EUR cap ({_pct}%)
                    </span>
                </div>
                <div style="font-size:0.68rem; color:rgba(255,255,255,0.45); margin-top:0.15rem;">
                    {_cost['llm_calls']} llamadas · {_cost['search_queries']} búsquedas
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        pass  # nunca romper la UI por el widget de costes

    # ── Footer ──────────────────────────────────────────────
    st.markdown(
        """
        <div style="position:fixed; bottom:0; width:inherit; padding:0.75rem 1rem;
                    background:#B71C2A; border-top:1px solid rgba(255,255,255,0.07);">
            <div style="font-size:0.75rem; font-weight:600; color:white;">Mario Encinar del Pozo</div>
            <div style="font-size:0.7rem; opacity:0.45; color:white; margin-top:0.1rem;">
                InvestCopilot analiza · La persona decide
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MAIN — cabecera
# ============================================================

_fondos = cargar_fondos_disponibles()

hdr_left, hdr_right = st.columns([7, 2])
with hdr_left:
    st.markdown(
        f"""
        <div class="ic-breadcrumb">
            Home <span>›</span> Decisiones <span>›</span> {_dec_id_now}
        </div>
        <div class="ic-page-title">Decisiones</div>
        <div class="ic-page-subtitle">
            Análisis multiagente de hipótesis de inversión ·
            <span class="ic-status-dot"></span>{_llm_mode_now}
        </div>
        """,
        unsafe_allow_html=True,
    )
with hdr_right:
    st.markdown("<div style='padding-top:1.4rem'></div>", unsafe_allow_html=True)
    if st.button("＋ Nueva decisión", type="primary", use_container_width=True):
        st.session_state["show_nueva_decision"] = not st.session_state.get("show_nueva_decision", False)
        st.session_state["pending_scenario"] = None

st.markdown("<hr style='border-color:#e5e7eb; margin:0.5rem 0 1rem 0;'>", unsafe_allow_html=True)


# ============================================================
# MAIN — formulario nueva decisión (inline, toggle)
# ============================================================

if st.session_state.get("show_nueva_decision"):
    with st.container():
        st.markdown(
            "<div class='ic-form-card'><div class='ic-form-title'>Nueva hipótesis de inversión</div>",
            unsafe_allow_html=True,
        )

        with st.form("form_nueva_decision", clear_on_submit=False):
            hipotesis_texto = st.text_area(
                "Hipótesis",
                placeholder="Ej: Evaluar si tiene sentido aumentar en 2 p.p. la exposición al sector Salud en BAM.",
                height=90,
                label_visibility="collapsed",
            )

            if _fondos:
                fondo_idx = st.selectbox(
                    "Fondo",
                    options=range(len(_fondos)),
                    format_func=lambda i: f"{_fondos[i]['nombre']} ({_fondos[i]['codigo']})",
                    label_visibility="visible",
                )
                fondo_elegido = _fondos[fondo_idx]
            else:
                fondo_elegido = None
                st.warning("No hay fondos registrados en fondos_disponibles.json.")

            fc1, fc2 = st.columns([3, 1])
            with fc1:
                enviado = st.form_submit_button("Lanzar análisis completo", type="primary", use_container_width=True)
            with fc2:
                cancelado = st.form_submit_button("Cancelar", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if cancelado:
            st.session_state["show_nueva_decision"] = False
            st.rerun()

        if enviado:
            if not hipotesis_texto.strip():
                st.error("Escribe una hipótesis antes de analizar.")
            elif fondo_elegido is None:
                st.error("No hay ningún fondo disponible.")
            else:
                nuevo_id = crear_decision(hipotesis_texto.strip(), fondo_elegido)
                st.session_state["decision_id"] = nuevo_id
                st.session_state["show_nueva_decision"] = False
                # Reset chat so old decision messages don't mix with the new one
                st.session_state.messages = []
                prog = st.empty()
                answer = respuesta_ejecutar_flujo(placeholder=prog, decision_id=nuevo_id)
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"**Nueva decisión** `{nuevo_id}` · {fondo_elegido['nombre']}\n\n{hipotesis_texto.strip()}",
                })
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()


# ============================================================
# MAIN — escenario refinado propuesto por el LLM
# ============================================================

_pending = st.session_state.get("pending_scenario")
if _pending:
    _fondo_ref = _fondos[0] if _fondos else {"nombre": "Fondmapfre Bolsa América", "codigo": "BAM"}
    st.markdown(
        f"""
        <div class="ic-scenario-card">
            <div class="ic-scenario-title">🔄 Escenario refinado propuesto</div>
            <div style="font-size:0.875rem; color:#78350f; margin-bottom:0.5rem;">
                {_pending.get('hipotesis','')}
            </div>
            {"<div style='font-size:0.78rem; color:#92400e; opacity:0.8;'>" + _pending.get('notas','') + "</div>" if _pending.get('notas') else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
    sc1, sc2, sc3 = st.columns([2, 1, 4])
    with sc1:
        if st.button("Lanzar análisis", type="primary", use_container_width=True):
            hip = _pending.get("hipotesis", "")
            nuevo_id = crear_decision(hip, _fondo_ref)
            st.session_state["decision_id"] = nuevo_id
            st.session_state["pending_scenario"] = None
            # Reset chat so prior decision messages don't mix with the new scenario
            st.session_state.messages = []
            prog = st.empty()
            answer = respuesta_ejecutar_flujo(placeholder=prog, decision_id=nuevo_id)
            st.session_state.messages.append({"role": "user", "content": f"**Escenario refinado**\n\n{hip}"})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
    with sc2:
        if st.button("Descartar", use_container_width=True):
            st.session_state["pending_scenario"] = None
            st.rerun()


# ============================================================
# MAIN — chat
# ============================================================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Barra de acciones post-ejecución ─────────────────────────────────────────

if st.session_state.get("show_post_exec_actions"):
    _dec_pa = decision_id_actual()
    _aprobacion_path_pa = PROJECT_DIR / "01_decision_input" / "decisiones" / f"{_dec_pa}_aprobacion.json"
    if _dec_pa == "DECISION_001":
        _aprobacion_path_pa = PROJECT_DIR / "01_decision_input" / f"{_dec_pa}_aprobacion.json"

    st.markdown(
        "<div style='background:white; border:1px solid #e5e7eb; border-radius:10px;"
        " padding:0.6rem 1rem; margin:0.5rem 0 0.25rem 0;'>"
        "<span style='font-size:0.78rem; color:#6b7280; font-weight:500;'>"
        "Análisis completado — acciones rápidas:</span></div>",
        unsafe_allow_html=True,
    )
    _pa_cols = st.columns(5)
    with _pa_cols[0]:
        if st.button("📄 Resumen", use_container_width=True):
            st.session_state.messages.append({"role": "assistant", "content": respuesta_resumen_decision()})
            st.rerun()
    with _pa_cols[1]:
        if st.button("📝 Síntesis", use_container_width=True):
            st.session_state.messages.append({"role": "assistant", "content": respuesta_sintesis()})
            st.rerun()
    with _pa_cols[2]:
        if st.button("⚠️ Alertas", use_container_width=True):
            st.session_state.messages.append({"role": "assistant", "content": respuesta_alertas()})
            st.rerun()
    with _pa_cols[3]:
        if st.button("📋 Mandatos", use_container_width=True):
            st.session_state.messages.append({"role": "assistant", "content": respuesta_mandatos()})
            st.rerun()
    with _pa_cols[4]:
        if _aprobacion_path_pa.exists():
            st.button("✅ Revisado", disabled=True, use_container_width=True)
        else:
            if st.button("✅ Marcar revisado", type="primary", use_container_width=True):
                _aprobacion_path_pa.parent.mkdir(parents=True, exist_ok=True)
                with open(_aprobacion_path_pa, "w", encoding="utf-8") as _f:
                    json.dump({
                        "decision_id": _dec_pa,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "revisado_por": "gestor (sesión web)",
                        "advertencia": (
                            "El gestor confirma haber revisado el análisis generado por InvestCopilot. "
                            "Este registro no sustituye la aprobación formal del comité ni constituye "
                            "una instrucción de ejecución."
                        ),
                    }, _f, ensure_ascii=False, indent=2)
                st.rerun()

user_question = st.chat_input("Pregunta a InvestCopilot sobre el caso activo…")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        prog = st.empty()
        with st.spinner("Consultando InvestCopilot…"):
            answer = responder_pregunta(user_question, placeholder=prog)
        prog.empty()
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.session_state.get("pending_scenario"):
        st.rerun()