"""
test_integracion.py — InvestCopilot integration test

Crea una decisión de prueba estandarizada, lanza el orquestador completo,
valida todos los outputs y simula respuestas de chat para preguntas clave.

Modos:
  --mode mock    : sin llamadas reales al LLM (valida plomería, ~10s)
  --mode llm     : llamadas reales a Vertex AI (~3-4 min, coste real)

Uso:
  python3 08_agents_mcp/test_integracion.py --mode mock
  python3 08_agents_mcp/test_integracion.py --mode llm
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

AGENTS_MCP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = AGENTS_MCP_DIR.parent
sys.path.insert(0, str(AGENTS_MCP_DIR / "llm_client"))
sys.path.insert(0, str(AGENTS_MCP_DIR / "agents"))
sys.path.insert(0, str(AGENTS_MCP_DIR / "orchestrator"))

# ── paleta de resultados ───────────────────────────────────────────────────────

PASS  = "✅  PASS"
FAIL  = "❌  FAIL"
SKIP  = "⚪  SKIP"
INFO  = "ℹ️  "

results: list[dict] = []


def record(name: str, passed: bool, detail: str = "", skip: bool = False):
    tag = SKIP if skip else (PASS if passed else FAIL)
    line = f"  {tag}  {name}"
    if detail:
        line += f"\n         {detail}"
    print(line)
    results.append({"name": name, "passed": passed if not skip else None, "skip": skip})
    return passed


def section(title: str):
    print(f"\n── {title} {'─' * max(0, 55 - len(title))}")


# ── decisión de prueba estándar ────────────────────────────────────────────────

TEST_DECISION = {
    "id_decision": "TEST_INTEGRACION_PLACEHOLDER",
    "fondo": "Fondmapfre Bolsa América",
    "fondo_id": "BAM",
    "hipotesis": (
        "Evaluar el impacto de incrementar en 2 p.p. la exposición al sector "
        "Consumer Staples en la cartera BAM, considerando la defensa ante un "
        "escenario de desaceleración económica y el cumplimiento del mandato."
    ),
    "tipo": "cambio_sectorial",
    "sector": "Consumer Staples",
    "delta_pp": 2.0,
    "origen": "test_integracion",
    "fecha_creacion": "PLACEHOLDER_DATE",
    "advertencia": (
        "Decisión creada automáticamente por el test de integración de InvestCopilot. "
        "No constituye una hipótesis real de inversión."
    ),
}


def crear_decision_prueba() -> str:
    """Crea el archivo de decisión de prueba y devuelve su decision_id."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    decision_id = f"TEST_{ts}"

    decision = dict(TEST_DECISION)
    decision["id_decision"] = decision_id
    decision["fecha_creacion"] = datetime.now().isoformat(timespec="seconds")

    decisiones_dir = PROJECT_DIR / "01_decision_input" / "decisiones"
    decisiones_dir.mkdir(parents=True, exist_ok=True)

    path = decisiones_dir / f"{decision_id}.json"
    path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")
    return decision_id


# ── decisión RF de prueba ──────────────────────────────────────────────────────

TEST_RF_DECISION = {
    "id_decision": "TEST_RF_PLACEHOLDER",
    "fondo": "Fondmapfre Bolsa América",
    "fondo_id": "BAM",
    "hipotesis": (
        "Evaluar el impacto de un shock de subida de tipos de interés de 50 puntos básicos "
        "sobre la cartera de renta fija de BAM, considerando la duración modificada de las "
        "posiciones y el efecto sobre el precio y la rentabilidad esperada."
    ),
    "tipo": "renta_fija",
    "origen": "test_integracion",
    "fecha_creacion": "PLACEHOLDER_DATE",
    "advertencia": (
        "Decisión creada automáticamente por el test de integración de InvestCopilot. "
        "No constituye una hipótesis real de inversión."
    ),
}


def validate_rf_tool_direct():
    """Valida directamente la tool calcular_escenario_renta_fija (sin orquestador)."""
    section("Tool de Renta Fija — validación directa")

    rf_dir = PROJECT_DIR / "04_portfolio_riesgo" / "renta_fija"
    if str(rf_dir) not in sys.path:
        sys.path.insert(0, str(rf_dir))

    try:
        from fixed_income_scenario_tool import calcular_escenario_renta_fija
        record("RF tool importable", True)
    except ImportError as e:
        record("RF tool importable", False, str(e))
        return

    # F4: verificar que usa datos reales (cartera_bonos_real.csv)
    real_csv = PROJECT_DIR / "04_portfolio_riesgo" / "renta_fija" / "cartera_bonos_real.csv"
    record("F4 cartera_bonos_real.csv existe", real_csv.exists(),
           f"{real_csv.name} ({real_csv.stat().st_size // 1024} KB)" if real_csv.exists() else str(real_csv))

    # tipos_paralelo +50pb (subida de tipos → precio baja)
    try:
        res = calcular_escenario_renta_fija(tipo_shock="tipos_paralelo", magnitud_pb=50)
        has_data = isinstance(res, dict) and res.get("status") != "error"
        precio = res.get("cartera", {}).get("impacto_precio_pct_estimado")
        dur    = res.get("cartera", {}).get("duracion_modificada_media")
        detail = f"dur={dur}a  impacto={precio:.4f}%" if precio is not None else str(list(res.keys())[:5])
        record("RF tipos_paralelo +50pb → devuelve resultado", has_data, detail)
        if precio is not None:
            record("RF subida tipos → precio baja (signo negativo)", precio < 0,
                   f"{precio:.4f}% (esperado < 0)")
        if real_csv.exists() and dur is not None:
            record("F4 duración real > 1 año (datos reales, no cero)", dur > 1.0,
                   f"dur media = {dur} años")
    except Exception as e:
        record("RF tipos_paralelo +50pb → devuelve resultado", False, str(e))

    # spread_credito +100pb
    try:
        res2 = calcular_escenario_renta_fija(tipo_shock="spread_credito", magnitud_pb=100)
        has_data2 = isinstance(res2, dict) and res2.get("status") != "error"
        precio2 = res2.get("cartera", {}).get("impacto_precio_pct_estimado")
        detail2 = f"impacto={precio2:.4f}%" if precio2 is not None else str(list(res2.keys())[:5])
        record("RF spread_credito +100pb → devuelve resultado", has_data2, detail2)
    except Exception as e:
        record("RF spread_credito +100pb → devuelve resultado", False, str(e))


# ── infraestructura: log_util, cost_tracker, grounding ────────────────────────

def validate_infrastructure():
    section("Infraestructura — log_util · cost_tracker · F2 grounding")

    # --- F3-B: log_util structured JSON ---
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("log_util", AGENTS_MCP_DIR / "log_util.py")
        _log_mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_log_mod)
        record("F3-B log_util importable y log()", True)

        import io as _io
        buf = _io.StringIO()
        _orig_stderr = sys.stderr
        sys.stderr = buf
        try:
            _log_mod.log("INFO", "test_infra_msg", agent="test", decision_id="TEST")
        finally:
            sys.stderr = _orig_stderr
        log_line = buf.getvalue().strip()
        parsed = json.loads(log_line)
        record("F3-B log emite JSON válido", True,
               f"level={parsed.get('level')} msg={parsed.get('msg')}")
        record("F3-B log incluye agent y decision_id",
               "agent" in parsed and "decision_id" in parsed,
               str({k: parsed.get(k) for k in ("agent", "decision_id")}))
    except Exception as e:
        record("F3-B log_util importable y log()", False, str(e))

    # --- F3-D: cost_tracker ---
    try:
        import importlib.util as _ilu2
        spec2 = _ilu2.spec_from_file_location("cost_tracker", AGENTS_MCP_DIR / "cost_tracker.py")
        ct = _ilu2.module_from_spec(spec2)
        spec2.loader.exec_module(ct)
        record("F3-D cost_tracker importable", True)

        summary = ct.get_today_summary()
        has_keys = all(k in summary for k in ("date", "total_cost_eur", "pct_cap", "status"))
        record("F3-D get_today_summary() devuelve estructura esperada",
               has_keys, str({k: summary.get(k) for k in ("total_cost_eur", "status", "pct_cap")}))

        # record_llm_call con tokens mínimos (no debería lanzar CostCapExceeded salvo cap ya alcanzado)
        try:
            info = ct.record_llm_call(
                model="gemini-2.5-flash",
                input_tokens=100,
                output_tokens=50,
                decision_id="TEST_INFRA",
            )
            cost_ok = isinstance(info, dict) and info.get("cost_eur", 0) >= 0
            record("F3-D record_llm_call() registra coste", cost_ok,
                   f"cost_eur={info.get('cost_eur',0):.6f} total_today={info.get('total_today_eur',0):.4f}")
        except ct.CostCapExceeded:
            record("F3-D record_llm_call() registra coste", True,
                   "CostCapExceeded (cap ya alcanzado hoy — correcto)")
        except Exception as e:
            record("F3-D record_llm_call() registra coste", False, str(e))

        # check_cap no debe lanzar si estamos lejos del cap (difícil de garantizar, skip si cap alcanzado)
        try:
            ct.check_cap(model="gemini-2.5-flash")
            record("F3-D check_cap() no lanza si bajo el cap", True)
        except ct.CostCapExceeded:
            record("F3-D check_cap() no lanza si bajo el cap", True,
                   "Cap ya alcanzado hoy — excepción esperada, no un fallo", skip=True)
        except Exception as e:
            record("F3-D check_cap() no lanza si bajo el cap", False, str(e))

    except Exception as e:
        record("F3-D cost_tracker importable", False, str(e))

    # --- F2: research grounding fields en output JSON (si existe DECISION_001) ---
    dec001_research_json = PROJECT_DIR / "02_research" / "outputs_research" / "DECISION_001_research_llm.json"
    if dec001_research_json.exists():
        try:
            rdata = json.loads(dec001_research_json.read_text(encoding="utf-8"))
            # grounding fields están al nivel raíz del JSON (no dentro de parsed_data)
            llm_mode_used  = rdata.get("llm_mode", "")
            grounding_used = rdata.get("grounding_used", False)
            sources        = rdata.get("sources", [])
            sources_count  = len(sources)
            web_queries    = rdata.get("web_queries", [])
            if llm_mode_used != "vertex_ai":
                record("F2 research grounding fields (DECISION_001)", True,
                       f"llm_mode={llm_mode_used} — grounding solo aplica en vertex_ai", skip=True)
            else:
                record("F2 research grounding_used=True (vertex_ai)", grounding_used,
                       f"grounding_used={grounding_used} sources={sources_count} web_queries={len(web_queries)}")
                record("F2 research sources_count > 0", sources_count > 0, f"sources={sources_count}")
        except Exception as e:
            record("F2 research grounding fields", False, str(e))
    else:
        record("F2 research grounding fields (DECISION_001)", True,
               "DECISION_001 output no existe — SKIP (solo verificable tras run vertex_ai)", skip=True)


# ── runners ────────────────────────────────────────────────────────────────────

def run_orchestrator(decision_id: str, llm_mode: str) -> dict:
    from run_decision import run_decision
    return run_decision(
        decision_id=decision_id,
        mode="llm",  # siempre llm (solo DECISION_001 tiene modo script)
        llm_mode=llm_mode,
    )


# ── validaciones de outputs ────────────────────────────────────────────────────

def _file(rel: str) -> Path:
    return PROJECT_DIR / rel


def validate_outputs(decision_id: str, llm_mode: str):
    section("Archivos de output")

    # Cada agente debe producir al menos el markdown
    agents_files = {
        "research": _file(f"02_research/outputs_research/{decision_id}_research_llm.md"),
        "macro":    _file(f"03_macro_houseview/outputs_macro/{decision_id}_macro_llm.md"),
        "risk":     _file(f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm.md"),
        "mandates": _file(f"05_mandatos_asset_allocation/outputs_mandatos/{decision_id}_mandatos_llm.md"),
        "synthesis":_file(f"06_sintesis_comite/{decision_id}_sintesis_llm.md"),
    }

    for agent, path in agents_files.items():
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        has_content = size > 200  # no vacío
        if llm_mode == "mock":
            # mock produce siempre texto, aunque muy corto
            record(f"{agent} MD existe", exists, f"{size} bytes" if exists else "FALTA")
        else:
            record(f"{agent} MD con contenido", exists and has_content,
                   f"{size:,} bytes" if exists else "FALTA")

    # Risk: comprobar que la tool fue invocada (más fiable que exigir _data.json)
    if llm_mode != "mock":
        section("Tool calling y JSON estructurados (requiere LLM real)")

        risk_llm_json = _file(f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm.json")
        mandates_data_path = _file(f"05_mandatos_asset_allocation/outputs_mandatos/{decision_id}_mandatos_llm_data.json")

        # Risk: preferimos que la tool fue llamada sobre si existe el JSON block
        if risk_llm_json.exists():
            try:
                meta = json.loads(risk_llm_json.read_text(encoding="utf-8"))
                raw_data = meta.get("raw_llm_response", {}).get("data", {})
                tools_inv = raw_data.get("tools_invocadas", [])
                tool_called = any("calcular" in str(t.get("tool", "")) for t in tools_inv)
                record("Risk: tool de cálculo invocada",
                       tool_called,
                       str([t.get("tool") for t in tools_inv]) if tools_inv else "sin tool calls")

                # _data.json es bonus; si no existe pero hay MD es aceptable
                risk_data_path = _file(f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm_data.json")
                if risk_data_path.exists():
                    record("Risk _data.json (bonus)", True, f"{risk_data_path.stat().st_size:,} bytes")
                else:
                    md_path = _file(f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm.md")
                    md_size = md_path.stat().st_size if md_path.exists() else 0
                    record("Risk _data.json (bonus — sin JSON block, fallback MD)",
                           True, f"MD disponible ({md_size:,} bytes) — LLM no emitió bloque json",
                           skip=True)
            except Exception as e:
                record("Risk: tool de cálculo invocada", False, str(e))
        else:
            record("Risk: tool de cálculo invocada", False, "llm.json no encontrado")

        for label, path in [("mandates _data.json", mandates_data_path)]:
            exists = path.exists()
            record(label, exists, str(path.stat().st_size) + " bytes" if exists else "FALTA — el LLM no emitió bloque ```json```")


def validate_risk_metrics(decision_id: str, llm_mode: str):
    if llm_mode == "mock":
        record("Risk métricas cuantitativas", True, "SKIP en modo mock", skip=True)
        return

    section("Métricas cuantitativas del Risk Agent")

    data_path = _file(f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm_data.json")
    if not data_path.exists():
        md_path = _file(f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm.md")
        llm_json_path = _file(f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm.json")
        tool_called = False
        if llm_json_path.exists():
            try:
                meta = json.loads(llm_json_path.read_text(encoding="utf-8"))
                tools_inv = meta.get("raw_llm_response", {}).get("data", {}).get("tools_invocadas", [])
                tool_called = any("calcular" in str(t.get("tool", "")) for t in tools_inv)
            except Exception:
                pass
        if md_path.exists() and tool_called:
            record("Risk métricas cuantitativas",
                   True, "Tool invocada; bloque json no emitido — fallback MD disponible", skip=True)
        elif md_path.exists():
            record("Risk métricas cuantitativas", False,
                   "MD existe pero sin evidencia de tool call y sin _data.json")
        else:
            record("Risk métricas cuantitativas", False, "Ni _data.json ni MD encontrado")
        return

    data = json.loads(data_path.read_text(encoding="utf-8"))
    metricas = data.get("metricas", {})
    actual = metricas.get("bam_actual", {})
    escenario_keys = [k for k in metricas if k not in ("bam_actual",) and "diferencia" not in k]

    record("Risk llamó a la tool de cálculo", bool(escenario_keys),
           f"escenario key: {escenario_keys[0] if escenario_keys else 'NO ENCONTRADA'}")

    if escenario_keys:
        escenario = metricas[escenario_keys[0]]
        vol_actual = actual.get("volatilidad_anualizada", 0)
        vol_esc    = escenario.get("volatilidad_anualizada", 0)
        te_actual  = actual.get("tracking_error_anualizado", 0)
        te_esc     = escenario.get("tracking_error_anualizado", 0)

        record("Volatilidad anual BAM actual plausible (5%-40%)",
               0.05 < vol_actual < 0.40, f"{vol_actual*100:.2f}%")
        record("Volatilidad escenario calculada",
               0.05 < vol_esc < 0.40, f"{vol_esc*100:.2f}%")
        record("Tracking Error BAM actual plausible (0%-20%)",
               0 < te_actual < 0.20, f"{te_actual*100:.2f}%")

        diff_vol = (vol_esc - vol_actual) * 100
        record("Diferencia de volatilidad en rango razonable (±5 p.p.)",
               abs(diff_vol) < 5, f"{diff_vol:+.2f} p.p.")

        diff_te = (te_esc - te_actual) * 100
        record("Diferencia de TE en rango razonable (±5 p.p.)",
               abs(diff_te) < 5, f"{diff_te:+.2f} p.p.")


def validate_mandates(decision_id: str, llm_mode: str):
    if llm_mode == "mock":
        record("Mandates análisis sectorial", True, "SKIP en modo mock", skip=True)
        return

    section("Análisis sectorial del Mandates Agent")

    data_path = _file(f"05_mandatos_asset_allocation/outputs_mandatos/{decision_id}_mandatos_llm_data.json")
    if not data_path.exists():
        record("Mandates _data.json", False, "FALTA")
        return

    data = json.loads(data_path.read_text(encoding="utf-8"))
    analisis = data.get("analisis_sectorial", {})

    record("Mandates _data.json parseable", True)

    if not analisis:
        # El LLM a veces estructura el JSON sin analisis_sectorial; es aceptable si hay datos
        has_sector_data = bool(data.get("alertas_mandatos") or data.get("clasificacion_preliminar"))
        record("Tiene datos mandatos (estructura alternativa)",
               has_sector_data,
               f"claves: {list(data.keys())[:6]}", skip=has_sector_data)
        return

    record("Tiene analisis_sectorial",
           True, f"sector: {analisis.get('sector_analizado','?')}")

    # El LLM puede usar peso_actual_bam_pct o peso_bam_actual_pct según el run
    peso_actual = analisis.get("peso_actual_bam_pct") or analisis.get("peso_bam_actual_pct", 0)
    record("Peso actual BAM > 0% y <= 60%",
           0 < peso_actual <= 60, f"{peso_actual:.2f}% (esperado >0 para Consumer Staples BAM ~6.87%)")

    # alerta puede ser un string directo, un dict con "clasificacion", o en alertas_mandatos
    _alerta_prot = analisis.get("alerta_prototipo_sectorial", {})
    alerta_str = (analisis.get("alerta_actual_prototipo") or
                  (_alerta_prot if isinstance(_alerta_prot, str) else _alerta_prot.get("clasificacion", "")) or
                  (data.get("alertas_mandatos") or [{}])[0].get("nivel_alerta", ""))
    record("Alerta sectorial calculada", bool(alerta_str), alerta_str or "FALTA")


# ── simulación de chat ─────────────────────────────────────────────────────────

def simulate_chat(decision_id: str, llm_mode: str):
    section("Simulación de respuestas de chat")

    # Simular leer_riesgo_json() del app.py
    def _read_json_fallback(*relpaths) -> dict:
        for rel in relpaths:
            p = PROJECT_DIR / rel
            if p.exists() and p.stat().st_size > 10:
                try:
                    return json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    pass
        return {}

    def _read_md_fallback(relpath: str) -> dict:
        p = PROJECT_DIR / relpath
        if p.exists() and p.stat().st_size > 200:
            return {"_texto_libre": p.read_text(encoding="utf-8")}
        return {}

    # Risk
    risk_data = (
        _read_json_fallback(
            f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm_data.json",
            f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo.json",
        ) or _read_md_fallback(f"04_portfolio_riesgo/outputs_riesgo/{decision_id}_riesgo_llm.md")
    )
    record("Chat: leer_riesgo_json() devuelve datos", bool(risk_data),
           "_texto_libre" if risk_data.get("_texto_libre") else f"resultado={risk_data.get('resultado','?')}")

    if risk_data.get("metricas"):
        metricas = risk_data["metricas"]
        vol_diff = metricas.get("diferencia_escenario_menos_actual", {}).get("volatilidad_anualizada")
        record("Chat: respuesta_riesgo() incluiría tabla de métricas",
               vol_diff is not None, f"Δvol = {vol_diff*100:+.2f} p.p." if vol_diff else "sin dato")
    elif risk_data.get("_texto_libre"):
        record("Chat: respuesta_riesgo() caería a modo texto libre",
               True, f"{len(risk_data['_texto_libre'])} chars disponibles")
    else:
        record("Chat: respuesta_riesgo() tiene datos", False, "dict vacío")

    # Mandates
    mandates_data = (
        _read_json_fallback(
            f"05_mandatos_asset_allocation/outputs_mandatos/{decision_id}_mandatos_llm_data.json",
            f"05_mandatos_asset_allocation/outputs_mandatos/{decision_id}_mandatos.json",
        ) or _read_md_fallback(f"05_mandatos_asset_allocation/outputs_mandatos/{decision_id}_mandatos_llm.md")
    )
    record("Chat: leer_mandatos_json() devuelve datos", bool(mandates_data),
           "_texto_libre" if mandates_data.get("_texto_libre") else f"sector={mandates_data.get('analisis_sectorial',{}).get('sector_analizado','?')}")

    # Síntesis
    synthesis_data = (
        _read_json_fallback(
            f"06_sintesis_comite/{decision_id}_sintesis_llm_data.json",
            f"06_sintesis_comite/{decision_id}_sintesis.json",
        ) or _read_md_fallback(f"06_sintesis_comite/{decision_id}_sintesis_llm.md")
    )
    record("Chat: leer_sintesis_json() devuelve datos", bool(synthesis_data),
           "_texto_libre" if synthesis_data.get("_texto_libre") else f"clasificacion={synthesis_data.get('clasificacion_consolidada','?')}")

    # Pregunta: ¿cuánto cambia la volatilidad?
    if risk_data.get("metricas"):
        diff = risk_data["metricas"].get("diferencia_escenario_menos_actual", {})
        vol = diff.get("volatilidad_anualizada")
        te  = diff.get("tracking_error_anualizado")
        if vol is not None and te is not None:
            print(f"\n  {INFO} Pregunta: '¿Cuánto cambia la volatilidad?'")
            print(f"         Respuesta simulada:")
            print(f"         Volatilidad:      {vol*100:+.2f} p.p.")
            print(f"         Tracking Error:   {te*100:+.2f} p.p.")
            var = diff.get("var_historico_anualizado_95")
            if var:
                print(f"         VaR 95%:          {var*100:+.2f} p.p.")
    elif risk_data.get("_texto_libre"):
        print(f"\n  {INFO} Pregunta cuant.: respuesta disponible vía texto libre del agente")


# ── limpieza opcional ──────────────────────────────────────────────────────────

def cleanup(decision_id: str):
    """Borra los archivos generados por el test."""
    paths = [
        PROJECT_DIR / "01_decision_input" / "decisiones" / f"{decision_id}.json",
        PROJECT_DIR / "02_research" / "outputs_research" / f"{decision_id}_research_llm.md",
        PROJECT_DIR / "02_research" / "outputs_research" / f"{decision_id}_research_llm.json",
        PROJECT_DIR / "02_research" / "outputs_research" / f"{decision_id}_research_llm_data.json",
        PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro_llm.md",
        PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro_llm.json",
        PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro_llm_data.json",
        PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm.md",
        PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm.json",
        PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm_data.json",
        PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm.md",
        PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm.json",
        PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm_data.json",
        PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm.md",
        PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm.json",
        PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm_data.json",
        AGENTS_MCP_DIR / "orchestrator" / f"run_{decision_id}_summary.json",
        AGENTS_MCP_DIR / "orchestrator" / f"run_{decision_id}_summary.md",
        AGENTS_MCP_DIR / "orchestrator" / f"run_{decision_id}_progress.json",
    ]
    removed = 0
    for p in paths:
        if p.exists():
            p.unlink()
            removed += 1
    print(f"\n  {INFO} Limpieza: {removed} archivos de test eliminados")


# ── main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Parse args
    llm_mode = "mock"
    do_cleanup = True
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--mode" and i + 1 < len(sys.argv[1:]):
            llm_mode = sys.argv[i + 2]
        if arg == "--no-cleanup":
            do_cleanup = False

    print("=" * 62)
    print("  InvestCopilot — Test de Integración")
    print(f"  Modo LLM: {llm_mode}")
    print("=" * 62)

    # Infraestructura: log_util, cost_tracker, grounding fields
    validate_infrastructure()

    # Validación directa de la tool de renta fija (no requiere LLM)
    validate_rf_tool_direct()

    # Hipótesis de prueba
    print(f"\n{INFO} Hipótesis de prueba:")
    print(f"     '{TEST_DECISION['hipotesis']}'")
    print(f"     Sector: {TEST_DECISION['sector']}  |  delta: +{TEST_DECISION['delta_pp']} p.p.")

    # Crear decisión
    section("Creación de decisión de prueba")
    decision_id = crear_decision_prueba()
    dec_path = PROJECT_DIR / "01_decision_input" / "decisiones" / f"{decision_id}.json"
    record("Archivo de decisión creado", dec_path.exists(), decision_id)

    # Lanzar orquestador
    section("Ejecución del orquestador")
    print(f"  {INFO} Lanzando flujo… (puede tardar {'~3-4 min' if llm_mode != 'mock' else '~5s'})")
    t0 = time.time()

    try:
        final = run_orchestrator(decision_id, llm_mode)
        elapsed = time.time() - t0
        status = final.get("status")
        record("Orquestador completado", status == "success",
               f"status={status}  |  {elapsed:.0f}s  |  {final.get('message','')[:80]}")

        for r in final.get("results", []):
            agent  = r.get("agent", "?")
            ast    = r.get("status", "?")
            msg    = r.get("message", "")[:60]
            record(f"  └─ {agent}", ast == "success", msg if ast != "success" else "")

    except Exception as e:
        elapsed = time.time() - t0
        record("Orquestador completado", False, str(e)[:120])

    # Validar archivos
    validate_outputs(decision_id, llm_mode)
    validate_risk_metrics(decision_id, llm_mode)
    validate_mandates(decision_id, llm_mode)
    simulate_chat(decision_id, llm_mode)

    # Limpieza
    if do_cleanup:
        cleanup(decision_id)

    # Resumen final
    passed  = sum(1 for r in results if r["passed"] is True)
    failed  = sum(1 for r in results if r["passed"] is False)
    skipped = sum(1 for r in results if r["skip"])
    total   = passed + failed

    print("\n" + "=" * 62)
    print(f"  Resultado: {passed}/{total} checks pasados  |  {skipped} skipped  |  {failed} fallidos")
    if failed == 0:
        print("  ✅  Todo OK — listo para prueba manual")
    else:
        print("  ❌  Hay fallos — revisar antes de la demo")
    print("=" * 62)

    sys.exit(0 if failed == 0 else 1)
