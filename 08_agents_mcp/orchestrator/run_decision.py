from pathlib import Path
import json
import sys
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# python run_decision.py --mode llm --llm-mode mock
# python run_decision.py --mode llm --llm-mode vertex_ai --decision-id DEC_20260630_120000
#
# Variables de entorno opcionales:
#
# INVESTCOPILOT_WORKFLOW_MODE=script | llm
# INVESTCOPILOT_LLM_MODE=mock | openai_compatible | azure_openai | vertex_ai
#
# --decision-id (o INVESTCOPILOT_DECISION_ID) selecciona qué decisión
# analizar. Por defecto DECISION_001 (caso de demo precalculado). Cualquier
# otra decision_id debe existir en 01_decision_input/decisiones/{id}.json
# (lo crea la web al enviar una hipótesis nueva) y solo funciona en
# mode="llm" (no hay script determinista para decisiones nuevas).

ORCHESTRATOR_DIR = Path(__file__).resolve().parent
AGENTS_MCP_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = Path(__file__).resolve().parents[2]

AGENTS_DIR = AGENTS_MCP_DIR / "agents"

if str(AGENTS_DIR) not in sys.path:
    sys.path.append(str(AGENTS_DIR))

if str(AGENTS_MCP_DIR) not in sys.path:
    sys.path.append(str(AGENTS_MCP_DIR))

from log_util import log

from research_agent import run_research_agent
from macro_agent import run_macro_agent
from risk_agent import run_risk_agent
from mandates_agent import run_mandates_agent
from synthesis_agent import run_synthesis_agent

_progress_lock = threading.Lock()


def _progress_path(decision_id: str) -> Path:
    return ORCHESTRATOR_DIR / f"run_{decision_id}_progress.json"


def _summary_json_path(decision_id: str) -> Path:
    return ORCHESTRATOR_DIR / f"run_{decision_id}_summary.json"


def _summary_md_path(decision_id: str) -> Path:
    return ORCHESTRATOR_DIR / f"run_{decision_id}_summary.md"


# ============================================================
# PROGRESO EN VIVO (para que la web pueda mostrar qué agente va corriendo,
# en vez de un spinner ciego durante los ~1-3 min que tarda el flujo)
# ============================================================

def _init_progress(decision_id, agent_names):
    data = {name: "pending" for name in agent_names}
    data["_updated_at"] = datetime.now().isoformat(timespec="seconds")

    with _progress_lock:
        with open(_progress_path(decision_id), "w", encoding="utf-8") as f:
            json.dump(data, f)


def _update_progress(decision_id, agent_name, status):
    with _progress_lock:
        path = _progress_path(decision_id)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

        data[agent_name] = status
        data["_updated_at"] = datetime.now().isoformat(timespec="seconds")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def status_icon(status):
    if status == "success":
        return "OK"
    if status == "error":
        return "ERROR"
    return "WARN"


def safe_get(dct, *keys, default=None):
    current = dct

    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)

    return current if current is not None else default


def parse_args():
    args = sys.argv[1:]

    mode = os.getenv("INVESTCOPILOT_WORKFLOW_MODE", "script").strip().lower()
    llm_mode = os.getenv("INVESTCOPILOT_LLM_MODE", "mock").strip().lower()
    decision_id = os.getenv("INVESTCOPILOT_DECISION_ID", "DECISION_001").strip()

    if "--mode" in args:
        idx = args.index("--mode")
        if idx + 1 < len(args):
            mode = args[idx + 1].strip().lower()

    if "--llm-mode" in args:
        idx = args.index("--llm-mode")
        if idx + 1 < len(args):
            llm_mode = args[idx + 1].strip().lower()

    if "--decision-id" in args:
        idx = args.index("--decision-id")
        if idx + 1 < len(args):
            decision_id = args[idx + 1].strip()

    if mode not in ["script", "llm"]:
        mode = "script"

    if llm_mode not in ["mock", "openai_compatible", "azure_openai", "vertex_ai"]:
        llm_mode = "mock"

    if not decision_id:
        decision_id = "DECISION_001"

    return {
        "mode": mode,
        "llm_mode": llm_mode,
        "decision_id": decision_id,
    }


def run_step(decision_id, step_name, func, mode="script", llm_mode="mock", model=None):
    _update_progress(decision_id, step_name, "running")
    log("INFO", "step_start", agent=step_name, decision_id=decision_id,
        mode=mode, llm_mode=llm_mode, **({"model": model} if model else {}))

    try:
        result = func(
            project_dir=PROJECT_DIR,
            decision_id=decision_id,
            mode=mode,
            llm_mode=llm_mode,
            model=model,
        )
    except TypeError:
        try:
            result = func(project_dir=PROJECT_DIR, decision_id=decision_id)
        except Exception as e:
            result = {
                "agent": step_name,
                "status": "error",
                "message": f"Error no controlado ejecutando {step_name}",
                "error": str(e),
            }
    except Exception as e:
        result = {
            "agent": step_name,
            "status": "error",
            "message": f"Error no controlado ejecutando {step_name}",
            "error": str(e),
        }

    _update_progress(decision_id, step_name, result.get("status", "error"))
    log(
        "INFO" if result.get("status") == "success" else "ERROR",
        "step_end",
        agent=step_name,
        decision_id=decision_id,
        status=result.get("status"),
        message=result.get("message", ""),
    )
    return result


# ============================================================
# ORQUESTADOR PRINCIPAL
# ============================================================

def run_decision(decision_id="DECISION_001", mode="script", llm_mode="mock"):
    start_time = datetime.now().isoformat(timespec="seconds")

    agent_order = ["research_agent", "macro_agent", "risk_agent", "mandates_agent", "synthesis_agent"]
    _init_progress(decision_id, agent_order)

    # Orden de ejecucion con dependencias:
    #
    # Fase 1 (paralelo): Research + Macro + Risk
    #   - No dependen entre si; cada uno analiza desde su dominio.
    #   - Research solo soporta mode="llm" (sin script determinista).
    #
    # Fase 2 (secuencial): Mandates
    #   - El prompt de Mandates dice "puedes usar el output del Agente Riesgo
    #     como input". Para que eso sea posible, Mandates corre despues de Risk.
    #
    # Fase 3 (secuencial): Synthesis
    #   - Depende de los outputs de los 4 agentes anteriores.

    parallel_specs = {
        "research_agent": (run_research_agent, "llm" if mode == "llm" else "script", llm_mode, None),
        "macro_agent": (run_macro_agent, mode, llm_mode, None),
        "risk_agent": (run_risk_agent, mode, llm_mode, None),
    }

    results_map = {}

    with ThreadPoolExecutor(max_workers=len(parallel_specs)) as executor:
        future_to_agent = {
            executor.submit(
                run_step, decision_id, agent_name, func, mode=step_mode, llm_mode=step_llm_mode, model=step_model
            ): agent_name
            for agent_name, (func, step_mode, step_llm_mode, step_model) in parallel_specs.items()
        }

        for future in as_completed(future_to_agent):
            agent_name = future_to_agent[future]
            results_map[agent_name] = future.result()

    results = [results_map[name] for name in ["research_agent", "macro_agent", "risk_agent"]]

    for agent_key, agent_label in [
        ("macro_agent", "Macro Agent"),
        ("risk_agent", "Risk Agent"),
    ]:
        if results_map[agent_key].get("status") != "success":
            return build_final_result(
                decision_id=decision_id,
                start_time=start_time,
                results=results,
                status="error",
                message=f"El flujo se detuvo porque fallo {agent_label}.",
                mode=mode,
                llm_mode=llm_mode,
            )

    # Fase 2: Mandates (despues de Risk, puede leer su output via tool)
    mandates_result = run_step(
        decision_id,
        "mandates_agent",
        run_mandates_agent,
        mode=mode,
        llm_mode=llm_mode,
        model=None,
    )
    results.append(mandates_result)
    results_map["mandates_agent"] = mandates_result

    if mandates_result.get("status") != "success":
        return build_final_result(
            decision_id=decision_id,
            start_time=start_time,
            results=results,
            status="error",
            message="El flujo se detuvo porque fallo Mandates Agent.",
            mode=mode,
            llm_mode=llm_mode,
        )

    synthesis_model = os.getenv("GOOGLE_VERTEX_MODEL_SYNTHESIS") or None

    synthesis_result = run_step(
        decision_id,
        "synthesis_agent",
        run_synthesis_agent,
        mode=mode,
        llm_mode=llm_mode,
        model=synthesis_model,
    )
    results.append(synthesis_result)

    if synthesis_result.get("status") != "success":
        return build_final_result(
            decision_id=decision_id,
            start_time=start_time,
            results=results,
            status="error",
            message="El flujo se detuvo porque fallo Synthesis Agent.",
            mode=mode,
            llm_mode=llm_mode,
        )

    return build_final_result(
        decision_id=decision_id,
        start_time=start_time,
        results=results,
        status="success",
        message=f"Flujo {decision_id} ejecutado correctamente.",
        mode=mode,
        llm_mode=llm_mode,
    )


def build_final_result(decision_id, start_time, results, status, message, mode, llm_mode):
    end_time = datetime.now().isoformat(timespec="seconds")

    final_result = {
        "id_decision": decision_id,
        "workflow": "InvestCopilot multi-agent flow",
        "workflow_mode": mode,
        "llm_mode": llm_mode,
        "status": status,
        "message": message,
        "start_time": start_time,
        "end_time": end_time,
        "project_dir": str(PROJECT_DIR),
        "agents_executed": [
            result.get("agent", "unknown")
            for result in results
        ],
        "results": results,
        "final_outputs": {
            "research": {
                "llm_markdown": str(PROJECT_DIR / "02_research" / "outputs_research" / f"{decision_id}_research_llm.md"),
                "llm_json": str(PROJECT_DIR / "02_research" / "outputs_research" / f"{decision_id}_research_llm.json"),
            },
            "macro": {
                "script_markdown": str(PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro.md"),
                "script_json": str(PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro.json"),
                "llm_markdown": str(PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro_llm.md"),
                "llm_json": str(PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro_llm.json"),
            },
            "risk": {
                "script_markdown": str(PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo.md"),
                "script_json": str(PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo.json"),
                "llm_markdown": str(PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm.md"),
                "llm_json": str(PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm.json"),
            },
            "mandates": {
                "script_markdown": str(PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos.md"),
                "script_json": str(PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos.json"),
                "llm_markdown": str(PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm.md"),
                "llm_json": str(PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm.json"),
            },
            "synthesis": {
                "script_markdown": str(PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis.md"),
                "script_json": str(PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis.json"),
                "llm_markdown": str(PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm.md"),
                "llm_json": str(PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm.json"),
            },
        },
    }

    save_run_summary(decision_id, final_result)
    return final_result


def save_run_summary(decision_id, final_result):
    ORCHESTRATOR_DIR.mkdir(parents=True, exist_ok=True)

    with open(_summary_json_path(decision_id), "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2, default=str)

    md = build_markdown_summary(final_result)

    with open(_summary_md_path(decision_id), "w", encoding="utf-8") as f:
        f.write(md)


def build_markdown_summary(final_result):
    decision_id = final_result.get("id_decision", "DECISION_001")
    status = final_result.get("status")
    message = final_result.get("message")
    mode = final_result.get("workflow_mode")
    llm_mode = final_result.get("llm_mode")

    rows = []

    for result in final_result.get("results", []):
        agent = result.get("agent", "unknown")
        agent_status = result.get("status", "unknown")
        agent_mode = result.get("mode", "No disponible")
        icon = status_icon(agent_status)
        prompt_used = result.get("prompt_used", "No disponible")
        output_md = safe_get(result, "outputs", "markdown", default="No disponible")
        output_json = safe_get(result, "outputs", "json", default="No disponible")

        rows.append(
            f"| {icon} {agent} | {agent_status} | {agent_mode} | `{prompt_used}` | `{output_md}` | `{output_json}` |"
        )

    table = "\n".join(rows)

    synthesis_summary = {}

    for result in final_result.get("results", []):
        if result.get("agent") == "synthesis_agent":
            synthesis_summary = result.get("summary", {})

    clasificacion = synthesis_summary.get("clasificacion_consolidada", "No disponible")
    conclusion = synthesis_summary.get("conclusion", "No disponible")
    response_preview = synthesis_summary.get("response_preview", "No disponible")

    bt = "`" * 3

    md = f"""# Run summary - {decision_id}

## 1. Estado de ejecucion

Estado: **{status}**

Mensaje:

{message}

Modo workflow:

{bt}plaintext
{mode}
{bt}

Modo LLM:

{bt}plaintext
{llm_mode}
{bt}

Inicio:

{bt}plaintext
{final_result.get("start_time")}
{bt}

Fin:

{bt}plaintext
{final_result.get("end_time")}
{bt}

---

## 2. Agentes ejecutados

| Agente | Estado | Modo agente | Prompt usado | Output Markdown | Output JSON |
|---|---|---|---|---|---|
{table}

---

## 3. Outputs finales

### Macro

Script:

{bt}plaintext
{final_result["final_outputs"]["macro"]["script_markdown"]}
{final_result["final_outputs"]["macro"]["script_json"]}
{bt}

LLM:

{bt}plaintext
{final_result["final_outputs"]["macro"]["llm_markdown"]}
{final_result["final_outputs"]["macro"]["llm_json"]}
{bt}

### Riesgo

Script:

{bt}plaintext
{final_result["final_outputs"]["risk"]["script_markdown"]}
{final_result["final_outputs"]["risk"]["script_json"]}
{bt}

LLM:

{bt}plaintext
{final_result["final_outputs"]["risk"]["llm_markdown"]}
{final_result["final_outputs"]["risk"]["llm_json"]}
{bt}

### Mandatos / Asset Allocation

Script:

{bt}plaintext
{final_result["final_outputs"]["mandates"]["script_markdown"]}
{final_result["final_outputs"]["mandates"]["script_json"]}
{bt}

LLM:

{bt}plaintext
{final_result["final_outputs"]["mandates"]["llm_markdown"]}
{final_result["final_outputs"]["mandates"]["llm_json"]}
{bt}

### Sintesis / Comite Virtual

Script:

{bt}plaintext
{final_result["final_outputs"]["synthesis"]["script_markdown"]}
{final_result["final_outputs"]["synthesis"]["script_json"]}
{bt}

LLM:

{bt}plaintext
{final_result["final_outputs"]["synthesis"]["llm_markdown"]}
{final_result["final_outputs"]["synthesis"]["llm_json"]}
{bt}

---

## 4. Resultado consolidado

Clasificacion consolidada:

{bt}plaintext
{clasificacion}
{bt}

Conclusion:

{bt}plaintext
{conclusion}
{bt}

Preview de respuesta LLM, si aplica:

{bt}plaintext
{response_preview}
{bt}

---

## 5. Nota metodologica

Este orquestador ejecuta los agentes del prototipo para la decision_id indicada.

En modo script (solo disponible para DECISION_001, el caso de demo precalculado):

- los agentes leen sus prompts internos;
- validan inputs;
- ejecutan scripts deterministas existentes;
- generan outputs .md y .json.

En modo llm (unico modo disponible para decisiones nuevas):

- los agentes leen sus prompts internos;
- construyen contexto con archivos del proyecto y la hipotesis de la decision;
- llaman a llm_client;
- por defecto llm_mode=mock, por lo que no se llama a ningun modelo externo.

---

## 6. Mensaje clave

InvestCopilot analiza.

InvestCopilot estructura.

InvestCopilot genera una sintesis trazable.

La persona decide.
"""

    return md


# ============================================================
# EJECUCION
# ============================================================

if __name__ == "__main__":
    args = parse_args()

    final = run_decision(
        decision_id=args["decision_id"],
        mode=args["mode"],
        llm_mode=args["llm_mode"],
    )

    log(
        "INFO" if final.get("status") == "success" else "ERROR",
        "orchestrator_end",
        decision_id=args["decision_id"],
        status=final.get("status"),
        summary_json=str(_summary_json_path(args["decision_id"])),
        summary_md=str(_summary_md_path(args["decision_id"])),
    )
