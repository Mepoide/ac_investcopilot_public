"""
diagnostico.py — InvestCopilot health check

Comprueba de un vistazo qué funciona y qué no:
  - Autenticación con Vertex AI (gcloud / token)
  - Llamada real al LLM (gemini-2.5-flash, 1 token)
  - Imports de los 5 agentes
  - Archivos de output de una decision_id dada

Uso:
  python3 08_agents_mcp/diagnostico.py
  python3 08_agents_mcp/diagnostico.py --decision-id DEC_20260707_161548
"""

import sys
import os
import json
from pathlib import Path

AGENTS_MCP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = AGENTS_MCP_DIR.parent
sys.path.insert(0, str(AGENTS_MCP_DIR / "llm_client"))
sys.path.insert(0, str(AGENTS_MCP_DIR / "agents"))


# ── helpers ────────────────────────────────────────────────────────────────────

OK   = "✅"
FAIL = "❌"
WARN = "⚠️ "

def check(label, ok, detail=""):
    icon = OK if ok else FAIL
    line = f"  {icon}  {label}"
    if detail:
        line += f"  →  {detail}"
    print(line)
    return ok


# ── 1. env & token ─────────────────────────────────────────────────────────────

def check_auth():
    print("\n── Autenticación Vertex AI ──────────────────────────────────────")
    from llm_client import _get_google_access_token, get_llm_mode

    mode = get_llm_mode()
    check("LLM mode en .env", True, mode)

    token, err = _get_google_access_token()
    if token:
        check("Access token OK", True, f"{token[:12]}…  ({len(token)} chars)")
    else:
        check("Access token", False, err)

    project = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    check("GOOGLE_CLOUD_PROJECT", bool(project), project or "NO FIJADO")
    return bool(token) and bool(project)


# ── 2. llamada real al LLM ─────────────────────────────────────────────────────

def check_llm_call():
    print("\n── Llamada real a Vertex AI ─────────────────────────────────────")
    from llm_client import call_llm, get_llm_mode
    mode = get_llm_mode()
    if mode != "vertex_ai":
        check("LLM call", True, f"modo={mode} (no llama a Vertex)")
        return True
    try:
        r = call_llm(
            system_prompt="Di exactamente: OK",
            user_context="Test diagnóstico.",
            mode="vertex_ai",
            max_tokens=10,
        )
        ok = r.get("status") == "success"
        text = r.get("data", {}).get("response_text", r.get("message", ""))[:60]
        check("Llamada a gemini-2.5-flash", ok, text)
        return ok
    except Exception as e:
        check("Llamada a gemini-2.5-flash", False, str(e)[:80])
        return False


# ── 3. imports de agentes ──────────────────────────────────────────────────────

def check_agents():
    print("\n── Imports de agentes ───────────────────────────────────────────")
    all_ok = True
    for name in ["research_agent", "macro_agent", "risk_agent", "mandates_agent", "synthesis_agent"]:
        try:
            __import__(name)
            check(name, True)
        except Exception as e:
            check(name, False, str(e)[:80])
            all_ok = False
    return all_ok


# ── 4. archivos de output de una decision ──────────────────────────────────────

def check_decision_outputs(decision_id: str):
    print(f"\n── Outputs de {decision_id} ──────────────────────────────────────")
    checks = [
        ("decision JSON",   PROJECT_DIR / "01_decision_input" / "decisiones" / f"{decision_id}.json"
                            if decision_id != "DECISION_001"
                            else PROJECT_DIR / "01_decision_input" / "decision_actual.json"),
        ("research MD",     PROJECT_DIR / "02_research" / "outputs_research" / f"{decision_id}_research_llm.md"),
        ("research data",   PROJECT_DIR / "02_research" / "outputs_research" / f"{decision_id}_research_llm_data.json"),
        ("macro MD",        PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro_llm.md"),
        ("macro data",      PROJECT_DIR / "03_macro_houseview" / "outputs_macro" / f"{decision_id}_macro_llm_data.json"),
        ("risk MD",         PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm.md"),
        ("risk data",       PROJECT_DIR / "04_portfolio_riesgo" / "outputs_riesgo" / f"{decision_id}_riesgo_llm_data.json"),
        ("mandates MD",     PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm.md"),
        ("mandates data",   PROJECT_DIR / "05_mandatos_asset_allocation" / "outputs_mandatos" / f"{decision_id}_mandatos_llm_data.json"),
        ("synthesis MD",    PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm.md"),
        ("synthesis data",  PROJECT_DIR / "06_sintesis_comite" / f"{decision_id}_sintesis_llm_data.json"),
    ]
    for label, path in checks:
        exists = path.exists()
        size = f"{path.stat().st_size:,} bytes" if exists else "FALTA"
        # data json que existe pero pesa <50 bytes probablemente es vacío/error
        if exists and "_data.json" in str(path) and path.stat().st_size < 50:
            check(label, False, f"existe pero vacío ({path.stat().st_size} bytes)")
        else:
            check(label, exists, size)


# ── 5. tool de cálculo de riesgo ───────────────────────────────────────────────

def check_risk_tool():
    print("\n── Tool de cálculo sectorial ────────────────────────────────────")
    risk_tool_dir = PROJECT_DIR / "04_portfolio_riesgo" / "metricas"
    sys.path.insert(0, str(risk_tool_dir))
    try:
        from risk_scenario_tool import calcular_escenario_sectorial
        r = calcular_escenario_sectorial("Health Care", 1.0)
        ok = "escenario" in str(r).lower() or "vol" in str(r).lower()
        check("calcular_escenario_sectorial(Health Care, +1pp)", ok, str(r)[:80])
        return ok
    except Exception as e:
        check("calcular_escenario_sectorial", False, str(e)[:80])
        return False


# ── main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    decision_id = "DECISION_001"
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--decision-id" and i + 1 < len(sys.argv[1:]):
            decision_id = sys.argv[i + 2]

    print("=" * 60)
    print("  InvestCopilot — Diagnóstico")
    print("=" * 60)

    auth_ok   = check_auth()
    llm_ok    = check_llm_call() if auth_ok else False
    agents_ok = check_agents()
    tool_ok   = check_risk_tool()
    check_decision_outputs(decision_id)

    print("\n── Resumen ───────────────────────────────────────────────────────")
    check("Autenticación",     auth_ok)
    check("Llamada LLM real",  llm_ok)
    check("Imports agentes",   agents_ok)
    check("Tool cálculo",      tool_ok)
    print()
