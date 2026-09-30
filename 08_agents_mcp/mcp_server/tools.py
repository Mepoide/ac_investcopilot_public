from pathlib import Path
import json
import os
import pandas as pd
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

# Este archivo debe estar guardado en:
# 08_agents_mcp/mcp_server/tools.py

MCP_SERVER_DIR = Path(__file__).resolve().parent
AGENTS_MCP_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = Path(__file__).resolve().parents[2]

ORCHESTRATOR_PATH = AGENTS_MCP_DIR / "orchestrator" / "run_decision.py"

RISK_SCENARIO_TOOL_DIR = PROJECT_DIR / "04_portfolio_riesgo" / "metricas"
FIXED_INCOME_TOOL_DIR = PROJECT_DIR / "04_portfolio_riesgo" / "renta_fija"

for _dir in (RISK_SCENARIO_TOOL_DIR, FIXED_INCOME_TOOL_DIR):
    if str(_dir) not in sys.path:
        sys.path.append(str(_dir))


# ============================================================
# UTILIDADES INTERNAS
# ============================================================

def _resolver_ruta(ruta_relativa_o_absoluta: str | Path) -> Path:
    """
    Resuelve una ruta.

    Si la ruta es absoluta, se usa tal cual.
    Si la ruta es relativa, se interpreta como relativa a la carpeta raíz del proyecto:
    InvestCopilot_AI_Summit/
    """

    ruta = Path(ruta_relativa_o_absoluta)

    if ruta.is_absolute():
        return ruta

    return PROJECT_DIR / ruta


def _asegurar_padre(path: Path):
    """
    Crea la carpeta padre de un archivo si no existe.
    """

    path.parent.mkdir(parents=True, exist_ok=True)


def _respuesta_ok(tool_name: str, data: dict) -> dict:
    """
    Formato estándar de respuesta correcta.
    """

    return {
        "tool": tool_name,
        "status": "success",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "data": data,
    }


def _respuesta_error(tool_name: str, message: str, details: dict | None = None) -> dict:
    """
    Formato estándar de respuesta de error.
    """

    return {
        "tool": tool_name,
        "status": "error",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "message": message,
        "details": details or {},
    }


# ============================================================
# TOOL 1 - LISTAR ARCHIVOS
# ============================================================

def listar_archivos(ruta: str = ".", patron: str = "*", recursivo: bool = False) -> dict:
    """
    Lista archivos dentro de una carpeta del proyecto.

    Parámetros:
    - ruta: ruta relativa o absoluta.
    - patron: patrón tipo glob, por ejemplo "*.md", "*.json", "*.csv".
    - recursivo: si True, busca en subcarpetas.

    Ejemplo:
    listar_archivos("04_portfolio_riesgo/metricas", "*.csv")
    """

    tool_name = "listar_archivos"

    try:
        base = _resolver_ruta(ruta)

        if not base.exists():
            return _respuesta_error(
                tool_name,
                "La ruta indicada no existe.",
                {"ruta": str(base)}
            )

        if not base.is_dir():
            return _respuesta_error(
                tool_name,
                "La ruta indicada no es una carpeta.",
                {"ruta": str(base)}
            )

        if recursivo:
            paths = sorted(base.rglob(patron))
        else:
            paths = sorted(base.glob(patron))

        archivos = [
            {
                "nombre": p.name,
                "ruta": str(p),
                "ruta_relativa": str(p.relative_to(PROJECT_DIR)) if PROJECT_DIR in p.parents or p == PROJECT_DIR else str(p),
                "tipo": "directorio" if p.is_dir() else "archivo",
                "tamano_bytes": p.stat().st_size if p.is_file() else None,
            }
            for p in paths
        ]

        return _respuesta_ok(
            tool_name,
            {
                "ruta": str(base),
                "patron": patron,
                "recursivo": recursivo,
                "numero_resultados": len(archivos),
                "archivos": archivos,
            }
        )

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error listando archivos.",
            {"error": str(e)}
        )


# ============================================================
# TOOL 2 - LEER TEXTO
# ============================================================

def leer_texto(ruta: str) -> dict:
    """
    Lee un archivo de texto, Markdown o similar.

    Parámetros:
    - ruta: ruta relativa o absoluta del archivo.
    """

    tool_name = "leer_texto"

    try:
        path = _resolver_ruta(ruta)

        if not path.exists():
            return _respuesta_error(
                tool_name,
                "El archivo no existe.",
                {"ruta": str(path)}
            )

        if not path.is_file():
            return _respuesta_error(
                tool_name,
                "La ruta no corresponde a un archivo.",
                {"ruta": str(path)}
            )

        texto = path.read_text(encoding="utf-8", errors="ignore")

        return _respuesta_ok(
            tool_name,
            {
                "ruta": str(path),
                "nombre": path.name,
                "caracteres": len(texto),
                "contenido": texto,
            }
        )

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error leyendo archivo de texto.",
            {"ruta": ruta, "error": str(e)}
        )


# ============================================================
# TOOL 3 - LEER JSON
# ============================================================

def leer_json(ruta: str) -> dict:
    """
    Lee un archivo JSON.

    Parámetros:
    - ruta: ruta relativa o absoluta del archivo JSON.
    """

    tool_name = "leer_json"

    try:
        path = _resolver_ruta(ruta)

        if not path.exists():
            return _respuesta_error(
                tool_name,
                "El archivo JSON no existe.",
                {"ruta": str(path)}
            )

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return _respuesta_ok(
            tool_name,
            {
                "ruta": str(path),
                "nombre": path.name,
                "contenido": data,
            }
        )

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error leyendo archivo JSON.",
            {"ruta": ruta, "error": str(e)}
        )


# ============================================================
# TOOL 4 - LEER CSV
# ============================================================

def leer_csv(ruta: str, max_filas: int | None = 20) -> dict:
    """
    Lee un archivo CSV y devuelve una vista en formato registros.

    Parámetros:
    - ruta: ruta relativa o absoluta del archivo CSV.
    - max_filas: número máximo de filas a devolver. Si es None, devuelve todo.
    """

    tool_name = "leer_csv"

    try:
        path = _resolver_ruta(ruta)

        if not path.exists():
            return _respuesta_error(
                tool_name,
                "El archivo CSV no existe.",
                {"ruta": str(path)}
            )

        df = pd.read_csv(path)

        if max_filas is None:
            df_out = df.copy()
        else:
            df_out = df.head(max_filas).copy()

        return _respuesta_ok(
            tool_name,
            {
                "ruta": str(path),
                "nombre": path.name,
                "filas_totales": int(len(df)),
                "columnas": list(df.columns),
                "max_filas_devuelto": max_filas,
                "contenido": df_out.to_dict(orient="records"),
            }
        )

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error leyendo archivo CSV.",
            {"ruta": ruta, "error": str(e)}
        )


# ============================================================
# TOOL 5 - GUARDAR TEXTO
# ============================================================

def guardar_texto(ruta: str, contenido: str, sobrescribir: bool = True) -> dict:
    """
    Guarda contenido de texto en un archivo.

    Parámetros:
    - ruta: ruta relativa o absoluta.
    - contenido: texto a guardar.
    - sobrescribir: si False y el archivo existe, devuelve error.
    """

    tool_name = "guardar_texto"

    try:
        path = _resolver_ruta(ruta)

        if path.exists() and not sobrescribir:
            return _respuesta_error(
                tool_name,
                "El archivo ya existe y sobrescribir=False.",
                {"ruta": str(path)}
            )

        _asegurar_padre(path)

        path.write_text(contenido, encoding="utf-8")

        return _respuesta_ok(
            tool_name,
            {
                "ruta": str(path),
                "nombre": path.name,
                "caracteres_guardados": len(contenido),
                "sobrescribir": sobrescribir,
            }
        )

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error guardando archivo de texto.",
            {"ruta": ruta, "error": str(e)}
        )


# ============================================================
# TOOL 6 - GUARDAR JSON
# ============================================================

def guardar_json(ruta: str, contenido: dict | list, sobrescribir: bool = True) -> dict:
    """
    Guarda contenido JSON en un archivo.

    Parámetros:
    - ruta: ruta relativa o absoluta.
    - contenido: dict o list a guardar.
    - sobrescribir: si False y el archivo existe, devuelve error.
    """

    tool_name = "guardar_json"

    try:
        path = _resolver_ruta(ruta)

        if path.exists() and not sobrescribir:
            return _respuesta_error(
                tool_name,
                "El archivo ya existe y sobrescribir=False.",
                {"ruta": str(path)}
            )

        _asegurar_padre(path)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2, default=str)

        return _respuesta_ok(
            tool_name,
            {
                "ruta": str(path),
                "nombre": path.name,
                "sobrescribir": sobrescribir,
            }
        )

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error guardando archivo JSON.",
            {"ruta": ruta, "error": str(e)}
        )


# ============================================================
# TOOL 7 - LEER OUTPUT DE AGENTE
# ============================================================

def leer_output_agente(nombre_agente: str, formato: str = "json") -> dict:
    """
    Lee el output principal de un agente.

    Parámetros:
    - nombre_agente: macro, riesgo, mandatos, sintesis.
    - formato: json o md.
    """

    tool_name = "leer_output_agente"

    try:
        nombre = nombre_agente.lower().strip()
        formato = formato.lower().strip()

        rutas = {
            "macro": {
                "json": "03_macro_houseview/outputs_macro/DECISION_001_macro.json",
                "md": "03_macro_houseview/outputs_macro/DECISION_001_macro.md",
            },
            "riesgo": {
                "json": "04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.json",
                "md": "04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.md",
            },
            "risk": {
                "json": "04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.json",
                "md": "04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.md",
            },
            "mandatos": {
                "json": "05_mandatos_asset_allocation/outputs_mandatos/DECISION_001_mandatos.json",
                "md": "05_mandatos_asset_allocation/outputs_mandatos/DECISION_001_mandatos.md",
            },
            "sintesis": {
                "json": "06_sintesis_comite/DECISION_001_sintesis.json",
                "md": "06_sintesis_comite/DECISION_001_sintesis.md",
            },
            "synthesis": {
                "json": "06_sintesis_comite/DECISION_001_sintesis.json",
                "md": "06_sintesis_comite/DECISION_001_sintesis.md",
            },
        }

        if nombre not in rutas:
            return _respuesta_error(
                tool_name,
                "Agente no reconocido.",
                {
                    "nombre_agente": nombre_agente,
                    "agentes_validos": list(rutas.keys()),
                }
            )

        if formato not in ["json", "md"]:
            return _respuesta_error(
                tool_name,
                "Formato no reconocido. Usa 'json' o 'md'.",
                {"formato": formato}
            )

        ruta = rutas[nombre][formato]

        if formato == "json":
            return leer_json(ruta)

        return leer_texto(ruta)

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error leyendo output de agente.",
            {
                "nombre_agente": nombre_agente,
                "formato": formato,
                "error": str(e),
            }
        )


# ============================================================
# TOOL 8 - EJECUTAR ORQUESTADOR DECISION_001
# ============================================================

def ejecutar_orquestador_decision_001(decision_id: str = "DECISION_001") -> dict:
    """
    Ejecuta el orquestador completo para la decision_id indicada (por
    defecto DECISION_001, el caso de demo precalculado).

    Lanza:
    - Research Agent
    - Macro Agent
    - Risk Agent
    - Mandates Agent
    - Synthesis Agent

    Usa el script:
    08_agents_mcp/orchestrator/run_decision.py
    """

    tool_name = "ejecutar_orquestador_decision_001"

    try:
        if not ORCHESTRATOR_PATH.exists():
            return _respuesta_error(
                tool_name,
                "No se encuentra el orquestador.",
                {"ruta": str(ORCHESTRATOR_PATH)}
            )

        try:
            result = subprocess.run(
                [sys.executable, str(ORCHESTRATOR_PATH), "--decision-id", decision_id],
                cwd=str(PROJECT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=600,
            )
        except subprocess.TimeoutExpired as e:
            return _respuesta_error(
                tool_name,
                "El orquestador no terminó en 10 minutos (timeout). Puede ser un problema de red con el LLM.",
                {"stdout_parcial": (e.stdout or "")[-2000:], "stderr_parcial": (e.stderr or "")[-2000:]}
            )

        summary_json = AGENTS_MCP_DIR / "orchestrator" / f"run_{decision_id}_summary.json"
        summary_md = AGENTS_MCP_DIR / "orchestrator" / f"run_{decision_id}_summary.md"

        summary_data = None

        if summary_json.exists():
            with open(summary_json, "r", encoding="utf-8") as f:
                summary_data = json.load(f)

        return _respuesta_ok(
            tool_name,
            {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "summary_json": str(summary_json),
                "summary_md": str(summary_md),
                "summary": summary_data,
            }
        )

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error ejecutando el orquestador.",
            {"error": str(e)}
        )


# ============================================================
# TOOL 9 - VALIDAR ESTRUCTURA BÁSICA DEL PROYECTO
# ============================================================

def validar_estructura_proyecto() -> dict:
    """
    Comprueba que existen las carpetas y archivos principales del prototipo.
    """

    tool_name = "validar_estructura_proyecto"

    rutas_requeridas = [
        "00_contexto",
        "01_decision_input/decision_actual.json",
        "03_macro_houseview/outputs_macro/DECISION_001_macro.json",
        "04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.json",
        "05_mandatos_asset_allocation/outputs_mandatos/DECISION_001_mandatos.json",
        "06_sintesis_comite/DECISION_001_sintesis.json",
        "07_demo_final/README_demo.md",
        "08_agents_mcp/prompts/macro_agent_prompt.md",
        "08_agents_mcp/prompts/risk_agent_prompt.md",
        "08_agents_mcp/prompts/mandates_agent_prompt.md",
        "08_agents_mcp/prompts/synthesis_agent_prompt.md",
        "08_agents_mcp/agents/macro_agent.py",
        "08_agents_mcp/agents/risk_agent.py",
        "08_agents_mcp/agents/mandates_agent.py",
        "08_agents_mcp/agents/synthesis_agent.py",
        "08_agents_mcp/agents/research_agent.py",
        "08_agents_mcp/orchestrator/run_decision.py",
    ]

    faltantes = []

    for ruta in rutas_requeridas:
        path = _resolver_ruta(ruta)
        if not path.exists():
            faltantes.append(ruta)

    return _respuesta_ok(
        tool_name,
        {
            "project_dir": str(PROJECT_DIR),
            "numero_rutas_revisadas": len(rutas_requeridas),
            "numero_faltantes": len(faltantes),
            "faltantes": faltantes,
            "estructura_ok": len(faltantes) == 0,
        }
    )


# ============================================================
# TOOL 10 - RESUMEN RÁPIDO DECISION_001
# ============================================================

def resumen_rapido_decision_001(decision_id: str = "DECISION_001") -> dict:
    """
    Devuelve un resumen rápido de la decision_id indicada leyendo su síntesis final.
    """

    tool_name = "resumen_rapido_decision_001"

    try:
        # Preferimos el output real del LLM. Si esa pasada no devolvió un
        # bloque JSON parseable (el modelo no es 100% consistente generando
        # markdown + json en una sola respuesta), caemos al output
        # determinista en modo script (solo existe para DECISION_001).
        sintesis_llm_path = PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm_data.json"
        sintesis_script_path = PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis.json"

        sintesis_path = sintesis_llm_path if sintesis_llm_path.exists() else sintesis_script_path

        if not sintesis_path.exists():
            # Fallback: el LLM produjo markdown pero sin bloque JSON parseable
            sintesis_md = PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm.md"
            if sintesis_md.exists():
                texto = sintesis_md.read_text(encoding="utf-8")
                return _respuesta_ok(tool_name, {"id_decision": decision_id, "texto_libre": texto})
            return _respuesta_error(
                tool_name,
                f"No existe {decision_id}_sintesis_llm_data.json ni {decision_id}_sintesis.json.",
                {"ruta": str(sintesis_path)}
            )

        with open(sintesis_path, "r", encoding="utf-8") as f:
            sintesis = json.load(f)

        resumen = {
            "id_decision": sintesis.get("id_decision"),
            "hipotesis": sintesis.get("hipotesis"),
            "clasificacion_consolidada": sintesis.get("clasificacion_consolidada"),
            "resumen_clasificacion": sintesis.get("resumen_clasificacion"),
            "conclusion": sintesis.get("conclusion"),
            "alertas_consolidadas": sintesis.get("alertas_consolidadas", []),
            "informacion_faltante_consolidada": sintesis.get("informacion_faltante_consolidada", []),
            "preguntas_revision_humana": sintesis.get("preguntas_revision_humana", []),
        }

        return _respuesta_ok(
            tool_name,
            resumen
        )

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error generando resumen rápido.",
            {"error": str(e)}
        )


def calcular_escenario_riesgo_sectorial(sector: str, delta_pp: float) -> dict:
    """
    Calcula el impacto en métricas de riesgo (volatilidad, VaR, drawdown,
    tracking error, beta) de cambiar el peso de un sector de la cartera BAM
    en +/- delta_pp puntos porcentuales, financiando el cambio
    proporcionalmente con el resto de posiciones.

    A diferencia de los outputs precalculados (que solo cubren el escenario
    fijo "+3pp tecnología"), esta tool calcula bajo demanda cualquier
    escenario sectorial ad-hoc, usando la misma metodología y los mismos
    datos históricos del prototipo.

    Parámetros:
    - sector: nombre del sector GICS tal como aparece en la cartera
      (p.ej. "Information Technology", "Health Care", "Financials").
    - delta_pp: cambio en puntos porcentuales. Negativo para reducir
      (vender), positivo para aumentar (comprar). P.ej. -1.0 para "vender 1pp".
    """

    tool_name = "calcular_escenario_riesgo_sectorial"

    try:
        from risk_scenario_tool import calcular_escenario_sectorial

        resultado = calcular_escenario_sectorial(sector=sector, delta_pp=delta_pp)

        if resultado.get("status") != "success":
            return _respuesta_error(tool_name, resultado.get("message", "Error desconocido."), resultado)

        return _respuesta_ok(tool_name, resultado)

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error calculando el escenario de riesgo sectorial.",
            {"error": str(e)}
        )


def calcular_escenario_riesgo_multisector(cambios: list) -> dict:
    """
    Calcula el impacto en métricas de riesgo de mover varios sectores a la vez.

    cambios: lista de dicts con claves 'sector' y 'delta_pp'.
    Ejemplo: [{"sector": "Health Care", "delta_pp": -2.0},
               {"sector": "Information Technology", "delta_pp": 1.5}]

    El resto de la cartera financia/absorbe el neto de todos los cambios
    proporcionalmente a sus pesos actuales.
    """

    tool_name = "calcular_escenario_riesgo_multisector"

    try:
        from risk_scenario_tool import calcular_escenario_multisector

        resultado = calcular_escenario_multisector(cambios=cambios)

        if resultado.get("status") != "success":
            return _respuesta_error(tool_name, resultado.get("message", "Error desconocido."), resultado)

        return _respuesta_ok(tool_name, resultado)

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error calculando el escenario multi-sectorial.",
            {"error": str(e)}
        )


def calcular_escenario_renta_fija(tipo_shock: str, magnitud_pb: float) -> dict:
    """
    Calcula el impacto de un shock de tipos (paralelo) o de spread de
    crédito sobre la cartera de renta fija, usando duración modificada y
    OAS por posición, comparado con el benchmark de renta fija.

    Parámetros:
    - tipo_shock: "tipos_paralelo" o "spread_credito".
    - magnitud_pb: magnitud del shock en puntos básicos (positivo = subida,
      negativo = bajada).

    Datos sintéticos por ahora (ver 04_portfolio_riesgo/renta_fija/README_renta_fija.md);
    mismo formato que se espera de un extracto real de Bloomberg.
    """

    tool_name = "calcular_escenario_renta_fija"

    try:
        from fixed_income_scenario_tool import calcular_escenario_renta_fija as _calcular

        resultado = _calcular(tipo_shock=tipo_shock, magnitud_pb=magnitud_pb)

        if resultado.get("status") != "success":
            return _respuesta_error(tool_name, resultado.get("message", "Error desconocido."), resultado)

        return _respuesta_ok(tool_name, resultado)

    except Exception as e:
        return _respuesta_error(
            tool_name,
            "Error calculando el escenario de renta fija.",
            {"error": str(e)}
        )


# ============================================================
# WEB SEARCH (Google Custom Search API)
# ============================================================

def web_search(query: str, num_results: int = 5) -> dict:
    """
    Busca en Internet usando Google Custom Search API.

    Requiere en .env:
      GOOGLE_SEARCH_API_KEY  — API key creada en GCP Console (Custom Search API habilitada)
      GOOGLE_SEARCH_CX       — ID del Programmable Search Engine (cx)

    Devuelve lista de resultados: título, snippet y URL.
    """
    tool_name = "web_search"

    api_key = os.getenv("GOOGLE_SEARCH_API_KEY", "").strip()
    cx = os.getenv("GOOGLE_SEARCH_CX", "").strip()

    if not api_key or not cx:
        return _respuesta_error(
            tool_name,
            "Faltan GOOGLE_SEARCH_API_KEY y/o GOOGLE_SEARCH_CX en .env. "
            "Crea un Programmable Search Engine en https://programmablesearchengine.google.com, "
            "habilita la Custom Search API en el proyecto GCP y genera una API key.",
        )

    num = max(1, min(10, int(num_results)))
    url = (
        "https://www.googleapis.com/customsearch/v1"
        f"?key={api_key}&cx={cx}&q={urllib.parse.quote(query)}&num={num}"
    )

    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return _respuesta_error(tool_name, f"Error llamando a Google Custom Search API: {e}")

    items = data.get("items", [])
    results = [
        {
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "url": item.get("link", ""),
        }
        for item in items
    ]

    # Registra coste (no bloquea si cost_tracker no está disponible)
    try:
        if str(AGENTS_MCP_DIR) not in sys.path:
            sys.path.insert(0, str(AGENTS_MCP_DIR))
        from cost_tracker import record_search_call
        record_search_call(query_count=1)
    except Exception:
        pass

    return _respuesta_ok(tool_name, {
        "query": query,
        "num_results": len(results),
        "results": results,
    })


# Declaración de tools para Research Agent (formato Gemini function calling)
RESEARCH_TOOLS_DECLARATIONS = [
    {
        "functionDeclarations": [
            {
                "name": "web_search",
                "description": (
                    "Busca información en Internet sobre un tema. "
                    "Devuelve títulos, snippets y URLs de los resultados más relevantes. "
                    "Úsala para encontrar información reciente sobre la hipótesis de inversión: "
                    "noticias del sector, datos de mercado, análisis de analistas, riesgos regulatorios, "
                    "posicionamiento competitivo, etc. Haz búsquedas específicas y variadas."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": (
                                "Consulta de búsqueda específica. "
                                "Usa términos concretos en inglés o español. "
                                "Ejemplos: 'AI infrastructure capex spending 2025', "
                                "'riesgo regulatorio sector tecnología Europa', "
                                "'semiconductor demand outlook 2025'."
                            ),
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Número de resultados a devolver (1-10). Por defecto 5.",
                        },
                    },
                    "required": ["query"],
                },
            }
        ]
    }
]

# ============================================================
# REGISTRO SIMPLE DE TOOLS
# ============================================================

TOOLS_REGISTRY = {
    "listar_archivos": listar_archivos,
    "leer_texto": leer_texto,
    "leer_json": leer_json,
    "leer_csv": leer_csv,
    "guardar_texto": guardar_texto,
    "guardar_json": guardar_json,
    "leer_output_agente": leer_output_agente,
    "ejecutar_orquestador_decision_001": ejecutar_orquestador_decision_001,
    "validar_estructura_proyecto": validar_estructura_proyecto,
    "resumen_rapido_decision_001": resumen_rapido_decision_001,
    "calcular_escenario_riesgo_sectorial": calcular_escenario_riesgo_sectorial,
    "calcular_escenario_riesgo_multisector": calcular_escenario_riesgo_multisector,
    "calcular_escenario_renta_fija": calcular_escenario_renta_fija,
    "web_search": web_search,
}


def listar_tools_disponibles() -> dict:
    """
    Devuelve el listado de tools disponibles en este módulo.
    """

    tool_name = "listar_tools_disponibles"

    return _respuesta_ok(
        tool_name,
        {
            "numero_tools": len(TOOLS_REGISTRY),
            "tools": sorted(list(TOOLS_REGISTRY.keys())),
        }
    )


# ============================================================
# PRUEBA MANUAL
# ============================================================

if __name__ == "__main__":
    print("Probando tools.py")
    print(json.dumps(listar_tools_disponibles(), ensure_ascii=False, indent=2))
    print(json.dumps(validar_estructura_proyecto(), ensure_ascii=False, indent=2))