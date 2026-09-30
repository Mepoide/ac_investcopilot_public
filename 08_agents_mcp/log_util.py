"""
Logging estructurado JSON para InvestCopilot.

Emite a stderr (una línea JSON por evento) para no mezclar con los outputs
de datos que van a stdout. Compatible con Cloud Logging / Stackdriver cuando
se despliega en Cloud Run (F5).

Uso:
    from log_util import log
    log("INFO", "agent_start", agent="risk_agent", decision_id="DEC_...")
    log("ERROR", "llm_failed", agent="mandates_agent", error=str(e))
"""
import json
import sys
from datetime import datetime, timezone


def log(level: str, msg: str, **fields) -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "level": level.upper(),
        "msg": msg,
        **fields,
    }
    print(json.dumps(entry, ensure_ascii=False, default=str), file=sys.stderr, flush=True)
