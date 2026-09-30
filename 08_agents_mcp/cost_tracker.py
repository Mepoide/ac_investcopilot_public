"""
Control de costes para InvestCopilot.

Registra uso real de Gemini (Vertex AI) y Google Search API, emite alertas
via log_util y eleva CostCapExceeded cuando se alcanza el cap duro.

Persistencia: 08_agents_mcp/cost_log.json (acumulados por día UTC)

Config via .env / os.environ:
  COST_CAP_DAILY_EUR    cap duro diario en EUR (default: 5.0)
  COST_CAP_WARN_EUR     umbral de alerta, aviso pero no bloquea (default: 3.0)
  SEARCH_CAP_DAILY      cap duro de queries de búsqueda por día (default: 100)

Precios (aproximados; 1 USD ≈ 1 EUR a efectos de prototipo):
  gemini-2.5-flash: $0.075/M input · $0.30/M output
  gemini-2.5-pro:   $1.25/M input  · $10.00/M output
  Google Search:    $5.00/1000 queries = $0.005/query
                    (primeras 100/día gratis — aquí no se descuentan;
                     estimación conservadora)
"""

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

_LOG_PATH = Path(__file__).resolve().parent / "cost_log.json"
_lock = threading.Lock()

# Precios en USD/token (tratamos 1 USD ≈ 1 EUR para prototipo)
_PRICE_PER_TOKEN = {
    "flash": {"input": 0.075 / 1_000_000, "output": 0.30 / 1_000_000},
    "pro":   {"input": 1.25  / 1_000_000, "output": 10.00 / 1_000_000},
}
_SEARCH_PRICE_PER_QUERY = 0.005  # $5 / 1000 queries

try:
    from log_util import log as _log
except ImportError:
    def _log(*args, **kwargs): pass


class CostCapExceeded(Exception):
    """Se eleva cuando el coste acumulado del día supera el cap configurado."""
    pass


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load() -> dict:
    if _LOG_PATH.exists():
        try:
            return json.loads(_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save(data: dict) -> None:
    _LOG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _day_template() -> dict:
    return {
        "llm_calls": 0,
        "llm_input_tokens": 0,
        "llm_output_tokens": 0,
        "llm_cost_eur": 0.0,
        "search_queries": 0,
        "search_cost_eur": 0.0,
        "total_cost_eur": 0.0,
    }


def _price_key(model: str) -> str:
    return "pro" if "pro" in model.lower() else "flash"


def _estimate_llm_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    p = _PRICE_PER_TOKEN[_price_key(model)]
    return round(input_tokens * p["input"] + output_tokens * p["output"], 8)


def _caps() -> tuple[float, float, int]:
    cap = float(os.getenv("COST_CAP_DAILY_EUR", "5.0"))
    warn = float(os.getenv("COST_CAP_WARN_EUR", "3.0"))
    search_cap = int(os.getenv("SEARCH_CAP_DAILY", "100"))
    return cap, warn, search_cap


def check_cap(model: str = "") -> None:
    """
    Comprueba si el coste acumulado de hoy ya supera el cap duro.
    Se llama ANTES de una llamada LLM para no incurrir en el gasto.
    Eleva CostCapExceeded si el total acumulado >= COST_CAP_DAILY_EUR.
    """
    cap_eur, _, _ = _caps()
    with _lock:
        data = _load()
    today_total = data.get(_today(), {}).get("total_cost_eur", 0.0)
    if today_total >= cap_eur:
        raise CostCapExceeded(
            f"Cap diario de coste alcanzado: {today_total:.4f} EUR >= {cap_eur} EUR. "
            "Espera al día siguiente o incrementa COST_CAP_DAILY_EUR."
        )


def record_llm_call(
    model: str,
    input_tokens: int,
    output_tokens: int,
    decision_id: str = "",
) -> dict:
    """
    Registra una llamada LLM completada con tokens reales.
    Emite log WARN si se supera el umbral de alerta.
    Eleva CostCapExceeded si el nuevo total supera el cap duro.
    Devuelve {"status": "ok"|"warn", "today_eur": float, "this_call_eur": float}.
    """
    cap_eur, warn_eur, _ = _caps()
    cost = _estimate_llm_cost(model, input_tokens, output_tokens)
    today = _today()

    with _lock:
        data = _load()
        day = data.setdefault(today, _day_template())
        day["llm_calls"] += 1
        day["llm_input_tokens"] += input_tokens
        day["llm_output_tokens"] += output_tokens
        day["llm_cost_eur"] = round(day["llm_cost_eur"] + cost, 8)
        day["total_cost_eur"] = round(day["llm_cost_eur"] + day["search_cost_eur"], 8)
        _save(data)
        today_total = day["total_cost_eur"]

    if today_total >= cap_eur:
        _log("ERROR", "cost_cap_reached",
             today_eur=today_total, cap_eur=cap_eur,
             model=model, decision_id=decision_id)
        raise CostCapExceeded(
            f"Cap diario de coste alcanzado: {today_total:.4f} EUR >= {cap_eur} EUR. "
            "Espera al día siguiente o incrementa COST_CAP_DAILY_EUR."
        )

    if today_total >= warn_eur:
        _log("WARN", "cost_warning",
             today_eur=today_total, warn_eur=warn_eur, cap_eur=cap_eur,
             pct_cap=round(today_total / cap_eur * 100, 1),
             model=model, decision_id=decision_id)
        return {"status": "warn", "today_eur": today_total, "this_call_eur": cost}

    return {"status": "ok", "today_eur": today_total, "this_call_eur": cost}


def record_search_call(
    query_count: int = 1,
    decision_id: str = "",
) -> dict:
    """
    Registra llamadas a Google Search API.
    Eleva CostCapExceeded si se supera SEARCH_CAP_DAILY o COST_CAP_DAILY_EUR.
    Devuelve {"status": "ok"|"warn", "today_eur": float, "today_queries": int}.
    """
    cap_eur, warn_eur, search_cap = _caps()
    cost = round(query_count * _SEARCH_PRICE_PER_QUERY, 8)
    today = _today()

    with _lock:
        data = _load()
        day = data.setdefault(today, _day_template())
        new_queries = day["search_queries"] + query_count
        if new_queries > search_cap:
            raise CostCapExceeded(
                f"Cap diario de búsquedas alcanzado: {new_queries} queries > {search_cap}. "
                "Espera al día siguiente o incrementa SEARCH_CAP_DAILY."
            )
        day["search_queries"] = new_queries
        day["search_cost_eur"] = round(day["search_cost_eur"] + cost, 8)
        day["total_cost_eur"] = round(day["llm_cost_eur"] + day["search_cost_eur"], 8)
        _save(data)
        today_total = day["total_cost_eur"]

    if today_total >= cap_eur:
        _log("ERROR", "cost_cap_reached",
             today_eur=today_total, cap_eur=cap_eur,
             service="google_search", decision_id=decision_id)
        raise CostCapExceeded(
            f"Cap diario de coste alcanzado: {today_total:.4f} EUR >= {cap_eur} EUR."
        )

    if today_total >= warn_eur:
        _log("WARN", "cost_warning",
             today_eur=today_total, warn_eur=warn_eur, cap_eur=cap_eur,
             pct_cap=round(today_total / cap_eur * 100, 1),
             service="google_search", decision_id=decision_id)
        return {"status": "warn", "today_eur": today_total, "today_queries": new_queries}

    return {"status": "ok", "today_eur": today_total, "today_queries": new_queries}


def get_today_summary() -> dict:
    """Devuelve el resumen de costes del día UTC actual."""
    cap_eur, warn_eur, search_cap = _caps()
    today = _today()
    with _lock:
        data = _load()
    day = data.get(today, _day_template())
    total = day["total_cost_eur"]
    return {
        "date": today,
        "llm_calls": day["llm_calls"],
        "llm_input_tokens": day["llm_input_tokens"],
        "llm_output_tokens": day["llm_output_tokens"],
        "llm_cost_eur": day["llm_cost_eur"],
        "search_queries": day["search_queries"],
        "search_cost_eur": day["search_cost_eur"],
        "total_cost_eur": total,
        "cap_eur": cap_eur,
        "warn_eur": warn_eur,
        "search_cap_daily": search_cap,
        "pct_cap": round(total / cap_eur * 100, 1) if cap_eur > 0 else 0.0,
        "remaining_eur": round(max(cap_eur - total, 0.0), 4),
        "status": "cap" if total >= cap_eur else ("warn" if total >= warn_eur else "ok"),
    }
